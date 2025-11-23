Genesis Core V2 — Developer Guide
=================================

1. Install dependencies:
    pip install fastapi uvicorn numpy faiss-cpu

2. Create adapter_demo.npz files:
    (See adapters/README.md)

3. Ingest adapters:
    python scripts/ingest_adapters.py

4. Run demo pipeline:
    python scripts/run_demo.py

5. Start API server:
    uvicorn api.server:app --host 0.0.0.0 --port 8000
