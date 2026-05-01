# HackerRank Orchestrate: Core Engine

This directory contains the entire source code for the **Multi-Domain Support Triage Agent**. The architecture is a modular, offline-first RAG pipeline built with Python, ChromaDB, and Groq.

## Quick Start Guide

### 1. Environment Setup
Ensure you have Python 3.12+ installed. We recommend using a virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install pandas rich pydantic chromadb sentence-transformers google-genai python-dotenv pyyaml
```
### 3. API Key Configuration
We use Groq for high-speed, free-tier LLM inference.

Duplicate the .env.example file and rename it to .env.

Add your Groq API key:

```bash
GROQ_API_KEY=Your_Groq_API_Key_Here
```

### 4. Run the Pipeline
To start the end-to-end pipeline, execute:

```bash
python main.py
```

### What happens when you run this?

**Idempotent Ingestion:** The script checks if the local ChromaDB exists. If not, it parses all .md files in ../data, chunks them, embeds them using `all-MiniLM-L6-v2`, and builds the vector database.

**Live Terminal UI:** The rich terminal dashboard initializes and begins processing support_issues.csv.

**Execution:** The agent reads each ticket, retrieves context, checks the semantic cache, calls the Groq LLM (if needed), and writes the final structured output to output.csv.

## Architecture & Module Breakdown
The codebase is strictly modularized to separate data ingestion, LLM orchestration, and pipeline execution.

> **main.py**

The CLI entry point. It triggers the corpus ingestion check and starts the `runner.py` pipeline.

> **config.py**

The central brain for all configurable variables, paths, and thresholds. Key settings include:

`EMBEDDING_MODEL = "all-MiniLM-L6-v2" (Local Context-Transformer)`

`LLM_MODEL = "llama-3.1-8b-instant" (via Groq)`

`CACHE_THRESHOLD = 0.25 (Distance metric for Semantic Caching)`

`RESPECT_RATE_LIMITS = True (Toggles the smart 2.5s throttling)`

### /ingestion (Data Prep)
> **loader.py:** 

Recursively walks the ../data directory, parses YAML frontmatter, and infers company domains based on folder paths.

> **chunker.py:** 

Splits markdown content into 300-word chunks with 60-word overlaps to maintain context windows.

> **embedder.py:** 

Handles the local ChromaDB persistent client and embeds the chunks.

### /agent (The AI Brain)
> **schemas.py:** 

Strictly typed Pydantic models (TriageInput, TriageOutput) that force the LLM to output valid JSON matching the exact hackathon requirements.

> **prompts.py:** 

Heavily engineered Few-Shot and `Chain-of-Thought (CoT)` system prompts.

> **safety.py:** 

A local, `zero-latency safety layer` that intercepts Prompt Injections and High-Risk keywords (fraud, stolen card, vulnerability) before they reach the internet.

> **triage.py:** 

The core orchestrator that ties `RAG retrieval`, safety checks, and the LLM together.

### /pipeline (Execution)
> **runner.py:** 

Handles pandas CSV I/O and renders the live, auto-scrolling terminal UI using the rich library. It includes `Smart Throttling`, calculating latency to dynamically apply API sleep timers only when the internet is queried.

## Advanced Enterprise Features
**Semantic Caching:** Bypasses Groq completely for `duplicate/similar` issues, dropping latency `from ~3.0s down to <0.1s` while saving API tokens.

**Graceful Fallbacks:** `try/except` blocks combined with Pydantic fallbacks ensure that 401 Invalid API Key or 413 Payload Too Large errors result in safe, structured escalations rather than system crashes.