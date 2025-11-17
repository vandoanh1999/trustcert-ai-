from fastapi import FastAPI
from pydantic import BaseModel
from neo4j import GraphDatabase
from itertools import combinations
from services.common import config
from services.common.hf_client import hf_client # Sử dụng hf_client nếu cần embed lại
from qdrant_client import QdrantClient

app = FastAPI(title="Graph Reasoning Service")

# --- Clients ---
driver = GraphDatabase.driver(
    config.NEO4J_URI,
    auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
)
qdrant = QdrantClient(url=config.QDRANT_URL, api_key=config.QDRANT_API_KEY)


def format_path_to_text(path):
    """Chuyển một đường đi Neo4j thành một câu văn."""
    nodes = [record['name'] for record in path['nodes']]
    relationships = [record['type'] for record in path['relationships']]

    if not nodes:
        return ""

    sentence = nodes[0]
    for i, rel in enumerate(relationships):
        sentence += f" --[{rel}]--> {nodes[i+1]}"
    return sentence

def find_meaningful_paths(tx, entry_nodes: list):
    """
    Tìm tất cả các đường đi ngắn nhất kết nối các cặp nút đầu vào.
    """
    all_paths = []
    # Tạo tất cả các cặp có thể có từ các nút đầu vào
    for node1, node2 in combinations(entry_nodes, 2):
        query = """
        MATCH (a:Node {name: $node1}), (b:Node {name: $node2}),
        p = allShortestPaths((a)-[*..5]-(b))
        RETURN p
        """
        result = tx.run(query, node1=node1, node2=node2)
        for record in result:
            path = record["p"]
            path_info = {
                "nodes": path.nodes,
                "relationships": path.relationships
            }
            all_paths.append(format_path_to_text(path_info))
    return all_paths

class TraverseRequest(BaseModel):
    entry_vector: list[float]

@app.post("/traverse")
def traverse(req: TraverseRequest):
    # 1. Tìm các nút đầu vào từ Qdrant
    hits = qdrant.search(
        collection_name="knowledge_graph",
        query_vector=req.entry_vector,
        limit=3
    )
    entry_nodes = list(set([hit.payload["node"] for hit in hits if "node" in hit.payload]))

    if len(entry_nodes) < 2:
        return {"context_path": "Not enough concepts found in the knowledge graph to form a connection."}

    # 2. Tìm các đường đi kết nối trong Neo4j
    with driver.session() as session:
        paths = session.read_transaction(find_meaningful_paths, entry_nodes)

    if not paths:
        return {"context_path": f"Found concepts: {', '.join(entry_nodes)}. But no direct relationships were found between them."}

    # 3. Tạo bối cảnh từ các đường đi
    context = "Found following connections in knowledge graph:\n- " + "\n- ".join(paths)
    return {"context_path": context}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
