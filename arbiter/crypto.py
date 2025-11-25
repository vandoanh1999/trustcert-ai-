"""
ASA-Fusion v2.0 - Quantum-Resistant Cryptography
SHA3-256 based certificate generation and validation.

This code is integrated from the Trustcert-ai project.
"""

import hashlib
import json
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

# --- Custom Exceptions for the Arbiter ---
class CertificateError(Exception):
    """Base exception for certificate errors."""
    pass

class ValidationError(ValueError):
    """Exception for data validation errors."""
    pass


@dataclass
class Certificate:
    """Quantum-resistant certificate using SHA3-256."""
    data_hash: str  # Hash of the data, not the data itself for privacy
    timestamp: float
    signature: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert certificate to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert certificate to JSON string."""
        return json.dumps(self.to_dict())


class SHA3CertificateManager:
    """Manages quantum-resistant SHA3-256 certificates for AI responses."""

    def __init__(self, salt: Optional[str] = "GENESIS-V5-ARBITER"):
        self.salt = salt

    @staticmethod
    def hash_data(data: str) -> str:
        """Hashes the input data using SHA3-256."""
        if not data:
            raise ValidationError("Data to be hashed cannot be empty.")
        return hashlib.sha3_256(data.encode('utf-8')).hexdigest()

    def generate_signature(self, data_hash: str, timestamp: float) -> str:
        """Generate SHA3-256 signature for the data hash."""
        if not data_hash:
            raise ValidationError("Data hash cannot be empty for signature generation.")

        combined = f"{data_hash}|{timestamp}|{self.salt}".encode('utf-8')
        return hashlib.sha3_256(combined).hexdigest()

    def create_certificate(self, data: str, metadata: Optional[Dict[str, Any]] = None) -> Certificate:
        """
        Create a new quantum-resistant certificate for a piece of data (e.g., an AI's response).
        The certificate is based on the hash of the data.
        """
        data_hash = self.hash_data(data)
        timestamp = time.time()
        signature = self.generate_signature(data_hash, timestamp)

        return Certificate(
            data_hash=data_hash,
            timestamp=timestamp,
            signature=signature,
            metadata=metadata or {}
        )

    def verify_certificate(self, cert: Certificate, original_data: str) -> bool:
        """Verify the certificate against the original data."""
        if not isinstance(cert, Certificate) or not cert.signature:
            raise CertificateError("Invalid certificate object provided.")

        # 1. Verify the data hash
        expected_data_hash = self.hash_data(original_data)
        if expected_data_hash != cert.data_hash:
            print("Data hash mismatch. The data may have been tampered with.")
            return False

        # 2. Verify the signature
        expected_signature = self.generate_signature(cert.data_hash, cert.timestamp)
        if expected_signature != cert.signature:
            print("Signature mismatch. The certificate is invalid.")
            return False

        return True
