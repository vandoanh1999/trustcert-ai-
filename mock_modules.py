import sys
from unittest.mock import MagicMock

class MockModule(MagicMock):
    @classmethod
    def __getattr__(cls, name):
        return MagicMock()

# Mocking heavy/missing dependencies for CI
sys.modules["torch"] = MockModule()
sys.modules["torch.nn"] = MockModule()
sys.modules["faiss"] = MockModule()
sys.modules["sentence_transformers"] = MockModule()
sys.modules["llama_cpp"] = MockModule()
