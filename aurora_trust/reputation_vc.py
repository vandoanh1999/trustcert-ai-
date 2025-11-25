"""
Aurora Trust: Reputation and Verifiable Credentials Engine

This module manages the reputation of expert adapters and issues
Verifiable Credentials (VCs) to record their contributions.
"""
import json
import time
import os
import hashlib
import hmac
from typing import Dict, Any, List
import torch

# Constants
REP_DB_PATH = "aurora_reputation.json"
VC_STORE_PATH = "aurora_vc_store.json"
VC_SIGNING_KEY = b"genesis_v6_aurora_secret_key" # Should be loaded securely in production

# --- Reputation Management ---

def load_reputation_db() -> Dict[str, float]:
    """Loads the reputation database from a local JSON file."""
    if os.path.exists(REP_DB_PATH):
        with open(REP_DB_PATH, "r") as f:
            return json.load(f)
    return {}

def save_reputation_db(db: Dict[str, float]):
    """Saves the reputation database to a local JSON file."""
    with open(REP_DB_PATH, "w") as f:
        json.dump(db, f, indent=2)

def get_reputation(expert_id: str) -> float:
    """Gets the reputation score for a given expert, defaulting to 0.5."""
    db = load_reputation_db()
    return float(db.get(expert_id, 0.5))

def update_reputation(expert_id: str, delta: float) -> float:
    """Updates an expert's reputation, clamping the score between 0.0 and 1.0."""
    db = load_reputation_db()
    db.setdefault(expert_id, 0.5)
    db[expert_id] = float(max(0.0, min(1.0, db[expert_id] + delta)))
    save_reputation_db(db)
    return db[expert_id]

# --- Verifiable Credential (VC) Management ---

def sign_payload_hmac(payload: bytes) -> str:
    """Signs a payload using HMAC-SHA256."""
    return hmac.new(VC_SIGNING_KEY, payload, digestmod=hashlib.sha256).hexdigest()

def issue_vc(expert_id: str, contribution: float, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Creates a Verifiable Credential (VC) for an expert's contribution."""
    vc = {
        "issuer": "aurora_trust_engine",
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

    # Persist the VC to a local store (simulating a ledger)
    store = []
    if os.path.exists(VC_STORE_PATH):
        with open(VC_STORE_PATH, "r") as f:
            store = json.load(f)
    store.append(vc_obj)
    with open(VC_STORE_PATH, "w") as f:
        json.dump(store, f, indent=2)

    return vc_obj

# --- Contribution Calculation and Issuance ---

def compute_and_issue_contributions(
    candidate_ids: List[str],
    alphas: torch.Tensor,
    aurora_loss_components: Dict[str, float]
) -> List[Dict[str, Any]]:
    """
    Computes the contribution of each candidate based on their weight (alpha)
    and the overall performance (loss components), then issues VCs and updates reputation.
    """
    results = []

    # Normalize losses/regs to a [0, 1] range where 0 is best
    loss_ci_norm = float(max(0.0, min(1.0, aurora_loss_components.get("loss_ci", 0.0))))
    tda_reg_norm = float(max(0.0, min(1.0, aurora_loss_components.get("tda_reg", 0.0))))

    # The "goodness" is the inverse of the error
    performance_factor = (1.0 - loss_ci_norm) * (1.0 - tda_reg_norm)

    alphas_np = alphas.detach().cpu().numpy()

    for i, expert_id in enumerate(candidate_ids):
        # Contribution is this expert's weight * the overall performance
        contribution_score = float(alphas_np[i] * performance_factor)

        vc = issue_vc(expert_id, contribution_score, aurora_loss_components)

        # Reputation delta is a small fraction of the contribution to avoid wild swings
        # Positive contribution increases reputation, negative (not possible here) would decrease
        rep_delta = contribution_score * 0.05
        new_reputation = update_reputation(expert_id, delta=rep_delta)

        results.append({
            "expert_id": expert_id,
            "contribution_score": contribution_score,
            "new_reputation": new_reputation,
            "verifiable_credential": vc,
        })
    return results
