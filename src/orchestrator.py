from typing import TypedDict, Annotated, Sequence
import operator
from langgraph.graph import StateGraph, END
from src.agents import Analyst, Visionary, FactChecker, Synthesizer
from src.evaluator import Evaluator
from src.context_manager import ContextManager

# Define the State for LangGraph
class AgentState(TypedDict):
    mode: str
    global_goal: str
    context: str
    latest_message: str
    sender: str
    turn_count: int
    history: Annotated[Sequence[str], operator.add]

class DASDOrchestrator:
    def __init__(self, global_goal: str, mode: str = "socratic"):
        self.global_goal = global_goal
        self.mode = mode
        
        self.analyst = Analyst()
        self.visionary = Visionary()
        self.fact_checker = FactChecker()
        self.synthesizer = Synthesizer()
        
        self.evaluator = Evaluator()
        self.context_manager = ContextManager(global_goal)
        
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)
        
        workflow.add_node("router_node", self.router_node)
        workflow.add_node("analyst_node", self.analyst_node)
        workflow.add_node("visionary_node", self.visionary_node)
        workflow.add_node("fact_check_node", self.fact_check_node)
        workflow.add_node("evaluator_node", self.evaluator_node)
        workflow.add_node("synthesizer_node", self.synthesizer_node)

        # Mode-Aware Branching (Phase A: Seed)
        if self.mode == "stress_test":
            workflow.set_entry_point("analyst_node")
        else: # socratic or blue_sky
            workflow.set_entry_point("visionary_node")

        # After generating a message, route to Fact Checker
        workflow.add_edge("analyst_node", "fact_check_node")
        workflow.add_edge("visionary_node", "fact_check_node")
        
        # After Fact Checking, route to Evaluator
        workflow.add_edge("fact_check_node", "evaluator_node")
        
        # Evaluator decides: Router or Synthesis
        workflow.add_conditional_edges(
            "evaluator_node",
            self.should_continue,
            {
                "continue": "router_node",
                "stop": "synthesizer_node"
            }
        )
        
        # Router decides who speaks next based on previous sender
        workflow.add_conditional_edges(
            "router_node",
            lambda state: "analyst_node" if state["sender"] == "visionary" else "visionary_node"
        )
        
        workflow.add_edge("synthesizer_node", END)
        
        return workflow.compile()

    # --- Node Implementations ---
    
    def analyst_node(self, state: AgentState):
        ctx = self.context_manager.get_context()
        response = self.analyst.invoke({"context": ctx, "latest_message": state["latest_message"], "global_goal": state["global_goal"]})
        return {"latest_message": response, "sender": "analyst", "turn_count": state["turn_count"] + 1, "history": [response]}

    def visionary_node(self, state: AgentState):
        ctx = self.context_manager.get_context()
        response = self.visionary.invoke({"context": ctx, "latest_message": state["latest_message"], "global_goal": state["global_goal"]})
        return {"latest_message": response, "sender": "visionary", "turn_count": state["turn_count"] + 1, "history": [response]}
        
    def fact_check_node(self, state: AgentState):
        # Fact-checker intercepts the message before adding to context
        validation = self.fact_checker.invoke(state["latest_message"])
        if "VALID" not in validation.upper():
            # If invalid, append the correction
            state["latest_message"] += f"\n\n[GATEKEEPER CORRECTION: {validation}]"
        
        # Add to actual sliding window now that it's checked
        self.context_manager.add_message(state["sender"], state["latest_message"])
        return state
        
    def evaluator_node(self, state: AgentState):
        # Check for semantic stagnation
        if state["turn_count"] > 3:
            if self.evaluator.is_stagnating(state["latest_message"], state["history"][:-1]):
                print("--- Semantic Stagnation Detected! Injecting Pivot ---")
                state["latest_message"] += "\n[EVALUATOR PIVOT: Address this from a completely orthogonal perspective. Do not repeat previous points.]"
        return state

    def router_node(self, state: AgentState):
        # Purely pass-through node for conditional routing
        return state

    def synthesizer_node(self, state: AgentState):
        response = self.synthesizer.invoke({
            "global_goal": state["global_goal"],
            "recursive_summary": self.context_manager.recursive_summary,
            "sliding_window": "\n".join([f"{m['role']}: {m['content']}" for m in self.context_manager.sliding_window])
        })
        return {"latest_message": response, "sender": "synthesizer"}

    def should_continue(self, state: AgentState):
        if state["turn_count"] >= 10:
            return "stop"
        return "continue"

if __name__ == "__main__":
    goal = "Design a scalable event-driven architecture for a global fintech application handling 1M RPS."
    print("Initializing DASD Orchestrator...")
    orchestrator = DASDOrchestrator(global_goal=goal, mode="socratic")
    
    initial_state = {
        "mode": "socratic",
        "global_goal": goal,
        "context": "",
        "latest_message": "Let's begin.",
        "sender": "system",
        "turn_count": 0,
        "history": []
    }
    
    print("Starting loop (Make sure OPENAI_API_KEY is set in environment)...\n")
    # For local execution, uncomment the following line once API keys are present.
    # final_state = orchestrator.graph.invoke(initial_state)
    # print("\n=== FINAL SYNTHESIS ===")
    # print(final_state["latest_message"])
