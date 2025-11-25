"""
Genesis Core V6: The Aurora Trust System

This module is the soul and ledger of the Sentient Forge. It provides:
- A Reputation Engine to score and track the performance of expert adapters.
- A Verifiable Credential (VC) issuer to create immutable records of contributions.
- A Zero-Knowledge Proof (ZKP) system for verifying causal integrity.
"""

from .reputation_vc import get_reputation, update_reputation, compute_and_issue_contributions
from .zk_proofs import CausalEffectCircuit, zk_prove, zk_verify, compute_zk_penalty

__all__ = [
    "get_reputation",
    "update_reputation",
    "compute_and_issue_contributions",
    "CausalEffectCircuit",
    "zk_prove",
    "zk_verify",
    "compute_zk_penalty"
]
