import sys
from unittest.mock import MagicMock

def mock_modules():
    mock_torch = MagicMock()
    mock_torch.nn = MagicMock()
    mock_torch.tensor = MagicMock()
    sys.modules["torch"] = mock_torch

    mock_faiss = MagicMock()
    sys.modules["faiss"] = mock_faiss

    mock_st = MagicMock()
    sys.modules["sentence_transformers"] = mock_st

    print("--- Heavy ML dependencies mocked ---")

if __name__ == "__main__":
    mock_modules()
