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

# --- In-Memory Cache (Bolt ⚡ Optimization) ---
_REPUTATION_CACHE = None
_VC_CACHE = None

# --- Reputation Management ---

def load_reputation_db() -> Dict[str, float]:
    """Loads reputation DB, using in-memory cache if available (Bolt ⚡)."""
    global _REPUTATION_CACHE
    # Check mtime to invalidate cache if another process updated the file
    try:
        current_mtime = os.path.getmtime(REP_DB_PATH)
    except OSError:
        current_mtime = 0

    if _REPUTATION_CACHE is not None and _REPUTATION_CACHE.get("_mtime") == current_mtime:
        return _REPUTATION_CACHE["data"].copy()

    if os.path.exists(REP_DB_PATH):
        with open(REP_DB_PATH, "r") as f:
            try:
                data = json.load(f)
                _REPUTATION_CACHE = {"data": data, "_mtime": current_mtime}
                return data.copy()
            except json.JSONDecodeError: return {}
    return {}

def save_reputation_db(db: Dict[str, float]):
    """Saves reputation DB to disk and updates in-memory cache (Bolt ⚡)."""
    global _REPUTATION_CACHE
    with open(REP_DB_PATH, "w") as f:
        json.dump(db, f, indent=2)
    try:
        new_mtime = os.path.getmtime(REP_DB_PATH)
    except OSError:
        new_mtime = 0
    _REPUTATION_CACHE = {"data": db.copy(), "_mtime": new_mtime}

def get_reputation(expert_id: str) -> float:
    db = load_reputation_db()
    return float(db.get(expert_id, 0.5))

def update_reputation_with_feedback(expert_id: str, feedback_score: float) -> float:
    """Updates reputation score, minimizing DB loads via cache (Bolt ⚡)."""
    db = load_reputation_db()
    old_score = float(db.get(expert_id, 0.5))
    clamped_feedback = max(0.0, min(1.0, feedback_score))
    new_score = (1 - REPUTATION_EMA_LEARNING_RATE) * old_score + REPUTATION_EMA_LEARNING_RATE * clamped_feedback
    db[expert_id] = new_score
    save_reputation_db(db)
    return new_score

# --- Verifiable Credential (VC) Management ---

def sign_payload_hmac(payload: bytes) -> str:
    return hmac.new(VC_SIGNING_KEY, payload, digestmod=hashlib.sha256).hexdigest()

def issue_vc(subject_id: str, credential_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
    """Issues a VC, using in-memory cache with mtime-based validation (Bolt ⚡)."""
    global _VC_CACHE
    vc = {
        "issuer": "aurora_trust_engine_v8",
        "issuanceDate": int(time.time()),
        "type": credential_type,
        "credentialSubject": { "id": subject_id, **details }
    }
    payload = json.dumps(vc, sort_keys=True).encode("utf8")
    signature = sign_payload_hmac(payload)
    vc_obj = {"credential": vc, "proof": {"type": "HmacSha256", "signature": signature}}

    try:
        current_mtime = os.path.getmtime(VC_STORE_PATH)
    except OSError:
        current_mtime = 0

    if _VC_CACHE is not None and _VC_CACHE.get("_mtime") == current_mtime:
        store = _VC_CACHE["data"]
    else:
        store = []
        if os.path.exists(VC_STORE_PATH):
            with open(VC_STORE_PATH, "r") as f:
                try: store = json.load(f)
                except: store = []

    store.append(vc_obj)
    with open(VC_STORE_PATH, "w") as f:
        json.dump(store, f, indent=2)

    try:
        new_mtime = os.path.getmtime(VC_STORE_PATH)
    except OSError:
        new_mtime = 0
    _VC_CACHE = {"data": store, "_mtime": new_mtime}
    return vc_obj

def issue_tier_credential(user_id: str, tier: str, contribution_score: float) -> Dict[str, Any]:
    details = {"tier": tier, "achievedWithContributionScore": contribution_score, "status": "active"}
    return issue_vc(user_id, "TierCredential", details)
