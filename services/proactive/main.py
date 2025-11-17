# services/proactive/main.py
from fastapi import FastAPI
import asyncio
import httpx
import redis

app = FastAPI(title="V-God Proactive Core")
client = httpx.AsyncClient()
r = redis.Redis(host='redis', port=6379, db=0)

async def check_gold_price_rss():
    # Giả lập check RSS feed
    await asyncio.sleep(10) # 10s check 1 lần
    # Giả lập phát hiện tin mới
    price_dropped = True
    if price_dropped:
        return "Giá vàng vừa sập 10%."
    return None

async def proactive_loop():
    while True:
        # 1. SENSE (Cảm nhận)
        print("[Proactive-Core]: Đang cảm nhận...")
        event = await check_gold_price_rss() # Chờ sự kiện

        if event:
            print(f"[Proactive-Core]: Phát hiện sự kiện! '{event}'")

            # 2. MODEL (Mô hình hóa) - Sự kiện này ảnh hưởng ai?
            # Embed sự kiện
            event_vec_resp = await client.post("http://embedder:8002/embed", json={"texts": [event]})
            event_vec = event_vec_resp.json()[0]

            # 3. PLAN (Lên kế hoạch)
            # a. Tìm user nào quan tâm? (Query vào LoRA Registry)
            relevant_users_resp = await client.post("http://router:8005/find_users_by_topic", json={"vector": event_vec})
            relevant_users = relevant_users_resp.json().get("user_ids", [])

            for user in relevant_users:
                print(f"[Proactive-Core]: User '{user}' có quan tâm. Đang suy luận GNN...")
                # b. Nó ảnh hưởng thế nào? (Chạy GNN)
                gnn_resp = await client.post("http://gnn:8006/traverse", json={"entry_vector": event_vec})
                context = gnn_resp.json()["context_path"]

                # 4. ACT (Hành động)
                message = f"CẢNH BÁO TỪ TWP-OMEGA: Này {user}, {event}. {context}. Mày nên check portfolio."
                print(f"[Proactive-Core]: Đang gửi: {message}")

                # Gửi thông báo (ví dụ qua Redis Pub/Sub, app sẽ nghe)
                r.publish(f"user_notifications:{user}", message)

        await asyncio.sleep(60) # Chờ 1 phút cho vòng lặp tiếp

@app.on_event("startup")
async def startup():
    # Khởi động "trái tim"
    asyncio.create_task(proactive_loop())
    print("[Proactive-Core]: Trái tim đã bắt đầu đập.")
