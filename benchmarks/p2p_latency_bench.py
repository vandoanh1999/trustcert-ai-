import asyncio
import time
import json
import logging
from typing import Dict, List, Optional
import numpy as np
from core.p2p_gossip import GossipP2P

# Mocking send_to_peer and send_and_wait to simulate latency
async def mock_send_to_peer(self, peer: str, message: Dict):
    await asyncio.sleep(0.1) # 100ms latency

async def mock_send_and_wait(self, peer: str, message: Dict, timeout: float = 10) -> Optional[Dict]:
    await asyncio.sleep(0.1) # 100ms latency
    if message.get('type') == 'query':
        return {
            "type": "query_response",
            "results": [{"id": f"vec_{peer}", "score": 0.9}],
            "node_id": "remote"
        }
    return None

async def main():
    # Setup
    node = GossipP2P("test_node", 8000)
    for i in range(10):
        node.peers.add(f"127.0.0.1:800{i}")

    # Monkeypatch
    GossipP2P.send_to_peer = mock_send_to_peer
    GossipP2P.send_and_wait = mock_send_and_wait

    print(f"Benchmarking with {len(node.peers)} peers (100ms latency each)")

    # Measure broadcast
    start = time.perf_counter()
    await node.broadcast({"type": "test"})
    duration = time.perf_counter() - start
    print(f"Broadcast duration: {duration:.4f}s")

    # Measure query_peers
    start = time.perf_counter()
    results = await node.query_peers(np.zeros(128))
    duration = time.perf_counter() - start
    print(f"Query duration: {duration:.4f}s")
    print(f"Results count: {len(results)}")

if __name__ == "__main__":
    asyncio.run(main())
