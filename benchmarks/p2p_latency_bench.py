import sys
from unittest.mock import MagicMock, patch

# Mock numpy for GossipP2P import
sys.modules['numpy'] = MagicMock()

import asyncio
import time
import json
from core.p2p_gossip import GossipP2P

async def mock_send_to_peer(self, peer, message):
    # Simulate network latency
    await asyncio.sleep(0.1)
    return

async def mock_send_and_wait(self, peer, message, timeout=10):
    # Simulate network latency
    await asyncio.sleep(0.1)
    return {
        "type": "query_response",
        "results": [{"id": f"vec_{peer}", "score": 0.9}],
        "node_id": "remote_node"
    }

async def run_benchmark():
    node_id = "bench_node"
    port = 8000
    p2p = GossipP2P(node_id, port)

    # Add 10 dummy peers
    for i in range(10):
        p2p.peers.add(f"192.168.1.{100+i}:8000")

    print(f"--- Benchmarking GossipP2P with {len(p2p.peers)} peers (0.1s simulated latency) ---")

    # Benchmark Broadcast
    with patch.object(GossipP2P, 'send_to_peer', mock_send_to_peer):
        print("Testing broadcast...")
        start = time.time()
        await p2p.broadcast({"type": "announce", "data": "test"})
        end = time.time()
        broadcast_time = end - start
        print(f"Broadcast time: {broadcast_time:.4f}s")

    # Benchmark Query
    with patch.object(GossipP2P, 'send_and_wait', mock_send_and_wait):
        import numpy as np
        print("Testing query_peers...")
        start = time.time()
        results = await p2p.query_peers(np.zeros(128))
        end = time.time()
        query_time = end - start
        print(f"Query peers time: {query_time:.4f}s")
        print(f"Results found: {len(results)}")

    return broadcast_time, query_time

if __name__ == "__main__":
    asyncio.run(run_benchmark())
