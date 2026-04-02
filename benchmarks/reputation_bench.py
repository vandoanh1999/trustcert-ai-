
import mock_modules
import time
import os
import json
from aurora_trust.reputation_vc import get_reputation, update_reputation_with_feedback

def benchmark():
    expert_id = "test_expert"
    iterations = 1000

    print(f"Running benchmark with {iterations} iterations...")

    # Warm up
    get_reputation(expert_id)

    start_time = time.perf_counter()
    for i in range(iterations):
        get_reputation(expert_id)
    read_duration = time.perf_counter() - start_time
    print(f"Read performance: {read_duration/iterations:.9f} s/op")

    start_time = time.perf_counter()
    for i in range(iterations):
        update_reputation_with_feedback(expert_id, 0.8)
    write_duration = time.perf_counter() - start_time
    print(f"Write performance: {write_duration/iterations:.9f} s/op")

if __name__ == "__main__":
    benchmark()
