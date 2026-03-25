
import asyncio
import time
import numpy as np
from core.p2p_gossip import GossipP2P
import json

class MockFVS:
    def __init__(self):
        self.vector_ids = ["vec1", "vec2"]
    def search(self, embedding, top_k):
        return [{"id": f"vec{i}", "score": 0.9} for i in range(top_k)]

class GossipP2PWithDelay(GossipP2P):
    async def _process_message(self, peer_id, message):
        if message.get('type') == 'query':
            await asyncio.sleep(0.1)
        return await super()._process_message(peer_id, message)

async def run_benchmark():
    print("Running P2P Gossip Query Benchmark with simulated latency...")

    # Setup 10 peers
    nodes = []
    for i in range(11): # 1 main + 10 peers
        if i > 0:
            node = GossipP2PWithDelay(node_id=f"node_{i}", port=10000 + i, fvs_store=MockFVS())
        else:
            node = GossipP2P(node_id=f"node_{i}", port=10000 + i, fvs_store=MockFVS())
        nodes.append(node)

    # Start nodes
    tasks = [asyncio.create_task(node.start()) for node in nodes]
    await asyncio.sleep(1) # Wait for servers to start

    main_node = nodes[0]
    for i in range(1, 11):
        main_node.add_bootstrap_peer(f"127.0.0.1:{10000+i}")

    query_vec = np.random.rand(128)

    print(f"Querying {len(main_node.peers)} peers...")
    start_time = time.time()
    results = await main_node.query_peers(query_vec, top_k=5)
    end_time = time.time()

    print(f"Query returned {len(results)} results")
    total_time = end_time - start_time
    print(f"Time taken: {total_time:.4f}s")

    if total_time < 0.3: # Should be around 0.1s + overhead, definitely < 1.0s
        print("SUCCESS: Performance optimization verified!")
    else:
        print("FAILURE: Performance optimization not effective.")

    # Cleanup
    for t in tasks:
        t.cancel()

if __name__ == "__main__":
    try:
        asyncio.run(run_benchmark())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        import traceback
        traceback.print_exc()
