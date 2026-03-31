
import asyncio
import time
import numpy as np
from core.p2p_gossip import GossipP2P

class MockFVS:
    def __init__(self):
        self.vector_ids = []
    def search(self, embedding, top_k):
        return [{"id": f"vec_{i}", "score": 0.9} for i in range(top_k)]

async def run_benchmark():
    print("Starting P2P Latency Benchmark...")

    # Setup 5 nodes
    nodes = []
    for i in range(5):
        node = GossipP2P(f"node_{i}", 8000 + i, fvs_store=MockFVS())
        nodes.append(node)

    # Start nodes
    tasks = [asyncio.create_task(node.start()) for node in nodes]
    await asyncio.sleep(1) # Give them time to start

    # Connect nodes in a star pattern (node 0 connected to all others)
    for i in range(1, 5):
        nodes[0].add_bootstrap_peer(f"127.0.0.1:{8000 + i}")

    # Inject artificial delay into send_to_peer and send_and_wait to simulate network latency
    original_send_to_peer = GossipP2P.send_to_peer
    async def delayed_send_to_peer(self, peer, message):
        await asyncio.sleep(0.1) # 100ms latency
        return await original_send_to_peer(self, peer, message)

    original_send_and_wait = GossipP2P.send_and_wait
    async def delayed_send_and_wait(self, peer, message, timeout=10):
        await asyncio.sleep(0.1) # 100ms latency
        return await original_send_and_wait(self, peer, message, timeout)

    GossipP2P.send_to_peer = delayed_send_to_peer
    GossipP2P.send_and_wait = delayed_send_and_wait

    print(f"Benchmarking broadcast to {len(nodes[0].peers)} peers...")
    start_time = time.time()
    await nodes[0].broadcast({"type": "test"})
    broadcast_duration = time.time() - start_time
    print(f"Broadcast duration: {broadcast_duration:.4f}s")

    print(f"Benchmarking query_peers to {len(nodes[0].peers)} peers...")
    query_embedding = np.random.random(384)
    start_time = time.time()
    await nodes[0].query_peers(query_embedding)
    query_duration = time.time() - start_time
    print(f"Query duration: {query_duration:.4f}s")

    # Cleanup
    for task in tasks:
        task.cancel()

    return broadcast_duration, query_duration

if __name__ == "__main__":
    asyncio.run(run_benchmark())
