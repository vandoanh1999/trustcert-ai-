# TWP-Omega-VInfinity

This project is a perpetual AI OS that uses a microservices architecture to assimilate and chat with data.

## Architecture Diagram

```mermaid
graph TD
    A[User] -->|HTTP POST /assimilate| B[Gateway API]
    B -->|Queue Task| C[Redis Broker]
    C -->|Dispatch| D[Celery Worker]
    D -->|Extract Graph| E[Graph Service]
    E -->|Write Nodes/Edges| F[Neo4j Graph DB]
    D -->|Embed Nodes| G[Batcher Proxy]
    G -->|Batch Embed| H[Embedder Service]
    D -->|Upsert Vectors| I[Qdrant Vector DB]
    D -->|Train S-LoRA| J[Trainer Service]
    J -->|Save LoRA| K[LoRA Storage Volume]

    A -->|HTTP POST /chat| B[Gateway API]
    B -->|Analyze Query| L[Router Service]
    L -->|Select LoRAs| K[LoRA Storage]
    B -->|Embed Query| G[Batcher Proxy]
    B -->|Traverse Graph| M[GNN Service]
    M -->|Get Subgraph| F[Neo4j]
    M -->|Run GCN| M
    B -->|Inference with LoRAs| N[vLLM Service]
    N -->|Load LoRAs| K[LoRA Storage]

    subgraph "CPU Services"
    E
    L
    M
    end

    subgraph "GPU Services"
    H
    J
    N
    end

    subgraph "Databases"
    F
    I
    end

    style A fill:#f9f,stroke:#333,stroke-width:4px
```

## How to Run

1.  Clone the repository.
2.  Make sure you have Docker and Docker Compose installed.
3.  Run `docker-compose up -d`.

The API will be available at `http://localhost:8000`.
