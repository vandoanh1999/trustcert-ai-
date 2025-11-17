from celery import Celery
import httpx

celery_app = Celery('tasks', broker='redis://redis:6379/0')
client = httpx.Client()

@celery_app.task
def assimilate_task(source_id: str, content: str, user_id: str):
    # 1. Extract graph
    graph = client.post("http://graph:8003/extract", json={"text": content}).json()

    # 2. Embed nodes
    vectors = client.post("http://embedder:8002/embed", json={"texts": graph["nodes"]}).json()

    # 3. Upsert Qdrant
    from qdrant_client import QdrantClient, models
    qdrant = QdrantClient("http://qdrant:6333")
    qdrant.upsert(
        collection_name="knowledge_graph",
        points=[
            models.PointStruct(
                id=f"{source_id}_{i}",
                vector=vec,
                payload={"node": node, "source": source_id}
            ) for i, (vec, node) in enumerate(zip(vectors, graph["nodes"]))
        ]
    )

    # 4. Ghi graph vào Neo4j
    client.post("http://graph:8003/write_to_neo4j", json={"graph": graph, "source_id": source_id})

    # 5. Train S-LoRA qua trainer-service
    train_resp = client.post("http://trainer:8007/train_lora", json={"content": content, "user_id": user_id, "source_id": source_id})
    lora_path = train_resp.json()["lora_path"]

    return {"status": "done", "lora_path": lora_path, "entities": len(graph["nodes"]), "relations": len(graph["edges"])}
