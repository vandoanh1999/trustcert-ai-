from fastapi import FastAPI
import spacy
from pydantic import BaseModel
from typing import List, Dict, Any
import redis
from neo4j import GraphDatabase
from .logic import extract_svo_relations, build_graph

app = FastAPI(title="Graph Service")
nlp = spacy.load("en_core_web_sm")
r = redis.Redis(host='redis', port=6379, db=0)
driver = GraphDatabase.driver("bolt://neo4j:7687", auth=("neo4j", "password"))

def write_graph_to_neo4j(tx, nodes, edges, source_id):
    for node in nodes:
        tx.run("MERGE (n:Node {name: $name, source: $source})", name=node['name'], source=source_id)
    for edge in edges:
        tx.run("""
            MATCH (a:Node {name: $startNode})
            MATCH (b:Node {name: $endNode})
            MERGE (a)-[:REL {type: $relType}]->(b)
        """, startNode=edge[0], endNode=edge[1], relType=edge[2])

class ExtractRequest(BaseModel):
    text: str

@app.post("/extract")
def extract(req: ExtractRequest):
    doc = nlp(req.text)
    entities = [ent.text for ent in doc.ents]
    relations = extract_svo_relations(doc)
    graph = build_graph(entities, relations)
    return {"nodes": [n["name"] for n in graph["nodes"]], "edges": graph["edges"]}

class WriteRequest(BaseModel):
    graph: Dict[str, Any]
    source_id: str

@app.post("/write_to_neo4j")
def write_to_neo4j(req: WriteRequest):
    with driver.session() as session:
        session.execute_write(write_graph_to_neo4j, req.graph["nodes"], req.graph["edges"], req.source_id)
    return {"status": "written"}

class TraverseRequest(BaseModel):
    nodes: List[str]

@app.post("/traverse")
def traverse(req: TraverseRequest):
    key = f"hot:{':'.join(sorted(req.nodes))}"
    cached = r.get(key)
    if cached:
        return {"context": cached.decode(), "source": "cache"}

    # Placeholder for GraphRAG-like traversal
    context = " → ".join(req.nodes)
    r.setex(key, 300, context)
    return {"context": context, "source": "computed"}
