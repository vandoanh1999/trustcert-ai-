"""
Genesis Core V8: Main API Entrypoint (Hardened & Refactored)

This version includes rate-limiting and uses the centralized config.
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import time
from collections import defaultdict

from api import feedback_endpoint, dispatch_endpoint
from core.config import *

app = FastAPI(
    title="Genesis Core V8 API",
    description="Endpoints for interacting with the Genesis expert ecosystem.",
    version="8.0.0"
)

# --- V8 Security Hardening: Rate Limiting ---
request_counts = defaultdict(lambda: [])

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()

    request_timestamps = [t for t in request_counts[client_ip] if t > current_time - API_REQUEST_WINDOW_SECONDS]

    if len(request_timestamps) >= API_MAX_REQUESTS_PER_WINDOW:
        return JSONResponse(status_code=429, content={"detail": "Too Many Requests"})

    request_counts[client_ip] = request_timestamps + [current_time]

    response = await call_next(request)
    return response

# --- Core Endpoints ---
app.include_router(dispatch_endpoint.router, prefix="/dispatch", tags=["V8 - Inference"])
app.include_router(feedback_endpoint.router, prefix="/feedback", tags=["V8 - Judgement Pillar"])

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Genesis Core V8",
        "docs_url": "/docs"
    }
