
import sys
import runpy
from unittest.mock import MagicMock

# List of heavy dependencies to mock
MOCK_MODULES = [
    "torch", "faiss", "sentence_transformers", "transformers",
    "peft", "accelerate", "bitsandbytes", "llama_cpp"
]

for mod in MOCK_MODULES:
    sys.modules[mod] = MagicMock()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_mocked.py <script_path> [args...]")
        sys.exit(1)

    script_path = sys.argv[1]
    sys.argv = sys.argv[1:]
    runpy.run_path(script_path, run_name="__main__")
