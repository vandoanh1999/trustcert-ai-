from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
import httpx
from qdrant_client import QdrantClient, models
from tasks import assimilate_task
import logging
import os
import boto3
from pathlib import Path

# --- Cấu hình ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
API_KEY = os.getenv("API_KEY", "your_super_secret_api_key")
QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
EMBEDDING_MODEL_DIM = int(os.getenv("EMBEDDING_MODEL_DIM", 384))
BASE_MODEL_NAME = os.getenv("BASE_MODEL_NAME", "meta-llama/Meta-Llama-3-8B-Instruct")
VLLM_API_BASE = os.getenv("VLLM_API_BASE", "http://vllm:8001/v1")
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")
S3_ACCESS_KEY_ID = os.getenv("S3_ACCESS_KEY_ID")
S3_SECRET_ACCESS_KEY = os.getenv("S3_SECRET_ACCESS_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# --- Logging ---
logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Clients ---
app = FastAPI(title="TWP-Ω V-Infinity – Perpetual AI OS")
client = httpx.AsyncClient(timeout=30.0)
qdrant = QdrantClient(host=QDRANT_HOST)
s3_client = boto3.client('s3', endpoint_url=S3_ENDPOINT_URL, aws_access_key_id=S3_ACCESS_KEY_ID, aws_secret_access_key=S3_SECRET_ACCESS_KEY)

# --- Xác thực ---
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
async def get_api_key(api_key: str = Security(api_key_header)):
    if not api_key or api_key != API_KEY:
        logger.warning("Invalid or missing API Key received.")
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    return api_key

# --- Logic tải LoRA ---
def download_lora_from_s3(s3_path: str) -> str:
    local_dir = Path("/app/lora_storage") / s3_path
    local_dir.mkdir(parents=True, exist_ok=True)

    response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=s3_path)
    for obj in response.get("Contents", []):
        s3_key = obj["Key"]
        local_file_path = local_dir / Path(s3_key).name
        if not local_file_path.exists():
            logger.info(f"Downloading LoRA file {s3_key} to {local_file_path}")
            s3_client.download_file(S3_BUCKET_NAME, s3_key, str(local_file_path))
    return str(local_dir)

@app.on_event("startup")
async def startup_event():
    # ... (giữ nguyên)

async def call_service(service_name: str, url: str, json_payload: dict):
    # ... (giữ nguyên)

@app.post("/v_infinity/chat")
async def chat(query: str, user_id: str, api_key: str = Security(get_api_key)):
    # ... (logic router, embed, gnn) ...

    # Tải các LoRA cần thiết từ S3
    local_lora_paths = [download_lora_from_s3(path) for path in lora_paths]

    llm_payload = {
        "model": BASE_MODEL_NAME,
        "prompt": f"Context: {context}\nQ: {query}\nAnswer:",
        "max_tokens": 256,
        "lora_paths": local_lora_paths if local_lora_paths else None
    }
    llm_resp = await call_service("vLLM", f"{VLLM_API_BASE}/completions", llm_payload)
    answer = llm_resp.get("choices", [{}])[0].get("text", "No answer generated.")

    return {"answer": answer, "loras_used": len(local_lora_paths)}

# ... (các endpoint khác)
