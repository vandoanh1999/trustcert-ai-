from fastapi import FastAPI, HTTPException
import httpx
from qdrant_client import QdrantClient, models
from tasks import assimilate_task
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="TWP-Ω V-Infinity – Perpetual AI OS")
client = httpx.AsyncClient(timeout=30.0)
qdrant = QdrantClient("http://qdrant:6333")

@app.on_event("startup")
async def startup_event():
    logger.info("Gateway service starting up.")
    try:
        qdrant.get_collection(collection_name="knowledge_graph")
        logger.info("Qdrant collection 'knowledge_graph' already exists.")
    except Exception:
        logger.info("Creating Qdrant collection 'knowledge_graph'.")
        qdrant.create_collection(
            collection_name="knowledge_graph",
            vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
        )

async def call_service(service_name: str, url: str, json_payload: dict):
    try:
        logger.info(f"Calling {service_name} at {url}")
        resp = await client.post(url, json=json_payload)
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error calling {service_name}: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Error from {service_name}: {e.response.text}")
    except httpx.RequestError as e:
        logger.error(f"Request error calling {service_name}: {e}")
        raise HTTPException(status_code=503, detail=f"Could not connect to {service_name}.")

@app.post("/v_infinity/chat")
async def chat(query: str, user_id: str):
    logger.info(f"Received chat request from user '{user_id}' with query: '{query[:50]}...'")

    # 1. Cognitive Router
    router_payload = {"query": query, "user_id": user_id}
    router_resp = await call_service("Router", "http://router:8005/analyze", router_payload)
    lora_paths = router_resp.get("selected_loras", [])
    logger.info(f"Router selected {len(lora_paths)} LoRAs.")

    # 2. Dynamic Batch Embed
    embed_payload = {"text": query}
    embed_resp = await call_service("Batcher", "http://batcher:8004/batch_sync", embed_payload)
    q_vec = embed_resp.get("vector")

    # 3. GNN Traverse
    gnn_payload = {"entry_vector": q_vec}
    gnn_resp = await call_service("GNN", "http://gnn:8006/traverse", gnn_payload)
    context = gnn_resp.get("context_path", "No context found.")
    logger.info(f"GNN returned context: {context[:100]}...")

    # 4. LLM with S-LoRA
    llm_payload = {
        "model": "meta-llama/Meta-Llama-3-8B-Instruct",
        "prompt": f"Context: {context}\nQ: {query}\nAnswer:",
        "max_tokens": 256,
        "lora_paths": lora_paths if lora_paths else None
    }
    llm_resp = await call_service("vLLM", "http://vllm:8001/v1/completions", llm_payload)
    answer = llm_resp.get("choices", [{}])[0].get("text", "No answer generated.")

    return {"answer": answer, "loras_used": len(lora_paths)}

@app.post("/v_infinity/assimilate")
async def assimilate(source_id: str, content: str, user_id: str):
    logger.info(f"Queueing assimilation task for source '{source_id}' from user '{user_id}'.")
    job = assimilate_task.delay(source_id, content, user_id)
    return {"status": "queued", "job_id": job.id}

@app.get("/v_infinity/job/{job_id}")
async def get_job(job_id: str):
    logger.info(f"Checking status for job '{job_id}'.")
    job = assimilate_task.AsyncResult(job_id)
    return {"status": job.state, "result": job.result if job.ready() else None}
