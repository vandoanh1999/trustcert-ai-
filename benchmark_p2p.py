import asyncio
import time
import numpy as np
import logging
from core.p2p_gossip import GossipP2P

# Disable logging to keep output clean
logging.basicConfig(level=logging.ERROR)

# Mocking network latency
LATENCY = 0.1 # 100ms per request

async def mock_send_to_peer(peer, message):
    await asyncio.sleep(LATENCY)

async def mock_send_and_wait(peer, message, timeout=10):
    await asyncio.sleep(LATENCY)
    if message.get('type') == 'query':
        return {
            "type": "query_response",
            "results": [{"id": f"res_{peer}", "score": 0.9}],
            "node_id": "peer_node"
        }
    return None

async def benchmark():
    print(f"--- Benchmarking P2P Gossip (Simulated Latency: {LATENCY}s) ---")

    node = GossipP2P("test_node", 8000)
    # Add 10 peers
    for i in range(10):
        node.add_bootstrap_peer(f"127.0.0.1:{8001+i}")

    # Override methods with mocks
    node.send_to_peer = mock_send_to_peer
    node.send_and_wait = mock_send_and_wait

    # 1. Benchmark Broadcast
    print(f"Broadcasting to {len(node.peers)} peers...")
    start_time = time.time()
    await node.broadcast({"type": "test"})
    broadcast_duration = time.time() - start_time
    print(f"Broadcast took: {broadcast_duration:.4f}s (Expected ~{len(node.peers) * LATENCY:.1f}s if sequential)")

    # 2. Benchmark Query
    print(f"Querying {len(node.peers)} peers...")
    query_embedding = np.random.rand(384)
    start_time = time.time()
    results = await node.query_peers(query_embedding)
    query_duration = time.time() - start_time
    print(f"Query took: {query_duration:.4f}s (Expected ~{len(node.peers) * LATENCY:.1f}s if sequential)")
    print(f"Results found: {len(results)}")

if __name__ == "__main__":
    asyncio.run(benchmark())
