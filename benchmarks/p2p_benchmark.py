import asyncio
import time
import numpy as np
import logging
from core.p2p_gossip import GossipP2P

# Configure logging to be quiet
logging.basicConfig(level=logging.ERROR)

class MockFVS:
    def __init__(self):
        self.vector_ids = ["vec_1", "vec_2"]
    def search(self, embedding, top_k):
        return [{"id": f"vec_{i}", "score": 0.9} for i in range(top_k)]

async def run_benchmark():
    num_nodes = 10
    base_port = 9000
    nodes = []

    print(f"--- Benchmarking P2P Gossip with {num_nodes} nodes ---")

    # 1. Initialize nodes
    for i in range(num_nodes):
        fvs = MockFVS()
        node = GossipP2P(f"node_{i}", base_port + i, fvs)
        nodes.append(node)
        asyncio.create_task(node.start())

    await asyncio.sleep(1) # Wait for servers to start

    # 2. Connect all to node 0
    node0 = nodes[0]
    for i in range(1, num_nodes):
        node0.add_bootstrap_peer(f"127.0.0.1:{base_port + i}")
        # Also make others aware of node 0 for symmetry if needed,
        # but for broadcast/query from node0, node0 knowing them is enough.
        nodes[i].add_bootstrap_peer(f"127.0.0.1:{base_port}")

    await asyncio.sleep(1)

    # 3. Benchmark Broadcast
    print("\n[1] Benchmarking Broadcast...")
    message = {"type": "test", "data": "hello"}

    start_time = time.time()
    await node0.broadcast(message)
    end_time = time.time()
    broadcast_duration = end_time - start_time
    print(f"Sequential Broadcast took: {broadcast_duration:.4f} seconds")

    # 4. Benchmark Query Peers
    print("\n[2] Benchmarking Query Peers...")
    query_emb = np.random.rand(384)

    start_time = time.time()
    results = await node0.query_peers(query_emb, top_k=5)
    end_time = time.time()
    query_duration = end_time - start_time
    print(f"Sequential Query Peers took: {query_duration:.4f} seconds")
    print(f"Results found: {len(results)}")

    # Cleanup
    # (In a real scenario we'd close the servers properly, but for a script exit is fine)
    print("\nBenchmark complete.")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
