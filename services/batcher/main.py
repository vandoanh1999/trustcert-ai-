from fastapi import FastAPI, Request
from typing import Dict
import asyncio
import httpx
import uuid

app = FastAPI()
queue = asyncio.Queue()
client = httpx.AsyncClient(base_url="http://embedder:8002", timeout=10.0)

pending_futures: Dict[str, asyncio.Future] = {}

async def batch_worker():
    while True:
        await asyncio.sleep(0.015)
        batch_items = []
        while not queue.empty() and len(batch_items) < 64:
            batch_items.append(await queue.get())

        if not batch_items:
            continue

        texts = [item["text"] for item in batch_items]
        request_ids = [item["id"] for item in batch_items]

        vectors = (await client.post("/embed", json={"texts": texts})).json()

        for req_id, vector in zip(request_ids, vectors):
            future = pending_futures.pop(req_id, None)
            if future:
                future.set_result(vector)

@app.on_event("startup")
async def startup():
    asyncio.create_task(batch_worker())

@app.post("/batch_sync")
async def batch_sync(req: Request):
    text = (await req.json())["text"]
    req_id = str(uuid.uuid4())

    future = asyncio.get_event_loop().create_future()
    pending_futures[req_id] = future

    await queue.put({"id": req_id, "text": text})

    vector = await future

    return {"vector": vector}
