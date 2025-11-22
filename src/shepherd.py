
from sentence_transformers import SentenceTransformer
import numpy as np
_MODEL = None
def load_shepherd(model_name='all-MiniLM-L6-v2'):
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer(model_name)
    return _MODEL
def shepherd_embed(text: str):
    model = load_shepherd()
    vec = model.encode(text, normalize_embeddings=True)
    return vec.astype('float32')
