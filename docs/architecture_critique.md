# DASD Architecture Critique

*Note: This is the original critique of the initial DASD architecture that led to the v2.0 design revisions.*

## Critique

What the design gets right — the hybrid context strategy (fixed goal + sliding window + recursive summary) is well-reasoned, and the Hallucination Gate at least acknowledges the problem of unverified claims. The interaction modes table is a useful framing.

### Significant design flaws:

1. **The Devil's Advocate Injector misfires.** Forcing contradiction after 3 consecutive agreeable turns conflates productive convergence with agreement loops. If agents have genuinely resolved a point, injecting artificial disagreement regresses the conversation. The correct trigger should be semantic stagnation, not agreement count.
2. **Agent 1 is both player and referee.** The Hallucination Gate delegates fact-checking entirely to the Analyst, but the Analyst can also be confidently wrong — and there's no mechanism to catch it. The gatekeeper needs a gate of its own.
3. **The Cosine Similarity threshold (0.85) is naive.** Two responses can be semantically novel yet lexically similar ("the system fails because X" vs. "X causes the system to fail"). Conversely, paraphrased repetition can score below 0.85. Embedding-based similarity or perplexity delta (which is mentioned but never operationalized) would be more robust.
4. **The Moderator is a single point of failure.** It routes, evaluates, injects adversarial prompts, fires the summarizer, checks stopping conditions, and synthesizes output. This is too much state in one component. A routing failure or miscalibrated evaluator corrupts the entire loop.
5. **Phase structure and interaction modes don't compose.** The 5-phase loop (Seed → Expansion → Constraint → Synthesis → Evaluation) assumes linear progression, but Stress Test mode (A1 simulates failures, A2 proposes fixes) doesn't map onto this — the Analyst would need to initiate Phase A, not the Visionary. There's no mode-aware branching in the loop.
6. **The stopping condition "No further logical inconsistencies detected" is circular.** It relies on Agent 1 declaring itself satisfied — an agent that's been arguing for 10 turns may have motivated reasoning to stop. This should be a Moderator-side objective metric, not agent self-report.
7. **Output synthesis is an orphan.** The diagram shows a "Final Output Synthesis" node, but the spec never defines who produces it, with what prompt, or what format it takes. It's the most user-visible part of the system and gets no specification.
8. **Agent 2 always goes first.** Seeding the Visionary every time biases the framing. The Analyst is always in reactive mode, which may suppress structural critiques before the conceptual frame is even established.
