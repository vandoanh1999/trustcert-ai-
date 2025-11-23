"""
V3 Semantic Router
- Uses a real SentenceTransformer model for semantic understanding.
- Caches the model for efficiency.
- Still includes L1 keyword routing as a fast path.
"""

import numpy as np
from sentence_transformers import SentenceTransformer

class SemanticRouter:
    _model = None

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        if SemanticRouter._model is None:
            print(f"Loading SentenceTransformer model: {model_name}...")
            SemanticRouter._model = SentenceTransformer(model_name)
            print("Model loaded.")
        self.encoder = SemanticRouter._model

        # Keyword routing can still be a useful heuristic or for domain forcing
        self.domain_keywords = {
            "math": ["solve", "integral", "equation", "algebra", "calculus", "derivative"],
            "code": ["python", "javascript", "bug", "error", "function", "algorithm", "class"],
            "history": ["war", "king", "empire", "ancient", "renaissance", "revolution"],
        }

    def _encode(self, text: str) -> np.ndarray:
        """Encodes text and normalizes the embedding."""
        return self.encoder.encode(text, normalize_embeddings=True, convert_to_numpy=True)

    def l1_keyword_route(self, text: str) -> str | None:
        """Fast path keyword-based routing."""
        t = text.lower()
        for domain, keywords in self.domain_keywords.items():
            if any(k in t for k in keywords):
                return domain
        return None

    def route(self, text: str) -> tuple[str, np.ndarray]:
        """
        Routes the text to a domain and returns the domain and query vector.
        It uses keyword search as a primary override. If no keyword is found,
        it would typically use a more sophisticated L2 router. For now, we'll
        default to a "general" domain in the L2 case, but the key is the
        high-quality semantic vector that is generated.
        """
        query_vec = self._encode(text)

        # The L1 route can act as a "domain hint"
        l1_domain = self.l1_keyword_route(text)

        # In a true V3, the L2 router would be a classifier model trained on
        # these embeddings. For now, we prioritize the L1 hint, then default.
        final_domain = l1_domain if l1_domain else "general"

        return final_domain, query_vec
