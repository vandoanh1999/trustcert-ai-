"""
Aurora Trust V8: Reputation, VCs, and Decentralized Identity (Refactored)

This version uses the centralized config for all parameters.
"""
import json
import time
import os
import hashlib
import hmac
from typing import Dict, Any, List
from core.config import *

# --- Constants ---
REP_DB_PATH = "aurora_reputation.json"
VC_STORE_PATH = "aurora_vc_store.json"

# --- Reputation Management ---

_REPUTATION_CACHE: Dict[str, float] = None

def load_reputation_db() -> Dict[str, float]:
    global _REPUTATION_CACHE
    if _REPUTATION_CACHE is not None:
        return dict(_REPUTATION_CACHE)

    if os.path.exists(REP_DB_PATH):
        with open(REP_DB_PATH, "r") as f:
            try:
                _REPUTATION_CACHE = json.load(f)
                return dict(_REPUTATION_CACHE)
            except json.JSONDecodeError:
                _REPUTATION_CACHE = {}
                return dict(_REPUTATION_CACHE)
    _REPUTATION_CACHE = {}
    return dict(_REPUTATION_CACHE)

def save_reputation_db(db: Dict[str, float]):
    global _REPUTATION_CACHE
    _REPUTATION_CACHE = db
    with open(REP_DB_PATH, "w") as f:
        json.dump(db, f, indent=2)

def get_reputation(expert_id: str) -> float:
    db = load_reputation_db()
    return float(db.get(expert_id, 0.5))

def update_reputation_with_feedback(expert_id: str, feedback_score: float) -> float:
    old_score = get_reputation(expert_id)
    clamped_feedback = max(0.0, min(1.0, feedback_score))
    new_score = (1 - REPUTATION_EMA_LEARNING_RATE) * old_score + REPUTATION_EMA_LEARNING_RATE * clamped_feedback
    db = load_reputation_db()
    db[expert_id] = new_score
    save_reputation_db(db)
    return new_score

# --- Verifiable Credential (VC) Management ---

def sign_payload_hmac(payload: bytes) -> str:
    return hmac.new(VC_SIGNING_KEY, payload, digestmod=hashlib.sha256).hexdigest()

def issue_vc(subject_id: str, credential_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
    vc = {
        "issuer": "aurora_trust_engine_v8",
        "issuanceDate": int(time.time()),
        "type": credential_type,
        "credentialSubject": { "id": subject_id, **details }
    }
    payload = json.dumps(vc, sort_keys=True).encode("utf8")
    signature = sign_payload_hmac(payload)
    vc_obj = {"credential": vc, "proof": {"type": "HmacSha256", "signature": signature}}

    store = []
    if os.path.exists(VC_STORE_PATH):
        with open(VC_STORE_PATH, "r") as f: store = json.load(f)
    store.append(vc_obj)
    with open(VC_STORE_PATH, "w") as f: json.dump(store, f, indent=2)
    return vc_obj

def issue_tier_credential(user_id: str, tier: str, contribution_score: float) -> Dict[str, Any]:
    details = {"tier": tier, "achievedWithContributionScore": contribution_score, "status": "active"}
    return issue_vc(user_id, "TierCredential", details)
