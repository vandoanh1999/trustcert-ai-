"""
Genesis Core V7: Main API Entrypoint
"""
from fastapi import FastAPI
from api import feedback_endpoint, dispatch_endpoint

app = FastAPI(
    title="Genesis Core V7 API",
    description="Endpoints for interacting with the Genesis expert ecosystem.",
    version="7.0.0"
)

# --- V7 Core Endpoints ---

# The primary endpoint for querying the expert network
app.include_router(
    dispatch_endpoint.router,
    prefix="/dispatch",
    tags=["V7 - Inference"],
)

# The endpoint for submitting feedback on a dispatch
app.include_router(
    feedback_endpoint.router,
    prefix="/feedback",
    tags=["V7 - Judgement Pillar"],
)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Genesis Core V7",
        "docs_url": "/docs",
        "active_pipelines": ["V7 - Inference", "V7 - Judgement Pillar"]
    }
