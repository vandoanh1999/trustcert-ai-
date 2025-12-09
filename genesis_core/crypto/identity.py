import os
from secp256k1 import PrivateKey, PublicKey

class NodeIdentity:
    """
    Manages the cryptographic identity of a P2P node.
    """
    def __init__(self, private_key_path: str = "node_private_key.pem"):
        self.private_key_path = private_key_path
        self.private_key = self._load_or_create_private_key()
        self.public_key = self.private_key.pubkey

    def _load_or_create_private_key(self) -> PrivateKey:
        """
        Loads the private key from the specified path, or creates a new one
        if it doesn't exist.
        """
        if os.path.exists(self.private_key_path):
            with open(self.private_key_path, "rb") as f:
                privkey_bytes = f.read()
            # The key is stored as a hex string, so we must pass raw=False
            return PrivateKey(privkey_bytes, raw=False)
        else:
            privkey = PrivateKey()
            with open(self.private_key_path, "wb") as f:
                # The serialize() method returns a string, so we must encode it to bytes
                f.write(privkey.serialize().encode('utf-8'))
            return privkey

    def sign(self, message: bytes) -> bytes:
        """
        Signs a message with the node's private key.
        """
        return self.private_key.ecdsa_sign(message)

    def verify(self, signature: bytes, message: bytes, public_key: PublicKey) -> bool:
        """
        Verifies a signature with a given public key.
        """
        return public_key.ecdsa_verify(signature, message)

    @property
    def peer_id(self) -> str:
        """
        Returns the node's peer ID, derived from its public key.
        """
        # A simple representation for now. In a real system, this would
        # likely be a multihash of the public key.
        return self.public_key.serialize(compressed=True).hex()
