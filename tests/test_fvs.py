# tests/test_fvs.py - Test FVS P2P System
import asyncio
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.fvs_storage import FaissVectorStore
from core.p2p_gossip import GossipP2P

async def test_local_fvs():
    """Test local vector storage"""
    print("\n" + "="*50)
    print("TEST 1: Local FVS Storage")
    print("="*50)
    
    # Initialize
    store = FaissVectorStore("test_node", dimension=384, data_dir="./test_data")
    
    # Save vectors
    for i in range(10):
        text = f"Test document number {i} with some content"
        embedding = np.random.rand(384).astype('float32')
        vec_id = store.save(text, embedding)
        print(f"  Saved: {vec_id}")
    
    # Search
    query = np.random.rand(384).astype('float32')
    results = store.search(query, top_k=3)
    
    print(f"\n  Search results:")
    for r in results:
        print(f"    - {r['text'][:40]}... (score: {r['score']:.3f})")
    
    # Stats
    print(f"\n  Stats: {store.get_stats()}")
    
    store.close()
    print("  PASSED")

async def test_p2p_network():
    """Test P2P network"""
    print("\n" + "="*50)
    print("TEST 2: P2P Network")
    print("="*50)
    
    # Create two nodes
    store1 = FaissVectorStore("node_1", dimension=384, data_dir="./test_data")
    store2 = FaissVectorStore("node_2", dimension=384, data_dir="./test_data")
    
    p2p1 = GossipP2P("node_1", 8765, store1)
    p2p2 = GossipP2P("node_2", 8766, store2)
    
    # Start servers
    asyncio.create_task(p2p1.start())
    asyncio.create_task(p2p2.start())
    
    await asyncio.sleep(1)
    
    # Connect peers
    p2p1.add_bootstrap_peer("localhost:8766")
    p2p2.add_bootstrap_peer("localhost:8765")
    
    print(f"  Node 1 peers: {p2p1.peers}")
    print(f"  Node 2 peers: {p2p2.peers}")
    
    # Add vectors to node 1
    for i in range(5):
        text = f"Node 1 document {i}"
        embedding = np.random.rand(384).astype('float32')
        vec_id = store1.save(text, embedding)
        await p2p1.announce_vector(vec_id)
    
    await asyncio.sleep(1)
    
    # Query from node 2
    query = np.random.rand(384).astype('float32')
    results = await p2p2.query_peers(query, top_k=3)
    
    print(f"\n  P2P Query results from node 2:")
    for r in results:
        print(f"    - {r['text']} (score: {r['score']:.3f})")
    
    store1.close()
    store2.close()
    print("  PASSED")

async def main():
    """Run all tests"""
    print("\n" + "="*50)
    print("FVS P2P SYSTEM TESTS")
    print("="*50)
    
    await test_local_fvs()
    await test_p2p_network()
    
    print("\n" + "="*50)
    print("ALL TESTS PASSED")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main())