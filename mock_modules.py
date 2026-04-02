import sys
from unittest.mock import MagicMock

class Mock(MagicMock):
    @classmethod
    def __getattr__(cls, name):
        return MagicMock()

mock_modules = [
    "torch",
    "torch.nn",
    "torch.optim",
    "faiss",
    "sentence_transformers",
    "llama_cpp",
    "transformers",
    "safetensors",
    "peft",
    "accelerate",
    "bitsandbytes",
    "sklearn",
    "sklearn.metrics"
]

for mod in mock_modules:
    sys.modules[mod] = Mock()
