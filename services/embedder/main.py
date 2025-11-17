from fastapi import FastAPI
from sentence_transformers import SentenceTransformer
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Embedder Service")
embedder = SentenceTransformer('BAAI/bge-small-en-v1.5', device='cuda')

class EmbedRequest(BaseModel):
    texts: List[str]

@app.post("/embed")
def embed(req: EmbedRequest):
    vectors = embedder.encode(req.texts, batch_size=32, show_progress_bar=False)
    return vectors.tolist()
