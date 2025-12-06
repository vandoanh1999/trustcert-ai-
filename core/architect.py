"""
Genesis Core V9: The Architect Governance Layer

This module defines the identity of the Architect, who holds ultimate
governance authority over the network.
"""
from Crypto.PublicKey import ECC

# --- Architect's Public Key ---
# This public key is a hardcoded part of the network's genesis configuration.
# Only messages signed by the corresponding private key will be accepted for
# critical, Architect-level actions.
ARCHITECT_PUBLIC_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEIIyIRCTLwR1oDl1aFwyOfSctF1lv
VJqtW2fXoPUCXvdrHxe/fioGe7k4UTOnLYcU3+QsWs++kFpRKVT7fwppeg==
-----END PUBLIC KEY-----"""

ARCHITECT_PUBLIC_KEY = ECC.import_key(ARCHITECT_PUBLIC_KEY_PEM)

def verify_architect_signature(message: bytes, signature: bytes) -> bool:
    """
    Verifies that a message was signed by the Architect's private key.
    """
    from core.security import verify_signature
    return verify_signature(ARCHITECT_PUBLIC_KEY, message, signature)
