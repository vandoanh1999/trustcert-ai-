
import time
import numpy as np
from core.fvs_storage import FaissVectorStore
import os
import shutil

def benchmark():
    node_id = "bench_node"
    dimension = 384
    data_dir = "./data/bench_fvs"

    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)

    fvs = FaissVectorStore(node_id, dimension=dimension, data_dir=data_dir)

    # 1. Benchmark Save (O(N) check)
    num_vectors = 5000
    embeddings = np.random.random((num_vectors, dimension)).astype('float32')

    print(f"--- Benchmarking Save ({num_vectors} vectors) ---")
    start_time = time.time()
    for i in range(num_vectors):
        fvs.save(f"text_{i}", embeddings[i])
    end_time = time.time()
    print(f"Saved {num_vectors} vectors in {end_time - start_time:.4f}s ({num_vectors/(end_time - start_time):.2f} vectors/s)")

    # 2. Benchmark Duplicate Check (O(N) in List)
    print(f"--- Benchmarking Duplicate Check ({num_vectors} checks) ---")
    start_time = time.time()
    for i in range(num_vectors):
        fvs.save(f"text_{i}", embeddings[i])
    end_time = time.time()
    print(f"Checked {num_vectors} duplicates in {end_time - start_time:.4f}s ({num_vectors/(end_time - start_time):.2f} checks/s)")

    # 3. Benchmark Search (N+1 SQL queries)
    num_queries = 100
    top_k = 100
    query_embeddings = np.random.random((num_queries, dimension)).astype('float32')

    print(f"--- Benchmarking Search ({num_queries} queries, top_k={top_k}) ---")
    start_time = time.time()
    for i in range(num_queries):
        fvs.search(query_embeddings[i], top_k=top_k)
    end_time = time.time()
    print(f"Performed {num_queries} searches in {end_time - start_time:.4f}s ({num_queries/(end_time - start_time):.2f} searches/s)")

    fvs.close()
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)

if __name__ == "__main__":
    benchmark()
