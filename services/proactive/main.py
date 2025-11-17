# services/proactive/main.py
from fastapi import FastAPI
import asyncio
import httpx
import redis
import feedparser

app = FastAPI(title="V-God Proactive Core")
client = httpx.AsyncClient()
r = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

# URL của một nguồn tin RSS công nghệ
RSS_FEED_URL = "http://feeds.arstechnica.com/arstechnica/index/"
PROCESSED_NEWS_KEY = "processed_news_ids"

async def check_news_feed():
    print(f"[Proactive-Core]: Checking RSS feed: {RSS_FEED_URL}")
    feed = feedparser.parse(RSS_FEED_URL)

    latest_entry = feed.entries[0] if feed.entries else None

    if not latest_entry:
        return None

    # Dùng ID của tin bài để kiểm tra xem đã xử lý chưa
    entry_id = latest_entry.get("id", latest_entry.link)

    # SISMEMBER trả về 0 hoặc 1, không phải boolean
    if r.sismember(PROCESSED_NEWS_KEY, entry_id):
        print(f"[Proactive-Core]: No new events found. Last known ID: {entry_id[:30]}...")
        return None

    # Nếu tin bài là mới, thêm vào set đã xử lý và trả về tiêu đề
    r.sadd(PROCESSED_NEWS_KEY, entry_id)
    return latest_entry.title

async def proactive_loop():
    while True:
        # 1. SENSE (Cảm nhận)
        print("[Proactive-Core]: Sensing for new events...")
        event = await check_news_feed()

        if event:
            print(f"[Proactive-Core]: New event detected! '{event}'")

            # 2. MODEL (Mô hình hóa) - Sự kiện này ảnh hưởng ai?
            event_vec_resp = await client.post("http://embedder:8002/embed", json={"texts": [event]})
            event_vec = event_vec_resp.json()[0]

            # 3. PLAN (Lên kế hoạch)
            # a. Tìm user nào quan tâm?
            relevant_users_resp = await client.post("http://router:8005/find_users_by_topic", json={"vector": event_vec})
            relevant_users = relevant_users_resp.json().get("user_ids", [])

            if not relevant_users:
                print(f"[Proactive-Core]: No users are interested in this event.")

            for user in relevant_users:
                print(f"[Proactive-Core]: User '{user}' is interested. Running GNN...")
                # b. Nó ảnh hưởng thế nào?
                gnn_resp = await client.post("http://gnn:8006/traverse", json={"entry_vector": event_vec})
                context = gnn_resp.json()["context_path"]

                # 4. ACT (Hành động)
                message = f"TWP-OMEGA ALERT for {user}: A new event has occurred that may interest you: '{event}'. Our analysis suggests: {context}. You may want to check your portfolio."
                print(f"[Proactive-Core]: Sending notification: {message}")

                r.publish(f"user_notifications:{user}", message)

        # Chờ 5 phút trước khi kiểm tra lại
        await asyncio.sleep(300)

@app.on_event("startup")
async def startup():
    asyncio.create_task(proactive_loop())
    print("[Proactive-Core]: The heart has started beating.")
