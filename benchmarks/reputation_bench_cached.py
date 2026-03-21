import time
import os
import json
import sys

# Baseline without caching:
# In each update_reputation_with_feedback:
# 1. get_reputation calls load_reputation_db() -> 1 open/read/json.load
# 2. update_reputation_with_feedback calls load_reputation_db() -> 1 open/read/json.load
# 3. update_reputation_with_feedback calls save_reputation_db() -> 1 open/write/json.dump

# With caching:
# In each update_reputation_with_feedback:
# 1. get_reputation calls load_reputation_db() -> Returns from cache (fast)
# 2. update_reputation_with_feedback calls load_reputation_db() -> Returns from cache (fast)
# 3. update_reputation_with_feedback calls save_reputation_db() -> 1 open/write/json.dump AND updates cache

# For 1000 iterations:
# Baseline: 2000 reads, 1000 writes
# Cached: 0 reads (after first), 1000 writes

import aurora_trust.reputation_vc as rep_vc
from aurora_trust.reputation_vc import update_reputation_with_feedback, REP_DB_PATH

def benchmark_reputation_update_no_write(iterations=1000, num_experts=5000):
    # Create a larger database
    initial_db = {f"expert_{i}": 0.5 for i in range(num_experts)}
    with open(REP_DB_PATH, "w") as f:
        json.dump(initial_db, f)

    # Mocking save_reputation_db to only update cache, so we measure reading performance
    original_save = rep_vc.save_reputation_db
    rep_vc.save_reputation_db = lambda db: setattr(rep_vc, '_REP_CACHE', db)

    start_time = time.time()
    for i in range(iterations):
        expert_id = f"expert_{i % num_experts}"
        update_reputation_with_feedback(expert_id, 0.8)
    end_time = time.time()

    duration = end_time - start_time
    print(f"Updated (no write) reputation {iterations} times with {num_experts} experts in {duration:.4f} seconds.")
    print(f"Average time per update (cached reads): {duration/iterations:.6f} seconds.")

    # Restore
    rep_vc.save_reputation_db = original_save

if __name__ == "__main__":
    benchmark_reputation_update_no_write()
