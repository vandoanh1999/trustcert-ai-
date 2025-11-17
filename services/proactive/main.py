from fastapi import FastAPI
import asyncio
import httpx
import redis
import feedparser
from services.common import config
from services.common.hf_client import hf_client

app = FastAPI(title="V-God Proactive Core")
client = httpx.AsyncClient()
r = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=0, decode_responses=True)

# ... (logic check_news_feed giữ nguyên) ...

async def proactive_loop():
    while True:
        print("[Proactive-Core]: Sensing for new events...")
        event = await check_news_feed()

        if event:
            print(f"[Proactive-Core]: New event detected! '{event}'")

            # 2. Embed sự kiện (dùng HF client)
            event_vec = await hf_client.get_embedding(event, model=config.EMBEDDING_MODEL_NAME)

            # 3. Tìm user quan tâm (gọi router service)
            # Giả sử router-service được triển khai
            relevant_users_resp = await client.post("http://router-service:8005/find_users_by_topic", json={"vector": event_vec})
            relevant_users = relevant_users_resp.json().get("user_ids", [])

            if not relevant_users:
                print(f"[Proactive-Core]: No users are interested in this event.")

            for user in relevant_users:
                print(f"[Proactive-Core]: User '{user}' is interested. Running GNN...")
                # Giả sử gnn-service được triển khai
                gnn_resp = await client.post("http://gnn-service:8006/traverse", json={"entry_vector": event_vec})
                context = gnn_resp.json()["context_path"]

                message = f"TWP-OMEGA ALERT for {user}: A new event has occurred: '{event}'. Analysis: {context}."
                print(f"[Proactive-Core]: Sending notification: {message}")
                r.publish(f"user_notifications:{user}", message)

        await asyncio.sleep(300)

@app.on_event("startup")
async def startup():
    asyncio.create_task(proactive_loop())
    print("[Proactive-Core]: The heart has started beating.")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
