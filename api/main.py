"""
Genesis Core V7: Main API Entrypoint
"""
from fastapi import FastAPI
from api import feedback_endpoint

app = FastAPI(
    title="Genesis Core V7 API",
    description="Endpoints for interacting with the Genesis expert ecosystem.",
    version="7.0.0"
)

# Include the router from the feedback endpoint module
app.include_router(
    feedback_endpoint.router,
    prefix="/feedback",
    tags=["Judgement Pillar"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Genesis Core V7"}
