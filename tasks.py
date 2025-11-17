from celery import Celery
import httpx
from qdrant_client import QdrantClient, models
from services.common import config
from services.common.hf_client import hf_client # Import client mới
import asyncio

celery_app = Celery('tasks', broker=f'redis://{config.REDIS_HOST}:{config.REDIS_PORT}/0')
client = httpx.Client()

@celery_app.task
def assimilate_task(source_id: str, content: str, user_id: str):

    async def do_assimilation():
        # 1. Extract graph
        graph = client.post(f"{config.GRAPH_URL}/extract", json={"text": content}).json()
        nodes = graph.get("nodes", [])
        if not nodes:
            return {"status": "done", "lora_path": "N/A", "entities": 0, "relations": 0}

        # 2. Embed nodes (dùng HF API)
        vectors = await hf_client.get_embeddings(nodes, model=config.EMBEDDING_MODEL_NAME)

        # 3. Upsert Qdrant
        qdrant = QdrantClient(url=config.QDRANT_URL, api_key=config.QDRANT_API_KEY)
        qdrant.upsert(
            collection_name="knowledge_graph",
            points=[
                models.PointStruct(
                    id=f"{source_id}_{i}",
                    vector=vec,
                    payload={"node": node, "source": source_id}
                ) for i, (vec, node) in enumerate(zip(vectors, nodes))
            ]
        )

        # 4. Ghi graph vào Neo4j
        client.post(f"{config.GRAPH_URL}/write_to_neo4j", json={"graph": graph, "source_id": source_id})

        # 5. Huấn luyện LoRA sẽ được chuyển sang Colab Notebook
        # Tạm thời bỏ qua bước này
        lora_path = "N/A - Use Colab Notebook for training"

        return {"status": "done", "lora_path": lora_path, "entities": len(nodes), "relations": len(graph.get("edges", []))}

    # Chạy hàm async bên trong tác vụ Celery sync
    return asyncio.run(do_assimilation())
