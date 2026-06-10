import time
import numpy as np
import os
import shutil
from core.fvs_storage import FaissVectorStore

def benchmark_fvs():
    node_id = "bench_node"
    data_dir = "./data/bench_fvs"
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)

    dim = 384
    fvs = FaissVectorStore(node_id, dimension=dim, data_dir=data_dir)

    # Benchmark Save
    n_save = 1000
    embeddings = np.random.rand(n_save, dim).astype('float32')

    print(f"Benchmarking save of {n_save} vectors...")
    start_time = time.time()
    for i in range(n_save):
        fvs.save(f"text_{i}", embeddings[i], vec_id=f"id_{i}")
    end_time = time.time()
    duration = end_time - start_time
    print(f"Saved {n_save} vectors in {duration:.4f}s ({n_save/duration:.2f} vectors/s)")

    # Benchmark Duplicate Check (part of save, but let's test specifically)
    print(f"Benchmarking duplicate checks for {n_save} existing vectors...")
    start_time = time.time()
    for i in range(n_save):
        fvs.save(f"text_{i}", embeddings[i], vec_id=f"id_{i}")
    end_time = time.time()
    duration = end_time - start_time
    print(f"Checked {n_save} duplicates in {duration:.4f}s ({n_save/duration:.2f} checks/s)")

    # Benchmark Search
    n_search = 100
    top_k = 100
    query = np.random.rand(dim).astype('float32')

    print(f"Benchmarking search (top_k={top_k}) {n_search} times...")
    start_time = time.time()
    for _ in range(n_search):
        fvs.search(query, top_k=top_k)
    end_time = time.time()
    duration = end_time - start_time
    print(f"Performed {n_search} searches in {duration:.4f}s ({n_search/duration:.2f} searches/s)")

    fvs.close()
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)

if __name__ == "__main__":
    benchmark_fvs()
