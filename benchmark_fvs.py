
import time
import numpy as np
import os
import shutil
from core.fvs_storage import FaissVectorStore

def benchmark_fvs():
    node_id = "bench_node"
    dimension = 384
    num_vectors = 1000

    if os.path.exists(f"./data/fvs/{node_id}"):
        shutil.rmtree(f"./data/fvs/{node_id}")

    fvs = FaissVectorStore(node_id, dimension=dimension)

    # 1. Benchmark Save (Duplicate Check & Insert)
    print(f"Benchmarking Save of {num_vectors} vectors...")
    embeddings = np.random.rand(num_vectors, dimension).astype('float32')

    start_time = time.time()
    for i in range(num_vectors):
        fvs.save(f"text_{i}", embeddings[i], vec_id=f"id_{i}")
    end_time = time.time()
    print(f"Save Time: {end_time - start_time:.4f}s ({num_vectors / (end_time - start_time):.2f} vectors/s)")

    # Benchmark Duplicate Check
    print("Benchmarking Duplicate Check...")
    start_time = time.time()
    for i in range(num_vectors):
        fvs.save(f"text_{i}", embeddings[i], vec_id=f"id_{i}")
    end_time = time.time()
    print(f"Duplicate Check Time: {end_time - start_time:.4f}s ({num_vectors / (end_time - start_time):.2f} checks/s)")

    # 2. Benchmark Search (N+1 query)
    num_searches = 100
    top_k = 100
    query_embeddings = np.random.rand(num_searches, dimension).astype('float32')

    print(f"Benchmarking Search (top_k={top_k}) over {num_searches} queries...")
    start_time = time.time()
    for i in range(num_searches):
        fvs.search(query_embeddings[i], top_k=top_k)
    end_time = time.time()
    print(f"Search Time: {end_time - start_time:.4f}s ({num_searches / (end_time - start_time):.2f} searches/s)")

    fvs.close()
    shutil.rmtree(f"./data/fvs/{node_id}")

if __name__ == "__main__":
    benchmark_fvs()
