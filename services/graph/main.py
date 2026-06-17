import asyncio
import logging
import hashlib
from fastapi import FastAPI
from contextlib import asynccontextmanager
from typing import List, Dict, Any

from core.fvs_storage import FaissVectorStore
from core.p2p_gossip import GossipP2P
from core.secure_dtq import MPCDistributedTaskQueue
from core.consensus import ProofOfContribution
from core.anchor_sync_v2 import DecentralizedSnapshot
from services.user_profile.profile_router import ProfileBasedRouter, UserTier

logger = logging.getLogger(__name__)

# Global instances
fvs_store = None
p2p_network = None
dtq = None
consensus = None
snapshot_manager = None
profile_router = None

# Mock settings for demonstration if not provided by a real config
class MockSettings:
    ENABLE_FVS = True
    FVS_NODE_ID = "main_node"
    EMBEDDING_MODEL_DIM = 384
    FVS_RELAY_NODES = ""
    FVS_P2P_PORT = 8003

settings = MockSettings()

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

        # 2. P2P Network
        p2p_network = GossipP2P(
            node_id=settings.FVS_NODE_ID,
            port=settings.FVS_P2P_PORT,
            fvs_store=fvs_store
        )

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
        await asyncio.sleep(2)  # Wait for peer discovery

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
        return {"error": "DTQ not enabled"}

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
    # 1. Get query embedding (Mocked for now)
    query_embedding = np.random.rand(384)

    # 2. P-RAG Routing (based on user profile)
    context_results = await profile_router.route_query(
        user_id=user_id,
        query_embedding=query_embedding,
        top_k=top_k
    )

    # 3. Update profile
    await profile_router.update_profile(user_id, 'query')

    # 4. Generate response with LLM (Mocked)
    answer = "This is a mocked response based on retrieved context."

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

    return {
        "node_id": settings.FVS_NODE_ID,
        "consensus": {
            "is_super_node": consensus.is_super_node(),
            "super_nodes_count": len(consensus.get_super_nodes())
        },
        "p2p": {
            "peers_connected": len(p2p_network.peers)
        }
    }

# ============================================
# TASK HANDLERS
# ============================================

async def handle_assimilate_task(payload: dict) -> dict:
    """Handle assimilation task (SECURE)"""
    text = payload['text']
    user_id = payload.get('user_id')

    # Get embedding (Mocked)
    embedding = np.random.rand(384)

    # Save to FVS
    vec_id = hashlib.sha256(text.encode()).hexdigest()[:16]
    fvs_store.save(
        text=text,
        embedding=embedding,
        vec_id=vec_id,
        metadata={"source": user_id}
    )

    # Record contribution
    consensus.record_contribution('task_completed')

    logger.info(f"✅ Assimilated: {vec_id}")

    return {"vector_id": vec_id, "status": "success"}

async def handle_pre_compute_task(payload: dict) -> dict:
    """
    Handle pre-computation task (OFF-PEAK)
    """
    user_id = payload['user_id']
    topic = payload['topic']

    logger.info(f"🔄 Pre-computing for {user_id}: {topic}")
    return {"status": "completed"}
