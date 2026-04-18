"""
Genesis Core V9: Production-Grade Security Module (Rev 2)

This version uses the correct Sharer class for handling hex-based keys.
"""
import os
import uuid
import hashlib
import gc
from typing import List

from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

# V9 FIX: Use the hex-based sharer for cryptographic keys
from core.shamir import SecretSharer as SSS

class ThresholdSignature:
    def __init__(self, k: int, n: int):
        self.k = k
        self.n = n
        self.master_private_key = ECC.generate(curve='P-256')
        self.master_public_key = self.master_private_key.public_key()

        private_key_hex = self.master_private_key.d.to_bytes(32, 'big').hex()
        self.shares = SSS.split_secret(private_key_hex, k, n)
        print("[MPC] Master key generated and split into shares.")

    def get_shares(self) -> List[str]:
        return self.shares

    @staticmethod
    def combine_shares_and_sign(shares: List[str], message: bytes) -> bytes:
        private_key_hex = SSS.recover_secret(shares)
        # Ensure the hex string is 64 characters (32 bytes) long
        private_key_hex = private_key_hex.zfill(64)
        private_key_bytes = bytes.fromhex(private_key_hex)

        key = ECC.construct(curve='P-256', d=int.from_bytes(private_key_bytes, 'big'))

        h = SHA256.new(message)
        return DSS.new(key, 'fips-186-3').sign(h)

    def verify_master_signature(self, message: bytes, signature: bytes) -> bool:
        h = SHA256.new(message)
        verifier = DSS.new(self.master_public_key, 'fips-186-3')
        try:
            verifier.verify(h, signature)
            return True
        except ValueError:
            return False

# ... (rest of the file is unchanged) ...
def secure_wipe(data: bytearray): data[:] = b'\x00' * len(data)
def secure_delete(secret):
    if isinstance(secret, bytearray): secure_wipe(secret)
    del secret; gc.collect()
def get_hardware_fingerprint():
    mac = hex(uuid.getnode()); machine_id = "generic"
    try:
        with open("/etc/machine-id", "r") as f: machine_id = f.read().strip()
    except: pass
    fp_raw = f"genesis-node-{mac}-{machine_id}"
    return hashlib.sha256(fp_raw.encode()).hexdigest()
def generate_keys(fp):
    seed = hashlib.sha256(fp.encode()).digest()
    return ECC.generate(curve='P-256', randfunc=lambda n: seed[:n])
def sign_message(key, msg):
    h = SHA256.new(msg); return DSS.new(key, 'fips-186-3').sign(h)
def verify_signature(pub_key, msg, sig):
    h = SHA256.new(msg); verifier = DSS.new(pub_key, 'fips-186-3')
    try: verifier.verify(h, sig); return True
    except: return False
if __name__ == "__main__":
    print("--- Running V9 Security Module Self-Test (Rev 2) ---")
    print("\n[1] Testing Threshold Signature (MPC)...")
    k, n = 3, 5
    mpc_scheme = ThresholdSignature(k, n)
    shares = mpc_scheme.get_shares()
    message_to_sign = b"Authorize deployment of expert_geology_v2"
    quorum_shares = shares[:k]
    network_signature = mpc_scheme.combine_shares_and_sign(quorum_shares, message_to_sign)
    print("  - Quorum of nodes generated a network signature.")
    is_valid = mpc_scheme.verify_master_signature(message_to_sign, network_signature)
    assert is_valid
    print("  - Network signature verified successfully with master public key.")
    print("  - [PASS] Threshold Signature OK.")
    print("\n--- V9 Security Module Self-Test Passed! ---")
