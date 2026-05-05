# Dual-Agent Synthetic Dialogue System (DASD)

This repository implements the DASD architecture, a multi-agent system designed to move beyond simple chat interfaces into a recursive, mode-aware synthesis of ideas. 

The system leverages an Analyst agent (logical/structured), a Visionary agent (intuitive/expressive), and a distributed Control Plane (Router, Evaluator, Fact-Checker, and Summarizer) built with LangGraph to orchestrate complex reasoning loops.

## Structure
- `/src`: The core LangGraph orchestration, agent definitions, evaluator metrics, and context manager.
- `/docs`: Architectural designs and requirements documentation.
- `/infra`: Dockerfile and infrastructure configurations.

## Architecture
See `/docs/architecture.md` for a complete breakdown of the Control Plane, Interaction Modes, and objective stopping conditions (Perplexity Delta, Semantic Stagnation).
