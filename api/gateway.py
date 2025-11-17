from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
import httpx
from qdrant_client import QdrantClient, models
from tasks import assimilate_task
import logging
import redis
import json
from services.common import config
from services.common.hf_client import hf_client

# ... (Logging, Auth) ...

app = FastAPI(title="TWP-Ω V-Infinity – Serverless Edition")
client = httpx.AsyncClient(timeout=30.0)
qdrant = QdrantClient(url=config.QDRANT_URL, api_key=config.QDRANT_API_KEY)
redis_client = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=0, decode_responses=True)

# --- Logic Trí nhớ Dài hạn ---
CHAT_HISTORY_KEY_PREFIX = "chat_history:"
MAX_HISTORY_LENGTH = 10 # Giới hạn 5 cặp hỏi-đáp

def get_chat_history(user_id: str) -> list:
    """Lấy lịch sử trò chuyện từ Redis."""
    history_json = redis_client.lrange(f"{CHAT_HISTORY_KEY_PREFIX}{user_id}", 0, -1)
    return [json.loads(item) for item in history_json]

def add_to_chat_history(user_id: str, user_message: str, assistant_message: str):
    """Thêm cặp hỏi-đáp mới vào lịch sử và cắt bớt nếu cần."""
    key = f"{CHAT_HISTORY_KEY_PREFIX}{user_id}"
    redis_client.lpush(key, json.dumps({"role": "user", "content": user_message}))
    redis_client.lpush(key, json.dumps({"role": "assistant", "content": assistant_message}))
    # Giữ lịch sử ở độ dài tối đa
    redis_client.ltrim(key, 0, MAX_HISTORY_LENGTH - 1)

def format_history_for_prompt(history: list) -> str:
    """Định dạng lịch sử thành một chuỗi cho prompt."""
    if not history:
        return ""
    # Đảo ngược lịch sử vì Redis lpush thêm vào đầu
    history.reverse()
    formatted_history = "\\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
    return f"Previous conversation history:\\n{formatted_history}\\n\\n"


@app.post("/v_infinity/chat")
async def chat(query: str, user_id: str, api_key: str = Security(get_api_key)):
    logger.info(f"Received chat request from user '{user_id}'")

    # 1. Lấy và định dạng lịch sử trò chuyện
    history = get_chat_history(user_id)
    history_prompt = format_history_for_prompt(history)

    # 2. Embed query & Suy luận đồ thị
    q_vec = await hf_client.get_embedding(query, model=config.EMBEDDING_MODEL_NAME)
    gnn_payload = {"entry_vector": q_vec}
    # Giả sử gnn-service được triển khai
    gnn_resp = await client.post("http://gnn-service:8006/traverse", json=gnn_payload)
    context = gnn_resp.json().get("context_path", "No context found.")

    # 3. Tạo prompt hoàn chỉnh
    prompt = f"{history_prompt}Current conversation:\nContext from knowledge graph: {context}\nUser: {query}\nAssistant:"

    # 4. Chat Completion
    answer = await hf_client.chat_completion(prompt, model=config.BASE_MODEL_NAME)

    # 5. Cập nhật lịch sử
    add_to_chat_history(user_id, query, answer)

    return {"answer": answer, "loras_used": 0}

# ... (các endpoint khác)
