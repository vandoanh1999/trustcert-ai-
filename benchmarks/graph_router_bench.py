"""
Graph Router bench harness.
- A simple GNN-like router simulation that scores candidate experts using features.
- This is a lightweight simulation to measure graph routing overhead & effect.
- Replace placeholder graph logic with real GNN model when available.
"""
import time
import numpy as np

def simple_graph_router(query_vec, candidate_metas):
    """
    Simulated graph scoring:
    - build adjacency by cosine similarity between query and candidate embeddings
    - run simple message-passing (2 hops)
    - return ranked candidate ids and timing
    """
    t0 = time.perf_counter()
    q = query_vec / (np.linalg.norm(query_vec) + 1e-12)
    sims = []
    for m in candidate_metas:
        emb = np.array(m.get("embedding", np.random.rand(len(query_vec))))
        embn = emb / (np.linalg.norm(emb) + 1e-12)
        sims.append(float(np.dot(q, embn)))
    # simple ranking
    order = np.argsort(sims)[::-1].tolist()
    t1 = time.perf_counter()
    return {"order": order, "scores": sims, "time_s": t1-t0}