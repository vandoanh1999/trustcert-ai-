from fastapi import FastAPI
import spacy
from pydantic import BaseModel
from typing import List, Dict, Any
from neo4j import GraphDatabase
from .logic import extract_svo_relations, build_graph
from ..common import config

app = FastAPI(title="Graph Service")
nlp = spacy.load("en_core_web_sm")

# Kết nối đến Neo4j AuraDB
driver = GraphDatabase.driver(
    config.NEO4J_URI,
    auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
)

def write_graph_to_neo4j(tx, nodes, edges, source_id):
    """
    Ghi các node và cạnh vào Neo4j bằng một transaction.
    Sử dụng MERGE để tránh tạo các node/cạnh trùng lặp.
    """
    # Tạo hoặc cập nhật các node
    tx.run("""
        UNWIND $nodes AS node_name
        MERGE (n:Node {name: node_name})
        SET n.source = $source_id
    """, nodes=nodes, source_id=source_id)

    # Tạo các mối quan hệ
    for edge in edges:
        tx.run("""
            MATCH (a:Node {name: $source_node})
            MATCH (b:Node {name: $target_node})
            MERGE (a)-[r:RELATED_TO {type: $rel_type}]->(b)
        """, source_node=edge['source'], target_node=edge['target'], rel_type=edge['type'])

# ... (các class và endpoint giữ nguyên, nhưng loại bỏ logic Redis) ...

@app.post("/traverse")
def traverse(req: TraverseRequest):
    # Tạm thời loại bỏ cache, sẽ có chiến lược cache khác sau này
    context = " → ".join(req.nodes)
    return {"context": context, "source": "computed"}

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
