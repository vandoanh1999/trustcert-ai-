
import asyncio
import time
import numpy as np
from unittest.mock import AsyncMock, patch
from core.p2p_gossip import GossipP2P

async def benchmark_p2p():
    num_peers = 10
    peers = [f"127.0.0.1:{8000+i}" for i in range(num_peers)]

    # Initialize GossipP2P
    node = GossipP2P(node_id="test_node", port=7999)
    for peer in peers:
        node.add_bootstrap_peer(peer)

    # Mock send_to_peer and send_and_wait to simulate 100ms latency
    async def mocked_send(*args, **kwargs):
        await asyncio.sleep(0.1)
        return {"status": "ok"}

    async def mocked_send_wait(*args, **kwargs):
        await asyncio.sleep(0.1)
        return {"type": "query_response", "results": [{"id": "vec_1", "score": 0.9}], "node_id": "peer"}

    print(f"--- Benchmarking GossipP2P with {num_peers} peers (simulated 100ms latency) ---")

    # Benchmark broadcast
    with patch.object(node, 'send_to_peer', side_effect=mocked_send):
        start = time.time()
        await node.broadcast({"type": "test", "data": "hello"})
        duration = time.time() - start
        print(f"Parallel Broadcast: {duration:.4f}s (Expected ~0.1s)")

    # Benchmark query_peers
    with patch.object(node, 'send_and_wait', side_effect=mocked_send_wait):
        start = time.time()
        query = np.random.rand(384)
        await node.query_peers(query, top_k=5)
        duration = time.time() - start
        print(f"Parallel Query:     {duration:.4f}s (Expected ~0.1s)")

if __name__ == "__main__":
    asyncio.run(benchmark_p2p())
