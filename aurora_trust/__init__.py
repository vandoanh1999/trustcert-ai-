"""
Genesis Core V7: The Aurora Trust System

This module is the soul and ledger of the Symbiotic Network. It provides:
- A Reputation Engine to score and track the performance of expert adapters.
- A Verifiable Credential (VC) issuer to create immutable records of contributions.
- A Zero-Knowledge Proof (ZKP) system for verifying causal integrity.
"""

# V7 Update: The main reputation update logic is now driven by direct user feedback.
from .reputation_vc import get_reputation, update_reputation_with_feedback, issue_vc
from .zk_proofs import CausalEffectCircuit, zk_prove, zk_verify

__all__ = [
    "get_reputation",
    "update_reputation_with_feedback",
    "issue_vc",
    "CausalEffectCircuit",
    "zk_prove",
    "zk_verify",
]
