"""
Genesis Core V6: The Oracle Brain (Upgraded)

The V6 Oracle Brain now integrates with the Aurora Trust system to factor
expert reputation into its routing decisions, providing a richer context
for the Hypercontroller.
"""

import numpy as np
import torch
import json
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import Tuple, Dict, List, Any
import os

# V6: Import the reputation system
from aurora_trust import get_reputation

class OracleBrain:
    # (Singleton pattern for models remains the same)
    _sbert_model = None
    _l2_model = None
    _l2_tokenizer = None
    _l2_id2label = None

    def __init__(self,
                 sbert_model_name: str = 'all-MiniLM-L6-v2',
                 l2_model_path: str = "l2_router_model/final_model"):

        if OracleBrain._sbert_model is None:
            # Code to load SBERT model...
            OracleBrain._sbert_model = SentenceTransformer(sbert_model_name)
        self.sbert_encoder = OracleBrain._sbert_model

        if OracleBrain._l2_model is None:
            # Code to load L2 router model...
            if os.path.exists(l2_model_path):
                OracleBrain._l2_model = AutoModelForSequenceClassification.from_pretrained(l2_model_path)
                OracleBrain._l2_tokenizer = AutoTokenizer.from_pretrained(l2_model_path)
                with open(os.path.join(l2_model_path, "label_mappings.json"), "r") as f:
                    mappings = json.load(f)
                    OracleBrain._l2_id2label = mappings['id2label']

    def route(self, text: str) -> Tuple[torch.Tensor, Dict[str, float]]:
        """
        Produces a query vector and a probability distribution over domains.
        The query vector is now a torch.Tensor for consistency with the forge.
        """
        embedding = self.sbert_encoder.encode(text, normalize_embeddings=True, convert_to_tensor=True)
        query_vec = embedding.float()

        if OracleBrain._l2_model is None:
            return query_vec, {"general": 1.0}

        inputs = OracleBrain._l2_tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            logits = OracleBrain._l2_model(**inputs).logits

        probabilities = torch.nn.functional.softmax(logits, dim=-1)[0]
        domain_scores = {OracleBrain._l2_id2label[str(i)]: prob.item() for i, prob in enumerate(probabilities)}

        return query_vec, domain_scores

    def gather_context_for_forge(
        self,
        query_text: str,
        candidates: List[Dict[str, Any]]
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        V6 Feature: Gathers all necessary context for the Hypercontroller.

        Args:
            query_text: The user's original query.
            candidates: The list of candidate experts from the WeightIndex.

        Returns:
            A tuple of (intent_vector, reputation_scores_tensor).
        """
        # 1. Generate an intent vector for the query.
        #    In V6, this is simplified. The Oracle's main role is routing,
        #    but we can use a simpler encoder for the Hypercontroller's intent.
        from fusion_forge.hypercontroller import IntentEncoder
        intent_encoder = IntentEncoder(device=query_text.device if isinstance(query_text, torch.Tensor) else 'cpu')
        intent_vector = intent_encoder(query_text)

        # 2. Retrieve reputation scores for each candidate from Aurora Trust.
        reputation_scores = [get_reputation(c['id']) for c in candidates]
        reputation_tensor = torch.tensor(reputation_scores, dtype=torch.float32, device=intent_vector.device)

        return intent_vector, reputation_tensor
