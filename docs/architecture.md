# Dual-Agent Synthetic Dialogue System (DASD)
## Architectural Design Document (v2.0)

This design balances the precision of an analytical model with the lateral thinking of an intuitive model. The goal is to move beyond simple "chat" into a recursive, mode-aware synthesis of ideas, driven by a distributed control plane.

### 1. Agent Personas & Behavioral Constraints

**Agent 1: The Analyst (Logical/Structured)**
*   **Role:** Acts as the "Anchor." Enforces technical accuracy, decomposes complex ideas into taxonomies, and provides structural critiques.
*   **Constraints:** Must use numbered lists or bullet points; must identify contradictions; prohibited from using metaphors or emotional filler.

**Agent 2: The Visionary (Intuitive/Expressive)**
*   **Role:** Acts as the "Catalyst." Connects disparate concepts, explores "what if" scenarios, and identifies emergent patterns.
*   **Constraints:** Must use narrative prose or metaphors; must focus on human impact/ethics/innovation; prohibited from using strict lists or technical jargon unless previously defined.

---

### 2. Distributed Control Plane
To prevent a single point of failure and separate concerns, the monolithic "Moderator" is decomposed into four distinct services:

1.  **Router:** Handles turn-taking and mode-aware branching. Decides which agent speaks next based on the active Interaction Mode.
2.  **Evaluator:** Continuously computes objective metrics (e.g., perplexity delta, embedding similarity) to monitor conversation health and trigger stopping conditions.
3.  **Fact-Checker (The Gatekeeper):** An independent verification node (LLM or deterministic tool integration) that audits claims made by *both* Agent 1 and Agent 2, removing the conflict of interest of Agent 1 being both player and referee.
4.  **Summarizer:** Middleware that condenses context to prevent token bloating.

---

### 3. Mode-Aware Conversation Loop & Turn Management
The loop structure is dynamically determined by the **Interaction Mode**, ensuring proper framing and avoiding the bias of the Visionary always speaking first.

**Interaction Modes & Branching:**

| Mode | Objective | Seeding Agent (Phase A) | Dynamics |
| :--- | :--- | :--- | :--- |
| **Socratic Debate** | Uncover flaws in a premise. | Agent 2 (Visionary) | A2 proposes a premise; A1 systematically deconstructs it; A2 defends/refines. |
| **Blue-Sky Design** | Rapid prototyping of ideas. | Agent 2 (Visionary) | A2 ideates broadly; A1 converts ideas into concrete requirements. |
| **Stress Test** | Identifying edge cases. | Agent 1 (Analyst) | A1 seeds the loop with simulated system failures; A2 proposes adaptive solutions. |

**Generalized Phase Structure:**
*   **Phase A (Seed):** Router injects the prompt into the designated Seeding Agent.
*   **Phase B (Response):** Seeding Agent generates the initial frame.
*   **Phase C (Fact-Check):** The independent Fact-Checker verifies the response.
*   **Phase D (Counter-Response):** The responding agent critiques or expands based on the mode.
*   **Phase E (Evaluation):** Evaluator calculates semantic gain. Router loops back to Phase C or triggers stopping conditions.

---

### 4. Context Management Strategy
To prevent token bloating while maintaining coherence, we utilize a **Hybrid Segmented Context**:

*   **Fixed Global Goal:** A static system prompt containing the original task, always present in the header of every turn.
*   **Sliding Window (Local):** The last 3 turns of dialogue are provided in full for immediate coherence.
*   **Recursive Summary (Middleware):** Every 4 turns, the Summarizer condenses the previous history into a "State of the Conversation" block that replaces the older turns in the sliding window.

---

### 5. Control Mechanisms & Failure Prevention

*   **Semantic Stagnation Injector:** Replacing the naive "Devil's Advocate," this triggers when the Evaluator detects low conceptual gain (perplexity delta drops below a threshold). It forces the Router to inject a "Pivot Prompt" (e.g., "Address this from a completely orthogonal perspective") to break the stagnation.
*   **Redundancy Filter:** Uses embedding-based similarity (e.g., text-embedding-ada-002) and perplexity delta rather than lexical cosine similarity. Responses with high embedding similarity to recent turns are rejected and regenerated with higher temperature.
*   **Independent Fact-Checking:** Technical claims from *either* agent are routed through the Fact-Checker node before being added to the context window, preventing confidently incorrect assertions from compounding.

---

### 6. Output Quality & Stopping Conditions
Stopping conditions are entirely handled by the **Evaluator** using objective metrics, removing circular self-reporting.

A "Good" Conversation must:
*   Move from abstract to concrete (convergence).
*   Maintain a Perplexity Delta (new information introduced in each turn).

**Stopping Conditions:**
*   **Semantic Convergence:** If the last two summaries show less than 5% new conceptual gain (measured via embedding distance), the conversation has naturally resolved.
*   **Target State Reached:** The Evaluator matches the current Recursive Summary against the Fixed Global Goal and determines the criteria are met.
*   **Hard Cap:** Fallback limit of 10–12 turns to prevent infinite drift.

---

### 7. Final Output Synthesis
Once a stopping condition is met, the workflow routes to a dedicated **Synthesizer Node**.

*   **Who Produces It:** A distinct LLM call decoupled from the personas of Agent 1 and Agent 2.
*   **Inputs:** The final Recursive Summary + the final Sliding Window + the Fixed Global Goal.
*   **Prompt Instruction:** "You are an executive synthesizer. Extract the resolved consensus, key architectural decisions, and remaining unresolved risks from the provided dialogue history."
*   **Format:** Outputs a structured artifact (e.g., Executive Summary, Action Items, and Technical Specifications) rather than a raw chat transcript.

---

### 8. High-Level Architecture Diagram

```plaintext
[ USER INPUT / SEED ]
         |
         v
+---------------------------------------------------+
|               DISTRIBUTED CONTROL PLANE           |
|                                                   |
|  +--------+    +-----------+    +--------------+  |
|  | Router |<-->| Evaluator |<-->| Summarizer   |  |
|  +---+----+    +-----------+    +-------+------+  |
+------|----------------------------------|---------+
       |   (Mode-Aware Branching)         |
       |                                  v
       |                      +-------------------------+
       |                      | CONTEXT SUMMARY BUFFER  |
       |                      | (Sliding Window/Memory) |
       v                      +-------------------------+
+-------------+                           ^
| [ AGENT 1 ] |                           |
|  (Analyst)  |                           |
+------+------+                           |
       |                                  |
       +--------> [ FACT-CHECKER ] <------+
       |          (Verification)          |
+------+------+                           |
| [ AGENT 2 ] |                           |
| (Visionary) |                           |
+-------------+                           |
       |                                  |
       +----------------------------------+
               (Evaluation Loop Back)
                        |
                        v
               +-----------------+
               | STOP CONDITIONS |
               +--------+--------+
                        | (Trigger Synthesis)
                        v
             +--------------------+
             | SYNTHESIZER NODE   |
             | (Final Formatting) |
             +--------+-----------+
                      |
                      v
             [ FINAL OUTPUT ARTIFACT ]
```
