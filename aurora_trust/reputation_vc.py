"""
Aurora Trust V7: Reputation and Verifiable Credentials Engine

This module manages the reputation of expert adapters using an
Exponential Moving Average (EMA) for stability and responsiveness.
It also issues Verifiable Credentials (VCs).
"""
import json
import time
import os
import hashlib
import hmac
from typing import Dict, Any, List
import torch

# --- Constants ---
REP_DB_PATH = "aurora_reputation.json"
VC_STORE_PATH = "aurora_vc_store.json"
VC_SIGNING_KEY = b"genesis_v7_symbiotic_network_key"
REPUTATION_LEARNING_RATE = 0.1 # Alpha for the EMA formula

# --- Reputation Management (V7) ---

def load_reputation_db() -> Dict[str, float]:
    """Loads the reputation database from a local JSON file."""
    if os.path.exists(REP_DB_PATH):
        with open(REP_DB_PATH, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {} # Return empty dict if file is corrupt or empty
    return {}

def save_reputation_db(db: Dict[str, float]):
    """Saves the reputation database to a local JSON file."""
    with open(REP_DB_PATH, "w") as f:
        json.dump(db, f, indent=2)

def get_reputation(expert_id: str) -> float:
    """Gets the reputation score for a given expert, defaulting to 0.5."""
    db = load_reputation_db()
    return float(db.get(expert_id, 0.5))

def update_reputation_with_feedback(expert_id: str, feedback_score: float) -> float:
    """
    Updates an expert's reputation based on new feedback using EMA.

    Formula: NewScore = (1 - α) * OldScore + α * FeedbackScore
    """
    old_score = get_reputation(expert_id)

    # Clamp feedback score to a safe range [0.0, 1.0]
    clamped_feedback = max(0.0, min(1.0, feedback_score))

    new_score = (1 - REPUTATION_LEARNING_RATE) * old_score + REPUTATION_LEARNING_RATE * clamped_feedback

    db = load_reputation_db()
    db[expert_id] = new_score
    save_reputation_db(db)

    print(f"Reputation for '{expert_id}' updated: {old_score:.4f} -> {new_score:.4f}")
    return new_score

# --- Verifiable Credential (VC) Management (remains the same as V6) ---

def sign_payload_hmac(payload: bytes) -> str:
    return hmac.new(VC_SIGNING_KEY, payload, digestmod=hashlib.sha256).hexdigest()

def issue_vc(expert_id: str, contribution: float, metadata: Dict[str, Any]) -> Dict[str, Any]:
    vc = {
        "issuer": "aurora_trust_engine_v7",
        "issuanceDate": int(time.time()),
        "credentialSubject": {
            "id": expert_id,
            "contributionScore": float(contribution),
            "metadata": metadata
        }
    }
    payload = json.dumps(vc, sort_keys=True).encode("utf8")
    signature = sign_payload_hmac(payload)

    vc_obj = {"credential": vc, "proof": {"type": "HmacSha256", "signature": signature}}

    store = []
    if os.path.exists(VC_STORE_PATH):
        with open(VC_STORE_PATH, "r") as f:
            store = json.load(f)
    store.append(vc_obj)
    with open(VC_STORE_PATH, "w") as f:
        json.dump(store, f, indent=2)

    return vc_obj
