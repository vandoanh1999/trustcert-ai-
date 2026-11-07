"""
Genesis Core: Security Module (Rev 3)

Rev 3 security fixes:
- Node keys are generated from a cryptographically secure RNG instead of being
  derived from the (guessable) hardware fingerprint. The fingerprint is kept
  only as a node identifier for the anti-Sybil check.
- ThresholdSignature is now a real k-of-n multi-signature: every signer keeps
  its own private key and the full key is never reassembled in one place.
  (Rev 2 split one master key with Shamir and recombined it to sign, so any
  quorum member saw the whole master key.)
"""
import gc
import hashlib
import os
import uuid
from typing import Dict, List, Optional, Sequence, Tuple

from Crypto.Hash import SHA256
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS

CURVE = "P-256"


# --------------------------------------------------------------------------- #
# k-of-n multi-signature
# --------------------------------------------------------------------------- #
class ThresholdSignature:
    """
    k-of-n multi-signature over ECDSA P-256.

    Each of the n signers holds an independent private key. A message is
    authorised when at least k *distinct* registered signers produced a valid
    signature over it. No secret is ever shared or recombined.

    Usage:
        scheme, private_keys = ThresholdSignature.generate(k=3, n=5)  # demo / tests
        sigs = {i: ThresholdSignature.sign_partial(private_keys[i], msg) for i in (0, 2, 4)}
        assert scheme.verify(msg, sigs)

    In production each signer runs ECC.generate() on its own machine and only
    publishes its public key; build the scheme with ThresholdSignature(k, public_keys).
    """

    def __init__(self, k: int, public_keys: Sequence[ECC.EccKey]):
        n = len(public_keys)
        if not 1 <= k <= n:
            raise ValueError(f"Threshold k must satisfy 1 <= k <= n (got k={k}, n={n}).")
        for pk in public_keys:
            if pk.has_private():
                raise ValueError("Pass public keys only; private keys must stay with their signers.")
        self.k = k
        self.n = n
        self.public_keys: List[ECC.EccKey] = list(public_keys)

    @classmethod
    def generate(cls, k: int, n: int) -> Tuple["ThresholdSignature", List[ECC.EccKey]]:
        """Creates n fresh signer keys (for local demos and tests)."""
        private_keys = [ECC.generate(curve=CURVE) for _ in range(n)]
        return cls(k, [sk.public_key() for sk in private_keys]), private_keys

    @staticmethod
    def sign_partial(private_key: ECC.EccKey, message: bytes) -> bytes:
        """One signer's contribution."""
        return sign_message(private_key, message)

    def verify(self, message: bytes, signatures: Dict[int, bytes]) -> bool:
        """True when >= k distinct signers (by index) produced valid signatures."""
        valid = 0
        for index, signature in signatures.items():
            if not isinstance(index, int) or not 0 <= index < self.n:
                continue
            if verify_signature(self.public_keys[index], message, signature):
                valid += 1
        return valid >= self.k


# --------------------------------------------------------------------------- #
# Memory hygiene
# --------------------------------------------------------------------------- #
def secure_wipe(data: bytearray) -> None:
    data[:] = b"\x00" * len(data)


def secure_delete(secret) -> None:
    if isinstance(secret, bytearray):
        secure_wipe(secret)
    del secret
    gc.collect()


# --------------------------------------------------------------------------- #
# Node identity
# --------------------------------------------------------------------------- #
def get_hardware_fingerprint() -> str:
    """
    Stable identifier of the host, used ONLY for anti-Sybil bookkeeping.
    It is derived from guessable data (MAC address, machine-id) and must never
    be used as key material.
    """
    mac = hex(uuid.getnode())
    machine_id = "generic"
    try:
        with open("/etc/machine-id", "r") as f:
            machine_id = f.read().strip()
    except OSError:
        pass
    return hashlib.sha256(f"genesis-node-{mac}-{machine_id}".encode()).hexdigest()


def generate_keys(fp: Optional[str] = None, key_path: Optional[str] = None) -> ECC.EccKey:
    """
    Returns the node's ECDSA private key.

    - The key comes from a cryptographically secure RNG. `fp` is accepted for
      backward compatibility and deliberately ignored (Rev 2 derived the key
      from the fingerprint, so anyone who knew the MAC address and machine-id
      could rebuild it).
    - If `key_path` is given, the key is loaded from it, or created and saved
      there with owner-only permissions (0600) so the node keeps its identity
      across restarts. Never commit that file.
    """
    del fp
    if key_path and os.path.exists(key_path):
        with open(key_path, "rt") as f:
            return ECC.import_key(f.read())

    key = ECC.generate(curve=CURVE)
    if key_path:
        fd = os.open(key_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wt") as f:
            f.write(key.export_key(format="PEM"))
    return key


def sign_message(key: ECC.EccKey, msg: bytes) -> bytes:
    return DSS.new(key, "fips-186-3").sign(SHA256.new(msg))


def verify_signature(pub_key: ECC.EccKey, msg: bytes, sig: bytes) -> bool:
    try:
        DSS.new(pub_key, "fips-186-3").verify(SHA256.new(msg), sig)
        return True
    except (ValueError, TypeError):
        return False


if __name__ == "__main__":
    print("--- Running Security Module Self-Test (Rev 3) ---")
    msg = b"Authorize deployment of expert_geology_v2"

    print("\n[1] k-of-n multi-signature (3 of 5)...")
    scheme, keys = ThresholdSignature.generate(k=3, n=5)
    quorum = {i: ThresholdSignature.sign_partial(keys[i], msg) for i in (0, 2, 4)}
    assert scheme.verify(msg, quorum), "quorum of 3 must pass"
    assert not scheme.verify(msg, {0: quorum[0], 2: quorum[2]}), "2 signatures must fail"
    assert not scheme.verify(b"tampered", quorum), "tampered message must fail"
    print("  - [PASS] 3 valid signatures accepted, 2 rejected, tampering rejected.")

    print("\n[2] Node keys are random, not derived from the fingerprint...")
    fp = get_hardware_fingerprint()
    assert generate_keys(fp).d != generate_keys(fp).d
    print("  - [PASS] Same fingerprint -> different keys.")

    print("\n--- Security Module Self-Test Passed! ---")
