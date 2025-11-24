"""
Genesis Core V4: The Oracle Brain
This is the V4 implementation of the SemanticRouter, now acting as the "Oracle Brain".

It uses two stages of models for maximum intelligence:
1.  **SentenceTransformer:** To get a deep, semantic understanding of the
    user's query, represented as a high-dimensional vector.
2.  **Fine-tuned Classifier (L2 Router):** A small, fast model trained to take
    the semantic vector and classify it into a specific domain, outputting
    a probability distribution across all known domains.
"""

import numpy as np
import torch
import json
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import Tuple, Dict, List
import os

class OracleBrain:
    _sbert_model = None
    _l2_model = None
    _l2_tokenizer = None
    _l2_id2label = None

    def __init__(self,
                 sbert_model_name: str = 'all-MiniLM-L6-v2',
                 l2_model_path: str = "l2_router_model/final_model"):

        # Load SentenceTransformer (SBERT) for embedding
        if OracleBrain._sbert_model is None:
            print(f"Loading SentenceTransformer model: {sbert_model_name}...")
            OracleBrain._sbert_model = SentenceTransformer(sbert_model_name)
            print("SBERT model loaded.")
        self.sbert_encoder = OracleBrain._sbert_model

        # Load Fine-tuned L2 Router model for classification
        if OracleBrain._l2_model is None:
            if not os.path.exists(l2_model_path):
                print(f"Warning: L2 router model not found at '{l2_model_path}'. The Oracle Brain will operate in a fallback mode.")
            else:
                print(f"Loading L2 Router model from: {l2_model_path}...")
                OracleBrain._l2_model = AutoModelForSequenceClassification.from_pretrained(l2_model_path)
                OracleBrain._l2_tokenizer = AutoTokenizer.from_pretrained(l2_model_path)

                # Load label mappings
                with open(os.path.join(l2_model_path, "label_mappings.json"), "r") as f:
                    mappings = json.load(f)
                    OracleBrain._l2_id2label = mappings['id2label']
                print("L2 Router model loaded.")

    def get_embedding(self, text: str) -> np.ndarray:
        """Generates a semantic embedding for the given text."""
        return self.sbert_encoder.encode(text, normalize_embeddings=True, convert_to_numpy=True)

    def route(self, text: str) -> Tuple[np.ndarray, Dict[str, float]]:
        """
        Routes the text to produce a query vector and a probability distribution over domains.

        Returns:
            - A high-quality query vector for similarity search.
            - A dictionary of {domain: probability_score}.
        """
        query_vec = self.get_embedding(text)

        if OracleBrain._l2_model is None:
            # Fallback mode: if no L2 model, return a generic distribution
            return query_vec, {"general": 1.0}

        # Use the L2 router to get domain probabilities
        inputs = OracleBrain._l2_tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            logits = OracleBrain._l2_model(**inputs).logits

        probabilities = torch.nn.functional.softmax(logits, dim=-1)[0]

        domain_scores = {OracleBrain._l2_id2label[str(i)]: prob.item() for i, prob in enumerate(probabilities)}

        return query_vec, domain_scores

# Example Usage
if __name__ == '__main__':
    print("--- Oracle Brain Demo ---")
    # This demo requires a trained L2 model to exist at 'l2_router_model/final_model'

    # Create dummy model for demonstration if it doesn't exist
    dummy_path = "l2_router_model/final_model"
    if not os.path.exists(dummy_path):
        print(f"Creating a dummy L2 router model at '{dummy_path}' for demonstration purposes...")
        dummy_tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
        dummy_model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=3)
        dummy_model.save_pretrained(dummy_path)
        dummy_tokenizer.save_pretrained(dummy_path)
        dummy_mappings = {"id2label": {"0": "legal", "1": "medical", "2": "code"}, "label2id": {"legal": 0, "medical": 1, "code": 2}}
        with open(os.path.join(dummy_path, "label_mappings.json"), "w") as f:
            json.dump(dummy_mappings, f)

    # Now, initialize the Oracle Brain
    oracle = OracleBrain()

    test_query = "How do I fix a null pointer exception in my Java code?"

    print(f"\nRouting query: '{test_query}'")
    query_vector, domain_probs = oracle.route(test_query)

    print(f"\nGenerated Query Vector Shape: {query_vector.shape}")
    print("Predicted Domain Probabilities:")
    for domain, prob in sorted(domain_probs.items(), key=lambda item: item[1], reverse=True):
        print(f"  - {domain}: {prob:.4f}")

    # The top domain would be used for primary expert selection, but others can be used
    # for creating hybrid experts.
    top_domain = max(domain_probs, key=domain_probs.get)
    print(f"\nTop Predicted Domain: {top_domain}")
