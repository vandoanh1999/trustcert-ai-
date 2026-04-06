
import asyncio
import time
import numpy as np
import json
from typing import Dict
from core.p2p_gossip import GossipP2P

class MockFVS:
    def __init__(self):
        self.vector_ids = ["vec1", "vec2"]
    def search(self, embedding, top_k):
        return [{"id": "vec1", "score": 0.9}]

async def run_benchmark():
    LATENCY = 0.1 # 100ms
    NUM_PEERS = 4

    print(f"--- P2P Latency Benchmark (Simulated {LATENCY*1000}ms network latency) ---")

    # Setup peers
    nodes = []
    for i in range(NUM_PEERS):
        node = GossipP2P(f"node_{i}", 8000 + i, fvs_store=MockFVS())

        # Inject artificial latency into the communication methods
        original_send = node.send_to_peer
        async def delayed_send(peer, message, orig=original_send):
            await asyncio.sleep(LATENCY)
            return await orig(peer, message)
        node.send_to_peer = delayed_send

        original_send_wait = node.send_and_wait
        async def delayed_send_wait(peer, message, timeout=10, orig=original_send_wait):
            await asyncio.sleep(LATENCY)
            return await orig(peer, message, timeout=timeout)
        node.send_and_wait = delayed_send_wait

        nodes.append(node)

    # Connect all-to-all
    for i in range(NUM_PEERS):
        for j in range(NUM_PEERS):
            if i != j:
                nodes[i].add_bootstrap_peer(f"127.0.0.1:{8000 + j}")

    # Start servers
    tasks = [asyncio.create_task(node.start()) for node in nodes]
    await asyncio.sleep(1) # Wait for servers to start

    print(f"Testing with {NUM_PEERS-1} target peers...")

    # Measure broadcast latency
    start_time = time.time()
    await nodes[0].broadcast({"type": "test", "data": "hello"})
    end_time = time.time()
    broadcast_latency = end_time - start_time
    print(f"Broadcast latency: {broadcast_latency:.4f}s")

    # Measure query latency
    query_embedding = np.random.rand(384)
    start_time = time.time()
    results = await nodes[0].query_peers(query_embedding)
    end_time = time.time()
    query_latency = end_time - start_time
    print(f"Query latency: {query_latency:.4f}s")

    # Expected sequential latency: (NUM_PEERS - 1) * LATENCY
    expected_sequential = (NUM_PEERS - 1) * LATENCY
    print(f"Theoretical sequential latency: ~{expected_sequential:.4f}s")
    print(f"Theoretical parallel latency: ~{LATENCY:.4f}s")

    # Stop tasks
    for task in tasks:
        task.cancel()

if __name__ == "__main__":
    asyncio.run(run_benchmark())
