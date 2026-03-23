import asyncio
import numpy as np
import unittest
from unittest.mock import MagicMock, AsyncMock
from core.p2p_gossip import GossipP2P

class TestGossipP2PParallel(unittest.IsolatedAsyncioTestCase):
    async def test_broadcast_parallel(self):
        node = GossipP2P("test_node", 9999)
        node.peers = {"127.0.0.1:9991", "127.0.0.1:9992"}

        # Mock send_to_peer to track calls
        node.send_to_peer = AsyncMock()

        message = {"type": "test"}
        await node.broadcast(message)

        self.assertEqual(node.send_to_peer.call_count, 2)
        node.send_to_peer.assert_any_call("127.0.0.1:9991", message)
        node.send_to_peer.assert_any_call("127.0.0.1:9992", message)

    async def test_query_peers_parallel(self):
        node = GossipP2P("test_node", 9999)
        node.peers = {"127.0.0.1:9991", "127.0.0.1:9992"}

        # Mock send_and_wait to return dummy results
        node.send_and_wait = AsyncMock(side_effect=[
            {"type": "query_response", "results": [{"id": "vec1", "score": 0.9}]},
            {"type": "query_response", "results": [{"id": "vec2", "score": 0.8}]}
        ])

        query_emb = np.zeros(384)
        results = await node.query_peers(query_emb, top_k=5)

        self.assertEqual(node.send_and_wait.call_count, 2)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["id"], "vec1")
        self.assertEqual(results[1]["id"], "vec2")

    async def test_query_peers_empty(self):
        node = GossipP2P("test_node", 9999)
        node.peers = set()

        query_emb = np.zeros(384)
        results = await node.query_peers(query_emb, top_k=5)
        self.assertEqual(results, [])

if __name__ == "__main__":
    unittest.main()
