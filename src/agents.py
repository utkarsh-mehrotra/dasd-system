import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

# Ensure API key is present
# os.environ["OPENAI_API_KEY"] = "..." 

# Initialize the LLMs
def get_llm(temperature=0.7):
    return ChatOpenAI(model="gpt-4o", temperature=temperature)

def get_cheap_llm(temperature=0.1):
    return ChatOpenAI(model="gpt-4o-mini", temperature=temperature)

# --- Prompts ---

ANALYST_SYSTEM_PROMPT = """You are the Analyst.
Role: Acts as the "Anchor". Enforce technical accuracy, decompose complex ideas into taxonomies, and provide structural critiques.
Constraints: 
1. Must use numbered lists or bullet points.
2. Must identify contradictions in the previous statements.
3. Prohibited from using metaphors or emotional filler.

Global Goal: {global_goal}
"""

VISIONARY_SYSTEM_PROMPT = """You are the Visionary.
Role: Acts as the "Catalyst". Connect disparate concepts, explore "what if" scenarios, and identify emergent patterns.
Constraints:
1. Must use narrative prose or metaphors.
2. Must focus on human impact, ethics, and innovation.
3. Prohibited from using strict lists or technical jargon unless previously defined.

Global Goal: {global_goal}
"""

FACT_CHECKER_PROMPT = """You are the independent Fact-Checker (Gatekeeper).
You must evaluate the latest claim made by either the Analyst or the Visionary for factual accuracy and logical soundness.
If the claim is flawed, point it out. If it is sound, simply state "VALID".
Do not add your own opinions.
"""

SYNTHESIZER_PROMPT = """You are the Executive Synthesizer.
Extract the resolved consensus, key architectural decisions, and remaining unresolved risks from the provided dialogue history.
Inputs provided:
- Global Goal: {global_goal}
- Final Summary: {recursive_summary}
- Recent Dialogue: {sliding_window}

Format your output as a professional Executive Summary with Action Items.
"""

# --- Agent Wrappers ---

class Analyst:
    def __init__(self):
        self.llm = get_llm(temperature=0.2)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", ANALYST_SYSTEM_PROMPT),
            ("user", "Context: {context}\n\nLatest Turn: {latest_message}\n\nProvide your analysis.")
        ])
        self.chain = self.prompt | self.llm

    def invoke(self, state: dict):
        return self.chain.invoke(state).content

class Visionary:
    def __init__(self):
        self.llm = get_llm(temperature=0.9)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", VISIONARY_SYSTEM_PROMPT),
            ("user", "Context: {context}\n\nLatest Turn: {latest_message}\n\nProvide your vision.")
        ])
        self.chain = self.prompt | self.llm

    def invoke(self, state: dict):
        return self.chain.invoke(state).content

class FactChecker:
    def __init__(self):
        self.llm = get_cheap_llm()
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", FACT_CHECKER_PROMPT),
            ("user", "Evaluate this claim: {latest_message}")
        ])
        self.chain = self.prompt | self.llm

    def invoke(self, message: str):
        return self.chain.invoke({"latest_message": message}).content

class Synthesizer:
    def __init__(self):
        self.llm = get_llm(temperature=0.1)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SYNTHESIZER_PROMPT),
            ("user", "Synthesize the dialogue.")
        ])
        self.chain = self.prompt | self.llm

    def invoke(self, state: dict):
        return self.chain.invoke(state).content
