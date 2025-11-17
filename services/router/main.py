# services/router/main.py
from fastapi import FastAPI
import httpx
from pydantic import BaseModel
from qdrant_client import QdrantClient

app = FastAPI(title="Cognitive Router (Real-Memory)")
client = httpx.Client()
qdrant = QdrantClient("http://qdrant:6333")

class AnalyzeRequest(BaseModel):
    query: str
    user_id: str

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    # 1. Embed query (như V12)
    q_vec_resp = client.post("http://embedder:8002/embed", json={"texts": [req.query]})
    q_vec = q_vec_resp.json()[0]

    # 2. TÌM LORA TRONG SỔ ĐĂNG KÝ (QDRANT)
    # Tìm các LoRA liên quan nhất đến query
    hits = qdrant.search(
        collection_name="lora_registry",
        query_vector=q_vec,
        limit=5 # Lấy 5 LoRA liên quan nhất
    )

    # 3. LỌC: Chỉ lấy LoRA của user này
    selected_paths = []
    for hit in hits:
        payload = hit.payload
        # Rất quan trọng: Chỉ load LoRA của đúng user đó
        if payload.get("user_id") == req.user_id:
            selected_paths.append(payload["path"])

    # Đảm bảo LoRA chung (nếu có) cũng được thêm vào
    # (Ví dụ: lora_user_id_general.safetensors)

    # Lấy 3 cái tốt nhất
    return {"selected_loras": list(set(selected_paths))[:3]}

class TopicRequest(BaseModel):
    vector: list[float]

@app.post("/find_users_by_topic")
def find_users_by_topic(req: TopicRequest):
    hits = qdrant.search(
        collection_name="lora_registry",
        query_vector=req.vector,
        limit=5
    )

    user_ids = {hit.payload.get("user_id") for hit in hits if hit.payload.get("user_id")}
    return {"user_ids": list(user_ids)}
