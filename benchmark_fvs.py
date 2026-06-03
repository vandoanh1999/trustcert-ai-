import time
import numpy as np
from core.fvs_storage import FaissVectorStore
import os
import shutil

def benchmark_fvs():
    node_id = "test_node_bolt"
    dimension = 384
    num_vectors = 1000
    top_k = 100

    # Clean up previous data
    if os.path.exists(f"./data/fvs/{node_id}"):
        shutil.rmtree(f"./data/fvs/{node_id}")

    fvs = FaissVectorStore(node_id=node_id, dimension=dimension)

    # Ingest data
    print(f"Ingesting {num_vectors} vectors...")
    start_time = time.time()
    for i in range(num_vectors):
        text = f"This is document number {i}"
        embedding = np.random.rand(dimension).astype('float32')
        fvs.save(text, embedding)
    ingest_time = time.time() - start_time
    print(f"Ingestion took {ingest_time:.2f}s ({num_vectors/ingest_time:.2f} vectors/s)")

    # Benchmark search
    num_searches = 100
    print(f"Performing {num_searches} searches (top_k={top_k})...")
    query_embeddings = [np.random.rand(dimension).astype('float32') for _ in range(num_searches)]

    start_time = time.time()
    for q in query_embeddings:
        fvs.search(q, top_k=top_k)
    search_time = time.time() - start_time
    print(f"Search took {search_time:.2f}s ({num_searches/search_time:.2f} searches/s)")

    fvs.close()
    # Cleanup
    shutil.rmtree(f"./data/fvs/{node_id}")

if __name__ == "__main__":
    benchmark_fvs()
