
import asyncio
import time
import numpy as np
from core.p2p_gossip import GossipP2P

class MockFVS:
    def __init__(self):
        self.vector_ids = ["vec1", "vec2"]
    def search(self, embedding, top_k):
        return [{"id": "vec1", "score": 0.9}]

async def main():
    print("--- P2P Parallelization Benchmark ---")

    # Setup 10 mock nodes
    num_peers = 10
    nodes = []
    for i in range(num_peers + 1):
        node = GossipP2P(f"node_{i}", 9000 + i, fvs_store=MockFVS())
        nodes.append(node)

    # Start all nodes
    server_tasks = []
    for node in nodes:
        # We don't actually need to run the full server for this benchmark if we mock network latency,
        # but the current implementation uses real network calls.
        # To avoid actual port binding issues and focus on the logic,
        # let's mock 'send_to_peer' and 'send_and_wait' to simulate latency.
        pass

    main_node = nodes[0]
    for i in range(1, num_peers + 1):
        main_node.add_bootstrap_peer(f"127.0.0.1:{9000+i}")

    # Simulated latency (ms)
    LATENCY = 0.1

    async def mocked_send_to_peer(peer, message):
        await asyncio.sleep(LATENCY)
        return True

    async def mocked_send_and_wait(peer, message, timeout=10):
        await asyncio.sleep(LATENCY)
        return {"type": "query_response", "results": [{"id": f"res_{peer}", "score": 0.8}]}

    main_node.send_to_peer = mocked_send_to_peer
    main_node.send_and_wait = mocked_send_and_wait

    print(f"Benchmarking with {num_peers} peers and {LATENCY*1000}ms simulated latency per call...")

    # Test Broadcast
    start = time.perf_counter()
    await main_node.broadcast({"type": "test"})
    broadcast_time = time.perf_counter() - start
    print(f"Broadcast time: {broadcast_time:.4f}s")

    # Test Query
    start = time.perf_counter()
    results = await main_node.query_peers(np.random.rand(384), top_k=5)
    query_time = time.perf_counter() - start
    print(f"Query time: {query_time:.4f}s")
    print(f"Results found: {len(results)}")

    expected_sequential_time = num_peers * LATENCY
    speedup_broadcast = expected_sequential_time / broadcast_time
    speedup_query = expected_sequential_time / query_time

    print(f"\nEstimated Speedup (vs Sequential {expected_sequential_time:.4f}s):")
    print(f"Broadcast: {speedup_broadcast:.2f}x")
    print(f"Query: {speedup_query:.2f}x")

    if broadcast_time < expected_sequential_time and query_time < expected_sequential_time:
        print("\n[PASS] Parallelization confirmed!")
    else:
        print("\n[FAIL] Parallelization not effective in benchmark.")

if __name__ == "__main__":
    asyncio.run(main())
