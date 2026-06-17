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
    # ... (giữ nguyên logic) ...

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
