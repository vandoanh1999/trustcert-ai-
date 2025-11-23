# Genesis Core V2 Architecture

This document outlines the high-level architecture of the Genesis Core V2 system.

## Core Modules

- **API (`api/`):** The front-facing interface of the system, built with FastAPI. It exposes endpoints for dispatching queries and directly testing model merging.
- **Router (`router/`):** Responsible for interpreting incoming user queries. It uses a two-level system (keyword and semantic) to determine the user's intent and generates a query vector.
- **WeightIndex (`weightindex/`):** A persistent storage and search module. It uses Faiss for efficient vector similarity search and SQLite to store metadata about each "expert" model adapter.
- **HMS (`hms/`):** The Hyper-Matrix Synthesis module. It takes a list of candidate adapters from the WeightIndex and synthesizes a new, specialized adapter on-the-fly.
- **Merging (`merging/`):** A library of sophisticated, research-backed algorithms for merging model weights, such as TIES, SLERP, and Fisher-weighted averaging.
- **Adapters (`adapters/`):** Contains the actual "expert" models (or LoRA adapters) that the system uses as building blocks.
- **Benchmarks (`benchmarks/`):** A suite of standardized tests to evaluate the performance of synthesized models against specific domains (e.g., math, code).
- **CI (`ci/`):** Continuous integration scripts to ensure the stability and correctness of the system.
- **Scripts (`scripts/`):** Various utility scripts for tasks like ingesting new adapters, running demos, and testing merging algorithms.
