graph TD
    subgraph "Users & Tools"
        A[User] -- Mobile/Web Interaction --> B(Frontend: Streamlit Cloud);
        C[Google Colab Notebook] -- Training & Registration --> D[Hugging Face Hub (LoRA Storage)];
        C --> E[Qdrant Cloud (LoRA Registration)];
    end

    subgraph "Free-Tier Cloud Infrastructure"
        F[Gateway API (Render)];
        G[Graph Service (Render)];
        H[Router Service (Render)];
        I[GNN Service (Render)];
        J[Celery Worker (Render)];

        K[Hugging Face API];
        L[Neo4j AuraDB];
        E[Qdrant Cloud];
        D[Hugging Face Hub (LoRA Storage)];
    end

    subgraph "Data Flow: Chat/Inference"
        B -- HTTP POST /chat --> F;
        F -- Get Embedding --> K[HF Inference API];
        F -- Find Relevant LoRA --> H;
        H -- Query Vector --> E;
        F -- Graph Reasoning --> I;
        I -- Query Vector --> E;
        I -- Cypher Query --> L;
        F -- Get Context & Chat --> K;
    end

    subgraph "Data Flow: Learning/Assimilation"
        B -- HTTP POST /assimilate --> F;
        F -- Submit Task --> J;
        J -- Graph Extraction --> G;
        J -- Get Embedding --> K;
        J -- Save Vector --> E;
        J -- Save Graph --> L;
    end

    style A fill:#f9f,stroke:#333,stroke-width:4px
