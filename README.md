# Project Genesis - The Next Evolution (Core V3)

**Genesis Core V3 is not just a Mixture-of-Experts (MoE) system; it's a dynamic, on-the-fly Model Synthesis Engine. It intelligently understands user intent and synthesizes a new, specialized AI model from a library of expert adapters in real-time.**

Instead of routing a query to a fixed expert, Genesis forges a *new expert* perfectly tailored to the immediate task. This is the dawn of bespoke, on-demand AI.

---

## Key Concepts & Architecture

Genesis Core V3 is built on a modular, production-ready architecture designed for scalability and power.

- **The Brain (`router/`):** A true semantic router powered by a `SentenceTransformer` model. It analyzes user queries to understand their deep meaning, producing a rich semantic vector that captures the user's true intent.

- **The Heart (`synthesizer/`):** An architecture-aware synthesis engine. It takes the best expert adapter candidates (found by the Brain), loads their actual model weights (`.safetensors`), and uses advanced merging algorithms like TIES to forge a completely new, synthesized model.

- **The Library (`weightindex/`):** A high-performance, persistent vector index using Faiss and SQLite. It stores the semantic embeddings of all available expert adapters, allowing the Brain to find the perfect building blocks for the Heart in milliseconds.

- **The Interface (`api/`):** A clean, powerful FastAPI server that exposes the core functionality of Genesis through a simple REST API. It's the gateway to the synthesis engine.

- **The Foundation (`docker-compose.yml`, `Makefile`, `setup.sh`):** A professional toolkit for developers. With just two commands, anyone can set up the required demo adapters, launch the full application stack, and start interacting with the API.

![Architecture Diagram Placeholder](https://via.placeholder.com/800x400.png?text=Genesis+Core+V3+Architecture)

---

## Quick Start

Getting started with Genesis is incredibly simple.

### 1. Initial Setup

First, run the setup script. This will create the necessary dummy adapters and populate the `WeightIndex`.

```bash
bash setup.sh
```

### 2. Run the Engine

Launch the entire application using Docker Compose for a consistent, isolated environment.

```bash
docker-compose up --build
```

The API server will be available at `http://localhost:8000`.

---

## Try It Now

Once the server is running, you can interact with the synthesis engine. Here’s how to ask Genesis to forge a model specialized for writing Python code:

```bash
curl -X POST "http://localhost:8000/dispatch/" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Write a Python function to calculate fibonacci sequence.",
       "topk": 2
     }'
```

You'll receive a JSON response detailing the expert adapters that were chosen as candidates and a preview of the newly synthesized model's architecture.

Welcome to the next evolution of AI. Welcome to Genesis.
