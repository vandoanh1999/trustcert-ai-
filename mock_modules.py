import sys
from unittest.mock import MagicMock

class MockModule(MagicMock):
    @classmethod
    def __getattr__(cls, name):
        return MagicMock()

# List of heavy ML modules to mock
modules_to_mock = [
    "torch", "faiss", "sentence_transformers", "llama_cpp",
    "transformers", "safetensors", "peft", "accelerate",
    "bitsandbytes", "sklearn", "Crypto", "Crypto.PublicKey",
    "Crypto.Signature", "Crypto.Hash"
]

for mod in modules_to_mock:
    sys.modules[mod] = MockModule()

# Specific mocks for Crypto
from unittest.mock import MagicMock
sys.modules["Crypto.PublicKey.ECC"] = MagicMock()
sys.modules["Crypto.Signature.DSS"] = MagicMock()
sys.modules["Crypto.Hash.SHA256"] = MagicMock()
