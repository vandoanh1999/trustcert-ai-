from fastapi import FastAPI
import httpx
from qdrant_client import QdrantClient, models
from tasks import assimilate_task

app = FastAPI(title="TWP-Ω V-Infinity – Perpetual AI OS")
client = httpx.AsyncClient(timeout=30.0)
qdrant = QdrantClient("http://qdrant:6333")

@app.on_event("startup")
async def startup_event():
    try:
        qdrant.get_collection(collection_name="knowledge_graph")
    except Exception:
        qdrant.create_collection(
            collection_name="knowledge_graph",
            vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
        )

async def call_llm(prompt: str, lora_paths: list = []):
    resp = await client.post("http://vllm:8001/v1/completions", json={
        "model": "meta-llama/Meta-Llama-3-8B-Instruct",
        "prompt": prompt,
        "max_tokens": 256,
        "lora_paths": lora_paths if lora_paths else None
    })
    return resp.json()["choices"][0]["text"]

@app.post("/v_infinity/chat")
async def chat(query: str, user_id: str):
    # 1. Cognitive Router: Chọn S-LoRA
    router_resp = await client.post("http://router:8005/analyze", json={"query": query, "user_id": user_id})
    lora_paths = router_resp.json()["selected_loras"]

    # 2. Dynamic batch embed
    resp = await client.post("http://batcher:8004/batch_sync", json={"text": query})
    q_vec = resp.json()["vector"]

    # 3. GNN: Traverse graph
    gnn_resp = await client.post("http://gnn:8006/traverse", json={"entry_vector": q_vec})
    context = gnn_resp.json()["context_path"]

    # 4. LLM with S-LoRA
    answer = await call_llm(f"Context: {context}\nQ: {query}\nAnswer:", lora_paths)

    return {"answer": answer, "loras_used": len(lora_paths)}

@app.post("/v_infinity/assimilate")
async def assimilate(source_id: str, content: str, user_id: str):
    job = assimilate_task.delay(source_id, content, user_id)
    return {"status": "queued", "job_id": job.id}

@app.get("/v_infinity/job/{job_id}")
async def get_job(job_id: str):
    job = assimilate_task.AsyncResult(job_id)
    return {"status": job.state, "result": job.result if job.ready() else None}
