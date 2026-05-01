# HackerRank Orchestrate: Multi-Domain Support Triage Agent

**An Enterprise-Grade, Offline-First AI Support Orchestrator built for the HackerRank Orchestrate Hackathon (May 2026).**

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![Groq](https://img.shields.io/badge/LLM-Groq%20(Llama%203.1)-orange.svg)
![ChromaDB](https://img.shields.io/badge/VectorDB-Chroma-green.svg)
![Pydantic](https://img.shields.io/badge/Validation-Pydantic-red.svg)

## What is this Agent Doing?
Customer support centers are drowning in redundant queries, unstructured data, and high-risk security escalations. 

We built a **Multi-Domain Support Triage Agent** that acts as the first line of defense for HackerRank, Claude, and Visa support tickets. The agent reads raw, unstructured user issues, dynamically identifies the product domain, retrieves ground-truth documentation using Local RAG (Retrieval-Augmented Generation), and makes a deterministic decision: **draft a grounded reply** or **escalate to a human agent**.

All outputs are strictly validated into perfect JSON schemas, ready for downstream API consumption.

---

## The MVP (Minimum Viable Product)
Our submission successfully processes a batch of raw CSV support tickets and outputs a highly structured response matrix. The MVP features:
*   **Automated Ingestion:** Dynamically parses 700+ Markdown files across three product domains into a local ChromaDB vector store.
*   **Multi-Domain Routing:** Automatically infers the correct company (HackerRank, Claude, Visa) based on user intent and metadata voting.
*   **Live Command Center:** A beautiful, real-time terminal UI built with `rich` that visualizes the pipeline's decision-making process.
*   **100% Schema Adherence:** Zero hallucinatory formats; every output strictly obeys the `status`, `product_area`, `response`, `justification`, and `request_type` contract.

---

## Our USP (Unique Selling Proposition)
Most hackathon projects are simple wrappers around an LLM API. We built a production-ready system optimized for speed, cost, and safety.

1.  **Zero-Latency Semantic Caching**
    *   *The Problem:* Calling an LLM for every "I forgot my password" ticket is expensive and slow.
    *   *The Solution:* We implemented a local `sentence-transformers` semantic cache. If a new ticket has a semantic distance of `< 0.25` to a previously solved ticket, the agent bypasses the internet and LLM entirely, serving the cached resolution in **~0.05 seconds**.
2.  **Pre-Flight Safety Layer**
    *   *The Problem:* Prompt injections and critical security threats (e.g., stolen credit cards) waste expensive LLM tokens to evaluate.
    *   *The Solution:* A localized, zero-latency keyword quarantine catches threats *before* the LLM is invoked, forcing an immediate, deterministic human escalation.
3.  **Smart Throttling**
    *   Our engine dynamically calculates processing latency to respect free-tier API rate limits only when necessary, bypassing sleep timers on cache hits to maximize throughput.

---

## Error Handling
Enterprise systems cannot afford to crash. Our pipeline features **Graceful Degradation**:
*   **LLM Outages / Broken API Keys:** Caught instantly via Pydantic fallbacks. Instead of throwing Python tracebacks, the system outputs a clean `escalated` status with a `system_error` flag to alert the engineering team.
*   **RAG Misses:** If the vector database returns insufficient context, the System Prompt is engineered to strictly forbid hallucination, defaulting to a safe human escalation.
*   **Payload Management:** Context chunks are strictly limited to top-K parameters to prevent HTTP 413 (Payload Too Large) crashes.

---

## Architectural Flexibility
The codebase is designed using SOLID principles, making it highly adaptable for future enterprise integration:
*   **Drop-In Knowledge:** Adding a new company (e.g., Stripe) is as simple as dropping a new folder of markdown files into the `/data` directory. The ingestion engine handles the rest.
*   **Model Agnostic:** Swapping from Groq (Llama 3) to OpenAI (GPT-4o) or Google Gemini requires changing only three lines in `config.py` and `triage.py`. 
*   **Pluggable UI:** Because the core `triage()` function returns a clean Pydantic object, the terminal UI can be instantly swapped for a FastAPI or Flask backend to serve a web frontend.

---

## Future Scope
If given more time and resources, the next iterations of this orchestration engine would include:
1.  **Multi-Agent Workflows:** Implementing a distinct "Routing Agent" that hands off complex queries to specialized "Domain Agents" using frameworks like LangChain or AutoGen.
2.  **CRM Integration:** Replacing the CSV I/O with live Webhooks directly to Zendesk, Salesforce, or Intercom.
3.  **Cloud Vector Scaling:** Migrating the local ChromaDB to a managed cloud vector database (like Pinecone or Weaviate) for cross-container scalability.
4.  **Automated Feedback Loops:** Allowing human agents to click "Thumbs Down" on a drafted reply, automatically updating the Semantic Cache to prevent the system from repeating the mistake.

---

## How to Run the Code
For detailed technical instructions, environment setup, and execution commands, please see the **[Developer Manual inside the `/code` directory](./code/README.md)**.