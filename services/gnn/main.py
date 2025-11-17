# services/gnn/main.py
from fastapi import FastAPI
import torch
from torch_geometric.data import Data
from torch_geometric.nn import GCNConv
from pydantic import BaseModel
from neo4j import GraphDatabase
import numpy as np
from qdrant_client import QdrantClient
import httpx

app = FastAPI(title="GNN Service (Real-Eyes)")
driver = GraphDatabase.driver("bolt://neo4j:7687", auth=("neo4j", "password"))
qdrant = QdrantClient("http://qdrant:6333")
client = httpx.Client() # Để embed nếu cần

class GCN(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = GCNConv(384, 64) # Corrected embed_dim to 384
        self.conv2 = GCNConv(64, 32)
    def forward(self, data):
        x, edge_index = data.x, data.edge_index
        x = self.conv1(x, edge_index).relu()
        x = self.conv2(x, edge_index)
        return x.mean(dim=0)

model = GCN()

def get_real_subgraph(entry_vector: list[float]) -> Data:
    # 1. DÙNG VECTOR ĐỂ TÌM "ĐIỂM VÀO" TRÊN GRAPH
    hits = qdrant.search(
        collection_name="knowledge_graph",
        query_vector=entry_vector,
        limit=3 # Lấy 3 node gần nhất làm điểm vào
    )
    entry_nodes = [hit.payload["node"] for hit in hits if "node" in hit.payload]

    if not entry_nodes:
        # Nếu không có gì, trả về graph rỗng
        return Data(x=torch.empty(0, 384), edge_index=torch.empty(0, 2, dtype=torch.long))

    # 2. DÙNG CYPHER THẬT: LẤY 2-HOP SUBGRAPH TỪ ĐIỂM VÀO
    with driver.session() as session:
        result = session.run("""
            MATCH (start:Node) WHERE start.name IN $nodes
            CALL {
                WITH start
                MATCH (start)-[r*1..2]-(neighbor)
                RETURN DISTINCT neighbor AS n
                UNION
                WITH start
                RETURN start AS n
            }
            RETURN n.name AS name
            """, nodes=entry_nodes
        )
        subgraph_nodes = [r["name"] for r in result]

        # Lấy các cạnh (edges) trong subgraph
        edges_result = session.run("""
            MATCH (a:Node)-[r:REL]->(b:Node)
            WHERE a.name IN $nodes AND b.name IN $nodes
            RETURN a.name AS u, b.name AS v
            """, nodes=subgraph_nodes
        )

    # Tạo map từ tên node về index
    node_map = {name: i for i, name in enumerate(subgraph_nodes)}
    edges = []
    for r in edges_result:
        if r["u"] in node_map and r["v"] in node_map:
            edges.append([node_map[r["u"]], node_map[r["v"]]])

    # 3. LẤY EMBEDDING CHO CÁC NODE (Feature)
    # Chúng ta phải lấy embedding thật của các node này
    node_vectors_resp = client.post("http://embedder:8002/embed",
                                    json={"texts": subgraph_nodes})
    node_vectors = np.array(node_vectors_resp.json())

    x = torch.tensor(node_vectors, dtype=torch.float)
    edge_index = torch.tensor(edges, dtype=torch.long).t().contiguous() if edges else torch.empty(2, 0, dtype=torch.long)

    return Data(x=x, edge_index=edge_index)


class TraverseRequest(BaseModel):
    entry_vector: list[float]

@app.post("/traverse")
def traverse(req: TraverseRequest):
    data = get_real_subgraph(req.entry_vector)
    if data.x.shape[0] == 0:
        return {"context_path": "Không tìm thấy suy luận."}

    path_vector = model(data).tolist()
    context_path = f"Suy luận (Graph-real): {len(data.x)} nodes, {data.edge_index.shape[1]} edges. Path vector: {path_vector[:3]}"
    return {"context_path": context_path}
