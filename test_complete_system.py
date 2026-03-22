import asyncio
import numpy as np
from pathlib import Path
import sys
import logging
import time

sys.path.insert(0, str(Path(__file__).parent))

from core.fvs_storage import FaissVectorStore
from core.p2p_gossip import GossipP2P
from core.secure_dtq import MPCDistributedTaskQueue
from core.consensus import ProofOfContribution
from core.anchor_sync_v2 import DecentralizedSnapshot
from services.user_profile.profile_router import ProfileBasedRouter, UserTier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompleteTestNode:
    """Full P2P node with all features"""
    
    def __init__(self, node_id: str, port: int):
        self.node_id = node_id
        self.port = port
        
        # Initialize all components
        self.fvs = FaissVectorStore(node_id, dimension=384)
        self.p2p = GossipP2P(node_id, port, self.fvs)
        self.consensus = ProofOfContribution(node_id, self.p2p)
        self.consensus.fvs_store = self.fvs
        self.dtq = MPCDistributedTaskQueue(node_id, self.p2p)
        self.snapshot = DecentralizedSnapshot(node_id, self.fvs, self.p2p, self.consensus)
        self.profile_router = ProfileBasedRouter(self.fvs, self.p2p, self.consensus)
        
        # Register handlers
        self.dtq.register_handler('test_task', self.handle_test_task)
    
    async def start(self):
        """Start all services"""
        logger.info(f"🚀 Starting complete node: {self.node_id}")
        
        # Start P2P
        self.p2p_task = asyncio.create_task(self.p2p.start())
        await asyncio.sleep(0.5)
        
        # Start consensus monitoring
        self.consensus_task = asyncio.create_task(self.consensus.start_monitoring())
        
        # Start DTQ worker
        self.dtq_task = asyncio.create_task(self.dtq.start_worker())
        
        # Start snapshot sync
        self.snapshot_task = asyncio.create_task(self.snapshot.start_sync_loop())
        
        logger.info(f"✅ Complete node ready: {self.node_id}")
    
    async def stop(self):
        """Stop all services"""
        self.p2p_task.cancel()
        self.consensus_task.cancel()
        self.dtq_task.cancel()
        self.snapshot_task.cancel()

    async def handle_test_task(self, payload):
        """Test task handler"""
        text = payload['text']
        embedding = np.random.rand(384)
        
        vec_id = f"vec_{self.node_id}_{int(time.time())}"
        self.fvs.save(text, embedding, vec_id)
        
        await self.p2p.announce_vector(vec_id)
        self.consensus.record_contribution('task_completed')
        
        return {"vector_id": vec_id}
    
    async def simulate_user_behavior(self, user_id: str, behavior: str):
        """Simulate user behavior patterns"""
        profile = await self.profile_router._get_profile(user_id)

        if behavior == "ephemeral":
            # Just 2 queries
            for i in range(2):
                query_emb = np.random.rand(384)
                await self.profile_router.route_query(user_id, query_emb, top_k=3)
                await self.profile_router.update_profile(user_id, 'query')
                await asyncio.sleep(0.01)
        
        elif behavior == "stable":
            # Force upgrade to STABLE for testing
            profile.total_queries = 101
            profile.daily_interaction_time = 61
            await self.profile_router.update_profile(user_id, 'query')

            topics = ["sexy", "gold_price"]
            for topic in topics:
                query_emb = np.random.rand(384)
                await self.profile_router.route_query(user_id, query_emb, top_k=5)
                if topic not in profile.preferred_topics:
                    profile.preferred_topics.append(topic)
                await asyncio.sleep(0.01)
        
        elif behavior == "vip":
            # Force upgrade to VIP PRO for testing
            profile.tier = UserTier.STABLE
            profile.total_queries = 1001
            profile.contribution_score = 0.81
            await self.profile_router.update_profile(user_id, 'query')

            for i in range(5):
                query_emb = np.random.rand(384)
                await self.profile_router.route_query(user_id, query_emb, top_k=5)
                await asyncio.sleep(0.01)

async def main():
    """Main test scenario"""
    logger.info("🧪 COMPLETE SYSTEM TEST\n")
    
    # 1. Create nodes
    logger.info("🏗️ Creating 3 test nodes...")
    nodes = [
        CompleteTestNode(f"node_{i}", 8765 + i)
        for i in range(3)
    ]
    
    # 2. Start all nodes
    for node in nodes:
        await node.start()
    
    # 3. Connect peers
    for i, node in enumerate(nodes):
        for j in range(len(nodes)):
            if i != j:
                peer_addr = f"127.0.0.1:{8765 + j}"
                node.p2p.add_bootstrap_peer(peer_addr)
    
    await asyncio.sleep(1)
    
    logger.info("\n" + "="*60 + "\n")
    
    # 4. Test consensus election
    logger.info("🗳️ Testing Consensus Election...")
    
    # Force super nodes for testing
    nodes[0].consensus.super_nodes.add("node_0")
    nodes[0].consensus.super_nodes.add("node_1")
    nodes[0].consensus.super_nodes.add("node_2")
    
    super_nodes = nodes[0].consensus.get_super_nodes()
    logger.info(f"🌟 Super Nodes (mocked for test): {super_nodes}")
    
    logger.info("\n" + "="*60 + "\n")
    
    # 5. Test user behaviors
    logger.info("👥 Testing P-RAG User Behaviors...")
    
    # User A: Ephemeral
    logger.info("\n📱 User A (Ephemeral):")
    await nodes[0].simulate_user_behavior("user_a", "ephemeral")
    profile_a = await nodes[0].profile_router._get_profile("user_a")
    logger.info(f"   Tier: {profile_a.tier.value}")
    
    # User B: Stable
    logger.info("\n📱 User B (Stable):")
    await nodes[0].simulate_user_behavior("user_b", "stable")
    profile_b = await nodes[0].profile_router._get_profile("user_b")
    logger.info(f"   Tier: {profile_b.tier.value}")
    
    # User Doanh: VIP
    logger.info("\n📱 User Doanh (VIP PRO):")
    await nodes[0].simulate_user_behavior("user_doanh", "vip")
    profile_d = await nodes[0].profile_router._get_profile("user_doanh")
    logger.info(f"   Tier: {profile_d.tier.value}")
    
    logger.info("\n" + "="*60 + "\n")
    
    # 6. Test secure task
    logger.info("🔒 Testing MPC-Enabled Secure Task...")
    
    task_id = await nodes[0].dtq.submit_secure_task(
        task_type='test_task',
        payload={'text': 'Secure test document'},
        threshold=2,
        num_shares=2
    )
    
    await asyncio.sleep(1)
    
    task = nodes[0].dtq.tasks.get(task_id)
    logger.info(f"   Task status: {task['status']}")
    
    logger.info("\n" + "="*60 + "\n")
    
    # 7. Final statistics
    logger.info("📊 FINAL STATISTICS:")
    for i, node in enumerate(nodes):
        logger.info(f"Node {i}: Peers: {len(node.p2p.peers)}")
    
    logger.info("\n" + "="*60 + "\n")
    logger.info("✅ COMPLETE SYSTEM TEST FINISHED!")
    
    for node in nodes:
        await node.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception("Test failed")
