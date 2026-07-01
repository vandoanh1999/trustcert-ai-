import asyncio
import numpy as np
from pathlib import Path
import sys
import logging

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
        self.p2p.consensus = self.consensus
        self.consensus.fvs_store = self.fvs
        self.dtq = MPCDistributedTaskQueue(node_id, self.p2p)
        self.snapshot = DecentralizedSnapshot(node_id, self.fvs, self.p2p, self.consensus)
        self.profile_router = ProfileBasedRouter(self.fvs, self.p2p, self.consensus)
        self.profile_router.dtq = self.dtq
        
        # Register handlers
        self.dtq.register_handler('test_task', self.handle_test_task)
    
    async def start(self):
        """Start all services"""
        logger.info(f"🚀 Starting complete node: {self.node_id}")
        
        # Start P2P
        asyncio.create_task(self.p2p.start())
        await asyncio.sleep(1)
        
        # Start consensus monitoring
        asyncio.create_task(self.consensus.start_monitoring())
        
        # Start DTQ worker
        asyncio.create_task(self.dtq.start_worker())
        
        # Start snapshot sync
        asyncio.create_task(self.snapshot.start_sync_loop())
        
        logger.info(f"✅ Complete node ready: {self.node_id}")
    
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
        if behavior == "ephemeral":
            # Thằng A: Hỏi 1-2 câu rồi biến
            for i in range(2):
                query_emb = np.random.rand(384)
                results = await self.profile_router.route_query(
                    user_id, query_emb, top_k=3
                )
                await self.profile_router.update_profile(user_id, 'query')
                await asyncio.sleep(1)
        
        elif behavior == "stable":
            # Thằng B: Hỏi nhiều, chủ đề cố định (sexy, vàng)
            topics = ["sexy", "gold_price"]
            for topic in topics * 10:  # 20 queries
                query_emb = np.random.rand(384)
                results = await self.profile_router.route_query(
                    user_id, query_emb, top_k=5
                )
                await self.profile_router.update_profile(user_id, 'query')
                
                # Update preferred topics
                profile = await self.profile_router._get_profile(user_id)
                if topic not in profile.preferred_topics:
                    profile.preferred_topics.append(topic)
                profile.daily_interaction_time += 0.5  # 30 seconds per query
                
                await asyncio.sleep(0.2)
        
        elif behavior == "vip":
            # Doanh 1102: Super active, high value
            for i in range(50):
                query_emb = np.random.rand(384)
                results = await self.profile_router.route_query(
                    user_id, query_emb, top_k=5
                )
                await self.profile_router.update_profile(user_id, 'query')
                await self.profile_router.update_profile(user_id, 'contribution')
                
                profile = await self.profile_router._get_profile(user_id)
                profile.daily_interaction_time += 1.0
                profile.contribution_score = min(1.0, profile.contribution_score + 0.02)
                
                await asyncio.sleep(0.1)

async def main():
    """Main test scenario"""
    logger.info("🧪 COMPLETE SYSTEM TEST\n")
    
    # 1. Create nodes
    logger.info("🏗️ Creating 5 test nodes...")
    nodes = [
        CompleteTestNode(f"node_{i}", 8765 + i)
        for i in range(5)
    ]
    
    # 2. Start all nodes
    for node in nodes:
        await node.start()
    
    # 3. Connect peers
    for i, node in enumerate(nodes):
        for j in range(i + 1, len(nodes)):
            peer_addr = f"localhost:{8765 + j}"
            node.p2p.add_bootstrap_peer(peer_addr)
    
    await asyncio.sleep(5)
    
    logger.info("\n" + "="*60 + "\n")
    
    # 4. Test consensus election
    logger.info("🗳️ Testing Consensus Election...")
    
    # Simulate different contribution levels
    nodes[0].consensus.my_metrics.total_uptime_hours = 100
    nodes[0].consensus.my_metrics.tasks_completed = 500
    nodes[1].consensus.my_metrics.total_uptime_hours = 80
    nodes[1].consensus.my_metrics.tasks_completed = 300
    
    await asyncio.sleep(10)  # Wait for election
    
    super_nodes = nodes[0].consensus.get_super_nodes()
    logger.info(f"🌟 Super Nodes elected: {super_nodes}")
    
    logger.info("\n" + "="*60 + "\n")
    
    # 5. Test user behaviors
    logger.info("👥 Testing P-RAG User Behaviors...")
    
    # User A: Ephemeral
    logger.info("\n📱 User A (Ephemeral):")
    await nodes[0].simulate_user_behavior("user_a", "ephemeral")
    profile_a = await nodes[0].profile_router._get_profile("user_a")
    logger.info(f"   Tier: {profile_a.tier.value}")
    logger.info(f"   Queries: {profile_a.total_queries}")
    
    # User B: Stable
    logger.info("\n📱 User B (Stable):")
    await nodes[0].simulate_user_behavior("user_b", "stable")
    profile_b = await nodes[0].profile_router._get_profile("user_b")
    logger.info(f"   Tier: {profile_b.tier.value}")
    logger.info(f"   Queries: {profile_b.total_queries}")
    logger.info(f"   Topics: {profile_b.preferred_topics}")
    
    # User Doanh: VIP
    logger.info("\n📱 User Doanh (VIP PRO):")
    await nodes[0].simulate_user_behavior("user_doanh", "vip")
    profile_d = await nodes[0].profile_router._get_profile("user_doanh")
    logger.info(f"   Tier: {profile_d.tier.value}")
    logger.info(f"   Queries: {profile_d.total_queries}")
    logger.info(f"   Contribution: {profile_d.contribution_score:.2f}")
    
    logger.info("\n" + "="*60 + "\n")
    
    # 6. Test secure task
    logger.info("🔒 Testing MPC-Enabled Secure Task...")
    
    task_id = await nodes[0].dtq.submit_secure_task(
        task_type='test_task',
        payload={'text': 'Secure test document'},
        threshold=2,
        num_shares=3
    )
    
    await asyncio.sleep(10)  # Wait for execution
    
    task = nodes[0].dtq.tasks.get(task_id)
    logger.info(f"   Task status: {task['status']}")
    
    logger.info("\n" + "="*60 + "\n")
    
    # 7. Final statistics
    logger.info("📊 FINAL STATISTICS:")
    
    for i, node in enumerate(nodes):
        logger.info(f"\nNode {i}:")
        logger.info(f"  Vectors: {node.fvs.index.ntotal}")
        logger.info(f"  Peers: {len(node.p2p.peers)}")
        logger.info(f"  Is Super Node: {node.consensus.is_super_node()}")
        logger.info(f"  Contribution Score: {node.consensus.my_metrics.contribution_score:.3f}")
        logger.info(f"  Tasks Completed: {node.consensus.my_metrics.tasks_completed}")
    
    logger.info(f"\nUser Profiles:")
    logger.info(f"  Total Users: {len(nodes[0].profile_router.profiles)}")
    logger.info(f"  VIP Users: {[u for u, p in nodes[0].profile_router.profiles.items() if p.tier == UserTier.VIP_PRO]}")
    logger.info(f"  Stable Users: {[u for u, p in nodes[0].profile_router.profiles.items() if p.tier == UserTier.STABLE]}")
    
    logger.info("\n" + "="*60 + "\n")
    logger.info("✅ COMPLETE SYSTEM TEST FINISHED!")
    logger.info("Press Ctrl+C to exit...")
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n👋 Doanh 1102!")