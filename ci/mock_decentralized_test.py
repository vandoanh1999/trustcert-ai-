
import sys
from unittest.mock import MagicMock

# Mock out heavy ML/hardware dependencies for simulation tests
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

for mod in mock_modules:
    sys.modules[mod] = MagicMock()

# Now run the actual test
import asyncio
import ci.v8_decentralized_test as test_module

if __name__ == "__main__":
    asyncio.run(test_module.main())
