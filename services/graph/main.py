import asyncio
import logging
import hashlib
from contextlib import asynccontextmanager
from fastapi import FastAPI
from core.fvs_storage import FaissVectorStore
from core.p2p_gossip import GossipP2P as HybridP2P
from core.secure_dtq import MPCDistributedTaskQueue
from core.consensus import ProofOfContribution
from core.anchor_sync_v2 import DecentralizedSnapshot
from services.user_profile.profile_router import ProfileBasedRouter, UserTier
from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Global instances
fvs_store = None
p2p_network = None
dtq = None
consensus = None
snapshot_manager = None
profile_router = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup logic - COMPLETE P2P SYSTEM"""
    global fvs_store, p2p_network, dtq, consensus, snapshot_manager, profile_router

    if settings.ENABLE_FVS:
        logger.info("🚀 Initializing Complete P2P System...")

        # 1. Vector Store (FAISS)
        fvs_store = FaissVectorStore(
            node_id=settings.FVS_NODE_ID,
            dimension=settings.EMBEDDING_MODEL_DIM,
            index_type="IVF"
        )

        # 2. P2P Network (NAT Traversal)
        relay_nodes = []
        if settings.FVS_RELAY_NODES:
            relay_nodes = [
                tuple(node.split(':'))
                for node in settings.FVS_RELAY_NODES.split(',')
            ]

        p2p_network = HybridP2P(
            node_id=settings.FVS_NODE_ID,
            p2p_port=settings.FVS_P2P_PORT,
            relay_nodes=relay_nodes
        )
        await p2p_network.initialize()

        # 3. Proof-of-Contribution (Consensus)
        consensus = ProofOfContribution(
            node_id=settings.FVS_NODE_ID,
            p2p_network=p2p_network
        )
        consensus.fvs_store = fvs_store  # Link for metrics
        asyncio.create_task(consensus.start_monitoring())

        # 4. MPC-Enabled DTQ
        dtq = MPCDistributedTaskQueue(
            node_id=settings.FVS_NODE_ID,
            p2p_network=p2p_network,
            max_concurrent=3
        )

        # Register handlers
        dtq.register_handler('assimilate', handle_assimilate_task)
        dtq.register_handler('pre_compute_rag', handle_pre_compute_task)

        # 5. Decentralized Snapshot
        snapshot_manager = DecentralizedSnapshot(
            node_id=settings.FVS_NODE_ID,
            fvs_store=fvs_store,
            p2p_network=p2p_network,
            consensus=consensus
        )

        # Bootstrap if not Super Node
        await asyncio.sleep(5)  # Wait for peer discovery
        if not consensus.is_super_node():
            await snapshot_manager.bootstrap_from_super_nodes()

        asyncio.create_task(snapshot_manager.start_sync_loop())

        # 6. Profile-Based Router (P-RAG)
        profile_router = ProfileBasedRouter(
            fvs_store=fvs_store,
            p2p_network=p2p_network,
            consensus=consensus
        )
        profile_router.dtq = dtq  # Link for pre-computation

        # 7. Start workers
        asyncio.create_task(p2p_network.start())
        asyncio.create_task(dtq.start_worker())

        logger.info("✅ Complete P2P System Ready")
        logger.info(f"   Node ID: {settings.FVS_NODE_ID}")
        logger.info(f"   P2P Port: {settings.FVS_P2P_PORT}")

    yield

    logger.info("🛑 Shutting down P2P system...")

app = FastAPI(lifespan=lifespan)

# ============================================
# API ENDPOINTS - P-RAG POWERED
# ============================================

@app.post("/assimilate")
async def assimilate_endpoint(text: str, user_id: str):
    """
    Submit assimilation task (SECURE)
    """
    if not settings.ENABLE_FVS or not dtq:
        # Fallback to Celery
        from tasks import assimilate_task
        result = assimilate_task.delay(text)
        return {"status": "submitted", "task_id": result.id}

    # Submit SECURE task
    task_id = await dtq.submit_secure_task(
        task_type='assimilate',
        payload={'text': text, 'user_id': user_id},
        threshold=2,  # Need 2 key shares
        num_shares=3  # Distribute to 3 Super Nodes
    )

    # Update profile
    await profile_router.update_profile(user_id, 'contribution')

    return {
        "status": "submitted",
        "task_id": task_id,
        "message": "Secure task submitted to P2P network"
    }

@app.get("/chat")
async def chat_endpoint(query: str, user_id: str, top_k: int = 5):
    """
    Chat endpoint with P-RAG routing
    """
    if not settings.ENABLE_FVS or not profile_router:
        # Fallback implementation
        pass

    # 1. Get query embedding
    from services.embeddings import get_embedding
    query_embedding = await get_embedding(query)

    # 2. P-RAG Routing (based on user profile)
    context_results = await profile_router.route_query(
        user_id=user_id,
        query_embedding=query_embedding,
        top_k=top_k
    )

    # 3. Update profile
    await profile_router.update_profile(user_id, 'query')

    # 4. Generate response with LLM
    context_text = "\n\n".join([r['text'] for r in context_results])

    # Call HF Inference API
    from services.llm import generate_response
    answer = await generate_response(query, context_text)

    # 5. Schedule pre-computation (nếu STABLE user)
    profile = await profile_router._get_profile(user_id)
    if profile.tier == UserTier.STABLE:
        asyncio.create_task(
            profile_router.schedule_pre_computation(user_id)
        )

    return {
        "answer": answer,
        "context": context_results,
        "user_tier": profile.tier.value,
        "routing": "p-rag"
    }

@app.get("/stats")
async def stats_endpoint():
    """System statistics"""
    if not settings.ENABLE_FVS:
        return {"error": "FVS not enabled"}

    # Consensus stats
    consensus_stats = {
        "is_super_node": consensus.is_super_node(),
        "super_nodes_count": len(consensus.get_super_nodes()),
        "contribution_score": consensus.my_metrics.contribution_score,
        "uptime_hours": consensus.my_metrics.total_uptime_hours,
        "tasks_completed": consensus.my_metrics.tasks_completed
    }

    # P2P stats
    p2p_stats = {
        "peers_connected": len(p2p_network.peers),
        "relay_connected": p2p_network.relay_connection is not None,
        "public_address": p2p_network.public_address
    }

    # Vector store stats
    fvs_stats = {
        "total_vectors": fvs_store.index.ntotal,
        "storage_mb": fvs_store.data_dir.stat().st_size / (1024 * 1024)
    }

    # DTQ stats
    dtq_stats = {
        "pending_tasks": len([t for t in dtq.tasks.values() if t['status'] == 'pending']),
        "running_tasks": len(dtq.running_tasks),
        "completed_tasks": len([t for t in dtq.tasks.values() if t['status'] == 'completed'])
    }

    # Profile stats
    profile_stats = {
        "total_users": len(profile_router.profiles),
        "vip_users": len([p for p in profile_router.profiles.values() if p.tier == UserTier.VIP_PRO]),
        "stable_users": len([p for p in profile_router.profiles.values() if p.tier == UserTier.STABLE]),
        "ephemeral_users": len([p for p in profile_router.profiles.values() if p.tier == UserTier.EPHEMERAL])
    }

    return {
        "node_id": settings.FVS_NODE_ID,
        "consensus": consensus_stats,
        "p2p": p2p_stats,
        "vector_store": fvs_stats,
        "task_queue": dtq_stats,
        "profiles": profile_stats
    }
@app.post("/admin/promote-user")
async def promote_user_endpoint(user_id: str, target_tier: str):
    """Admin: Manually promote user tier"""
    profile = await profile_router._get_profile(user_id)

    if target_tier == "vip_pro":
        profile.tier = UserTier.VIP_PRO
    elif target_tier == "stable":
        profile.tier = UserTier.STABLE
    else:
        profile.tier = UserTier.EPHEMERAL

    return {
        "user_id": user_id,
        "new_tier": profile.tier.value,
        "message": "User tier updated"
    }

# ============================================
# TASK HANDLERS
# ============================================

async def handle_assimilate_task(payload: dict) -> dict:
    """Handle assimilation task (SECURE)"""
    text = payload['text']
    user_id = payload.get('user_id')

    # Get embedding
    from services.embeddings import get_embedding
    embedding = await get_embedding(text)

    # Save to FVS
    vec_id = hashlib.sha256(text.encode()).hexdigest()[:16]
    fvs_store.save(
        text=text,
        embedding=embedding,
        vec_id=vec_id,
        metadata={"source": user_id}
    )

    # Announce to network
    await p2p_network.announce_vector(vec_id)

    # Record contribution
    consensus.record_contribution('task_completed')

    logger.info(f"✅ Assimilated: {vec_id}")

    return {"vector_id": vec_id, "status": "success"}

async def handle_pre_compute_task(payload: dict) -> dict:
    """
    Handle pre-computation task (OFF-PEAK)
    - Pre-compute embeddings and context for preferred topics
    """
    user_id = payload['user_id']
    topic = payload['topic']

    logger.info(f"🔄 Pre-computing for {user_id}: {topic}")

    # Generate topic-related queries
    sample_queries = [
        f"What is {topic}?",
        f"How does {topic} work?",
        f"Latest news about {topic}"
    ]

    # Pre-compute embeddings and cache
    from services.embeddings import get_embedding

    for query in sample_queries:
        embedding = await get_embedding(query)

        # Search and cache
        results = fvs_store.search(embedding, top_k=10)

        # Store in profile cache
        cache_key = hashlib.sha256(embedding.tobytes()).hexdigest()[:16]
        profile = await profile_router._get_profile(user_id)
        if not profile.pre_computed_topics:
            profile.pre_computed_topics = set()
        profile.pre_computed_topics.add(topic)

    logger.info(f"✅ Pre-computation completed for {user_id}: {topic}")

    return {"user_id": user_id, "topic": topic, "status": "completed"}