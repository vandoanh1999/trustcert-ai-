import sys
from unittest.mock import MagicMock

# Mock heavy ML/Inference modules
mock_modules = [
    'torch',
    'faiss',
    'sentence_transformers',
    'llama_cpp',
    'transformers',
    'safetensors',
    'peft',
    'accelerate',
    'bitsandbytes'
]

for module in mock_modules:
    sys.modules[module] = MagicMock()

# Specific mocks for class structures if needed
import torch
torch.nn = MagicMock()
torch.Tensor = MagicMock()

import faiss
faiss.IndexFlatL2 = MagicMock()

print("✅ Heavy modules mocked successfully.")
