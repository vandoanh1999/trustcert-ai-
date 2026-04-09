
import time
import os
import sys
from unittest.mock import MagicMock

# Mock heavy dependencies
sys.modules["torch"] = MagicMock()
sys.modules["torch.nn"] = MagicMock()
sys.modules["numpy"] = MagicMock()
sys.modules["faiss"] = MagicMock()
sys.modules["sentence_transformers"] = MagicMock()
sys.modules["llama_cpp"] = MagicMock()

# Ensure we can import from the root
sys.path.append(os.getcwd())

from aurora_trust.reputation_vc import get_reputation

def benchmark():
    expert_id = "dummy_adapters/expert_A/adapter_model.bin"
    iterations = 100000

    # Pre-warm
    _ = get_reputation(expert_id)

    start_time = time.perf_counter()
    for _ in range(iterations):
        _ = get_reputation(expert_id)
    end_time = time.perf_counter()

    total_time = end_time - start_time
    print(f"Total time for {iterations} calls: {total_time:.4f} seconds")
    print(f"Average time per call: {total_time/iterations:.6f} seconds")

if __name__ == "__main__":
    benchmark()
