from fastapi import FastAPI
from pydantic import BaseModel
from qdrant_client import QdrantClient
from services.common import config
from services.common.hf_client import hf_client
import asyncio

app = FastAPI(title="Cognitive Router (Real-Memory)")
qdrant = QdrantClient(url=config.QDRANT_URL, api_key=config.QDRANT_API_KEY)

class AnalyzeRequest(BaseModel):
    query: str
    user_id: str

@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    # 1. Embed query (dùng HF client)
    q_vec = await hf_client.get_embedding(req.query, model=config.EMBEDDING_MODEL_NAME)

    # 2. Tìm LoRA trong Qdrant
    hits = qdrant.search(
        collection_name="lora_registry",
        query_vector=q_vec,
        limit=5
    )

    # 3. Lọc LoRA theo user
    selected_paths = []
    for hit in hits:
        payload = hit.payload
        if payload.get("user_id") == req.user_id:
            selected_paths.append(payload["path"])

    return {"selected_loras": list(set(selected_paths))[:3]}

class TopicRequest(BaseModel):
    vector: list[float]

@app.post("/find_users_by_topic")
def find_users_by_topic(req: TopicRequest):
    # ... (giữ nguyên logic)

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
