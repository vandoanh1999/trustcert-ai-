from fastapi import FastAPI
import spacy
from graphrag import GraphRAG
from pydantic import BaseModel
from typing import List
import redis
from neo4j import GraphDatabase

app = FastAPI(title="Graph Service")
nlp = spacy.load("en_core_web_sm")
graphrag = GraphRAG()
r = redis.Redis(host='redis', port=6379, db=0)
driver = GraphDatabase.driver("bolt://neo4j:7687", auth=("neo4j", "password"))

def write_graph(tx, nodes, edges, source_id):
    for node in nodes:
        tx.run("MERGE (n:Node {name: $name, source: $source})", name=node, source=source_id)
    for edge in edges:
        tx.run("""
            MATCH (a:Node {name: $from})
            MATCH (b:Node {name: $to})
            MERGE (a)-[:REL {type: $type}]->(b)
        """, from=edge[0], to=edge[1], type=edge[2])

class ExtractRequest(BaseModel):
    text: str

@app.post("/extract")
def extract(req: ExtractRequest):
    doc = nlp(req.text)
    entities = [ent.text for ent in doc.ents]
    # FIXME: This is placeholder logic. A real implementation should use a
    # rule-based or model-based approach to extract relations.
    relations = []  # rule-based
    graph = graphrag.build_graph(entities, relations)
    return {"nodes": [n["name"] for n in graph.nodes], "edges": graph.edges}

class WriteRequest(BaseModel):
    graph: dict
    source_id: str

@app.post("/write_to_neo4j")
def write_to_neo4j(req: WriteRequest):
    with driver.session() as session:
        session.execute_write(write_graph, req.graph["nodes"], req.graph["edges"], req.source_id)
    return {"status": "written"}

class TraverseRequest(BaseModel):
    nodes: List[str]

@app.post("/traverse")
def traverse(req: TraverseRequest):
    key = f"hot:{':'.join(sorted(req.nodes))}"
    cached = r.get(key)
    if cached:
        return {"context": cached.decode(), "source": "cache"}

    context = graphrag.traverse_from_nodes(req.nodes, max_depth=2)
    context_str = " → ".join(context)
    r.setex(key, 300, context_str)
    return {"context": context_str, "source": "computed"}
