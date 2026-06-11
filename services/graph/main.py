import asyncio
import logging
import hashlib
from contextlib import asynccontextmanager

from fastapi import FastAPI
from core.fvs_storage import FaissVectorStore
from core.p2p_gossip import GossipP2P
from core.secure_dtq import MPCDistributedTaskQueue
# from core.nat_traversal import HybridP2P # Assuming this might be missing or replaced by GossipP2P
from core.consensus import ProofOfContribution
from core.anchor_sync_v2 import DecentralizedSnapshot
from services.user_profile.profile_router import ProfileBasedRouter, UserTier

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock settings for now, in a real system these would come from core.config or env
class Settings:
    ENABLE_FVS = True
    FVS_NODE_ID = "genesis-node-1"
    EMBEDDING_MODEL_DIM = 384
    FVS_RELAY_NODES = ""
    FVS_P2P_PORT = 8765

settings = Settings()

def get_settings():
    return settings

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
            dimension=settings.EMBEDDING_MODEL_DIM
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

    yield

    logger.info("🛑 Shutting down P2P system...")

app = FastAPI(lifespan=lifespan)

# ... (rest of the endpoints - keeping them as they are but ensuring they use globals)
# NOTE: In a real app, you'd use Dependency Injection or a cleaner way to access these.

@app.post("/assimilate")
async def assimilate_endpoint(text: str, user_id: str):
    if not settings.ENABLE_FVS or not dtq:
        return {"status": "error", "message": "FVS/DTQ not enabled"}

    task_id = await dtq.submit_secure_task(
        task_type='assimilate',
        payload={'text': text, 'user_id': user_id},
        threshold=2,
        num_shares=3
    )
    await profile_router.update_profile(user_id, 'contribution')
    return {"status": "submitted", "task_id": task_id}

@app.get("/chat")
async def chat_endpoint(query: str, user_id: str, top_k: int = 5):
    # Simplified mock for chat
    return {"answer": "This is a mock answer", "routing": "p-rag"}

@app.get("/stats")
async def stats_endpoint():
    if not settings.ENABLE_FVS: return {"error": "FVS not enabled"}
    return {
        "node_id": settings.FVS_NODE_ID,
        "peers_connected": len(p2p_network.peers),
        "total_vectors": fvs_store.index.ntotal if fvs_store else 0
    }

async def handle_assimilate_task(payload: dict) -> dict:
    text = payload['text']
    user_id = payload.get('user_id')
    # Mock embedding and save
    logger.info(f"✅ Mock Assimilated for user {user_id}")
    return {"status": "success"}

async def handle_pre_compute_task(payload: dict) -> dict:
    logger.info(f"🔄 Mock Pre-computing")
    return {"status": "completed"}
