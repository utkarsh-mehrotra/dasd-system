# DASD Implementation Requirements

To bring the Dual-Agent Synthetic Dialogue System (DASD) from an architectural design to a functional system, you will need a mix of custom code orchestration and specific infrastructure components. Here is the breakdown:

## 1. Software & Code Requirements

### Core Orchestration (The Router)
*   **State Machine / Graph Framework:** You need a way to manage the non-linear conversation loop and mode-aware branching. Instead of writing custom while-loops, use an agentic orchestrator framework:
    *   *Recommended:* **LangGraph** (Python/JS) or **Temporal.io**. These treat the multi-agent loop as a state graph, making it easy to pause, route between agents, and track context.
*   **Persona Instantiation Code:** System prompt templates and LLM client wrappers specifically configured for the Analyst, Visionary, and Synthesizer.

### The Evaluator & Memory
*   **Embedding Generator:** Code to convert the text of recent turns into vector embeddings to measure "Semantic Stagnation" and "Redundancy". 
    *   *Need:* API calls to an embedding model (e.g., OpenAI `text-embedding-3-small` or local HuggingFace sentence-transformers).
*   **Distance Calculation:** Simple utility functions to compute cosine similarity/distance between the current turn's embedding and the sliding window history.
*   **Context Buffer Management:** Logic to manage the Sliding Window (e.g., keeping only the last N messages) and trigger the Summarizer LLM call every 4 turns.

### The Fact-Checker (Gatekeeper)
*   **Tool Integrations:** If the Fact-Checker verifies claims against real-world data, you need API clients for search (e.g., SerpApi, Tavily) or access to an internal RAG knowledge base.
*   **Evaluation Prompting:** A strict, deterministic LLM prompt chain designed to return binary (Valid/Invalid) or corrective JSON outputs based on the agents' claims.

---

## 2. Infrastructure Requirements

### Compute & Hosting
*   **Backend Server:** A persistent backend to run the orchestration graph. Since the conversation loop may take 30-60 seconds (across 10-12 LLM calls), serverless functions (like standard AWS Lambda or Vercel functions) might time out. 
    *   *Recommended:* A containerized service like **AWS ECS/Fargate**, **Render Background Workers**, or **Google Cloud Run** (with extended timeouts).
*   **WebSockets (If User-Facing):** If a user needs to watch the agents debate in real-time, you'll need a WebSocket server (e.g., FastAPI + WebSockets, or Socket.io) to stream intermediate Agent 1/Agent 2 tokens back to a frontend.

### Managed Services & APIs
*   **Primary LLM Inference:** Access to high-tier models for the complex reasoning nodes (Visionary, Analyst, Fact-Checker).
*   **Secondary/Utility LLM Inference:** Cheaper, faster models (e.g., GPT-4o-mini or Claude 3.5 Haiku) for the repetitive background tasks (Summarizer, Evaluator).
*   **Vector DB / In-Memory Store:** If conversations get long and you need to compare embeddings across the entire history for redundancy, an in-memory store like **FAISS** or a lightweight vector DB like **ChromaDB** is needed.

### Data Persistence
*   **State Store:** To save the "State of the Conversation" and final synthesized artifacts. A NoSQL DB (MongoDB/DynamoDB) or Postgres (with pgvector if storing embeddings) is sufficient.

---

## 3. Recommended Tech Stack

| Component | Technology |
| :--- | :--- |
| **Language** | Python (Best ecosystem for AI/Graphs) or TypeScript |
| **Orchestration** | LangGraph or AutoGen |
| **LLM Provider** | Anthropic (Claude 3.5 Sonnet for reasoning) / OpenAI |
| **Embeddings** | OpenAI `text-embedding-3-small` |
| **Compute** | Dockerized FastAPI app on Render/AWS Fargate |
| **Storage** | PostgreSQL (Supabase) + pgvector |
