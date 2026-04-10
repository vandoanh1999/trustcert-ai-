import sys
from unittest.mock import MagicMock

# Mock heavy ML/ZK modules
mock_torch = MagicMock()
mock_torch.tensor = lambda x, **kwargs: x
sys.modules['torch'] = mock_torch

mock_faiss = MagicMock()
sys.modules['faiss'] = mock_faiss

mock_sentence_transformers = MagicMock()
sys.modules['sentence_transformers'] = mock_sentence_transformers

mock_llama_cpp = MagicMock()
sys.modules['llama_cpp'] = mock_llama_cpp

print("Heavily mocked modules for testing environment.")
