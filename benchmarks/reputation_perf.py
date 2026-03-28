
import time
import os
import sys
from unittest.mock import MagicMock

# Mock torch to avoid ImportError
sys.modules["torch"] = MagicMock()
sys.modules["torch.nn"] = MagicMock()

# Ensure we can import from the root
sys.path.append(os.getcwd())

from aurora_trust.reputation_vc import get_reputation, update_reputation_with_feedback

def benchmark_reputation(iterations=100):
    expert_id = "test_expert"

    start_time = time.time()
    for i in range(iterations):
        get_reputation(expert_id)
    read_duration = time.time() - start_time
    print(f"Read bottleneck ({iterations} iterations): {read_duration:.4f} seconds")

    start_time = time.time()
    for i in range(iterations):
        update_reputation_with_feedback(expert_id, 0.8)
    write_duration = time.time() - start_time
    print(f"Write bottleneck ({iterations} iterations): {write_duration:.4f} seconds")

if __name__ == "__main__":
    # Ensure files exist
    if not os.path.exists("aurora_reputation.json"):
        with open("aurora_reputation.json", "w") as f:
            f.write("{}")

    benchmark_reputation()
