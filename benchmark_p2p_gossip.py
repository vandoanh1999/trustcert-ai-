
import asyncio
import time
import json
import logging
from core.p2p_gossip import GossipP2P

# Mocking the send_to_peer to simulate network latency
async def mock_send_to_peer(self, peer, message):
    await asyncio.sleep(0.1) # 100ms latency

async def benchmark():
    print("Starting P2P Gossip Benchmark...")

    # Patch the send_to_peer to simulate network latency without actual networking
    original_send = GossipP2P.send_to_peer
    GossipP2P.send_to_peer = mock_send_to_peer

    node = GossipP2P("test_node", 8000)
    # Add 10 dummy peers
    num_peers = 10
    for i in range(num_peers):
        node.peers.add(f"127.0.0.1:{8001+i}")

    print(f"Broadcasting to {len(node.peers)} peers (now optimized)...")
    start_time = time.time()
    await node.broadcast({"type": "test"})
    end_time = time.time()
    duration = end_time - start_time
    print(f"Broadcast took: {duration:.4f}s")

    expected_sequential = num_peers * 0.1
    print(f"Expected sequential time would have been: ~{expected_sequential:.1f}s")

    if duration < expected_sequential / 2:
        print("SUCCESS: Performance improvement verified!")
    else:
        print("FAILURE: Performance does not meet expectations.")

    # Restore original
    GossipP2P.send_to_peer = original_send

if __name__ == "__main__":
    asyncio.run(benchmark())
