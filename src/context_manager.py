from typing import List, Dict
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

class ContextManager:
    def __init__(self, global_goal: str):
        self.global_goal = global_goal
        self.recursive_summary = ""
        self.sliding_window: List[Dict[str, str]] = []
        self.max_window_size = 3
        
        import os
        self.summarizer_llm = ChatGroq(model_name="llama-3.1-8b-instant", groq_api_key=os.environ.get("GROQ_API_KEY_1"), temperature=0.1)
        self.summarize_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are the Summarizer. Condense the following dialogue history into a concise 'State of the Conversation'. Retain key technical points, agreements, and open disagreements. Old Summary: {old_summary}"),
            ("user", "New Dialogue to integrate: {dialogue}")
        ])
        self.summarize_chain = self.summarize_prompt | self.summarizer_llm

    def add_message(self, role: str, content: str):
        self.sliding_window.append({"role": role, "content": content})
        
        # Trigger summarizer every 4 turns (since window size is 3, if it reaches 4)
        if len(self.sliding_window) > self.max_window_size:
            self._trigger_summary()

    def _trigger_summary(self):
        # Summarize the oldest messages, keep the most recent ones
        dialogue_to_summarize = "\n".join([f"{m['role']}: {m['content']}" for m in self.sliding_window[:-2]])
        
        response = self.summarize_chain.invoke({
            "old_summary": self.recursive_summary,
            "dialogue": dialogue_to_summarize
        })
        
        self.recursive_summary = response.content
        
        # Prune the sliding window
        self.sliding_window = self.sliding_window[-2:]

    def get_context(self) -> str:
        context = f"GLOBAL GOAL:\n{self.global_goal}\n\n"
        context += f"RECURSIVE SUMMARY:\n{self.recursive_summary if self.recursive_summary else 'None yet.'}\n\n"
        context += "RECENT SLIDING WINDOW:\n"
        for m in self.sliding_window:
            context += f"{m['role']}: {m['content']}\n"
        return context
