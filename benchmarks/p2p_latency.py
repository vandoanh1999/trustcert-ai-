import asyncio
import time
import numpy as np
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.p2p_gossip import GossipP2P
from unittest.mock import patch

async def mock_send_to_peer(self, peer, message):
    await asyncio.sleep(0.1) # 100ms latency

async def mock_send_and_wait(self, peer, message, timeout=10):
    await asyncio.sleep(0.1) # 100ms latency
    return {"type": "query_response", "results": [{"id": "1", "score": 0.9}]}

async def run_benchmark():
    node = GossipP2P("node_0", 9000)
    # Add 10 mock peers
    for i in range(1, 11):
        node.add_bootstrap_peer(f"1.2.3.{i}:9000")

    print(f"Benchmarking with {len(node.peers)} peers and 100ms simulated latency per call...")

    # Test Broadcast
    with patch.object(GossipP2P, 'send_to_peer', mock_send_to_peer):
        start_time = time.time()
        await node.broadcast({"type": "test"})
        elapsed = time.time() - start_time
        print(f"Broadcast took: {elapsed:.4f}s")
        # Expect ~1.0s for sequential

    # Test Query
    with patch.object(GossipP2P, 'send_and_wait', mock_send_and_wait):
        start_time = time.time()
        await node.query_peers(np.random.rand(384))
        elapsed = time.time() - start_time
        print(f"Query took: {elapsed:.4f}s")
        # Expect ~1.0s for sequential

if __name__ == "__main__":
    asyncio.run(run_benchmark())
