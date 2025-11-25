from fastapi import FastAPI
from .dispatch_endpoint_v6 import router as dispatch_router_v6

app = FastAPI(
    title="Genesis Core V6 - The Sentient Forge",
    version="6.0",
    description="An AI system that learns to synthesize new, verifiable AI experts on-demand."
)

# --- V6 Endpoint ---
# This is the primary, most advanced endpoint.
app.include_router(dispatch_router_v6, prefix="/dispatch", tags=["V6 - Sentient Forge"])

# --- Legacy Endpoints (can be kept for compatibility or removed) ---
# from .merge_endpoint import router as merge_router
# app.include_router(merge_router, prefix="/merge", tags=["Legacy Tools"])

@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": "Welcome to Genesis Core V6",
        "docs_url": "/docs",
        "active_pipelines": ["V6 - Sentient Forge"]
    }
