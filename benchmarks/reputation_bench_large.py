import time
import os
import json
from aurora_trust.reputation_vc import update_reputation_with_feedback, REP_DB_PATH

def benchmark_reputation_update(iterations=1000, num_experts=5000):
    # Create a larger database to simulate growth
    initial_db = {f"expert_{i}": 0.5 for i in range(num_experts)}
    with open(REP_DB_PATH, "w") as f:
        json.dump(initial_db, f)

    # Force cache reset if it exists (not easy without modifying the module or restarting)
    # But since we're running as a new process, cache is initially None.

    start_time = time.time()
    for i in range(iterations):
        expert_id = f"expert_{i % num_experts}"
        update_reputation_with_feedback(expert_id, 0.8)
    end_time = time.time()

    duration = end_time - start_time
    print(f"Updated reputation {iterations} times with {num_experts} experts in {duration:.4f} seconds.")
    print(f"Average time per update: {duration/iterations:.6f} seconds.")

if __name__ == "__main__":
    benchmark_reputation_update()
