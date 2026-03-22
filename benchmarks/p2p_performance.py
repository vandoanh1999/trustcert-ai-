import asyncio
import time
import json
import logging
import numpy as np
from core.p2p_gossip import GossipP2P

# Mock FVS store for testing
class MockFVS:
    def __init__(self):
        self.vector_ids = ["vec1", "vec2"]
    def search(self, embedding, top_k):
        return [{"id": "vec1", "score": 0.9}, {"id": "vec2", "score": 0.8}]

async def mock_peer_server(port):
    server = await asyncio.start_server(lambda r, w: handle_mock(r, w), '127.0.0.1', port)
    async with server:
        await server.serve_forever()

async def handle_mock(reader, writer):
    try:
        data = await reader.read(8192)
        if data:
            message = json.loads(data.decode())
            if message.get('type') == 'query':
                await asyncio.sleep(0.1)  # Simulate network/processing latency
                response = {
                    "type": "query_response",
                    "results": [{"id": f"res_{time.time()}", "score": 0.95}],
                    "node_id": "mock_node"
                }
                writer.write(json.dumps(response).encode())
                await writer.drain()
            elif message.get('type') == 'announce':
                await asyncio.sleep(0.05)
    except Exception:
        pass
    finally:
        writer.close()
        await writer.wait_closed()

async def run_benchmark():
    num_peers = 10
    base_port = 9000

    print(f"Setting up {num_peers} mock peers...")
    peer_tasks = []
    for i in range(num_peers):
        task = asyncio.create_task(mock_peer_server(base_port + i))
        peer_tasks.append(task)

    await asyncio.sleep(1)

    gossip = GossipP2P("test_node", 8888, MockFVS())
    for i in range(num_peers):
        gossip.add_bootstrap_peer(f"127.0.0.1:{base_port + i}")

    print("Testing broadcast latency...")
    start_time = time.time()
    await gossip.broadcast({"type": "announce", "vector_ids": ["test"]})
    broadcast_duration = time.time() - start_time
    print(f"Broadcast to {num_peers} peers took: {broadcast_duration:.4f}s")

    print("Testing query_peers latency...")
    start_time = time.time()
    results = await gossip.query_peers(np.random.rand(384), top_k=5)
    query_duration = time.time() - start_time
    print(f"Query to {num_peers} peers took: {query_duration:.4f}s")
    print(f"Got {len(results)} results")

    for task in peer_tasks:
        task.cancel()

if __name__ == "__main__":
    asyncio.run(run_benchmark())
