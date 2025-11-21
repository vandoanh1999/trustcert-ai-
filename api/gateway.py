# api/gateway.py - Main API Gateway with FVS P2P Support
import asyncio
import hashlib
import logging
from contextlib import asynccontextmanager
from typing import Optional
import numpy as np

from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel

from core.config import get_settings, Settings
from core.fvs_storage import FaissVectorStore
from core.p2p_gossip import GossipP2P

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
fvs_store: Optional[FaissVectorStore] = None
p2p_network: Optional[GossipP2P] = None

# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class AssimilateRequest(BaseModel):
    text: str
    user_id: Optional[str] = None

class ChatRequest(BaseModel):
    query: str
    user_id: Optional[str] = None
    top_k: int = 5

class ChatResponse(BaseModel):
    answer: str
    context: list
    source: str

# ============================================
# LIFESPAN (STARTUP/SHUTDOWN)
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize P2P system on startup"""
    global fvs_store, p2p_network
    
    settings = get_settings()
    
    if settings.ENABLE_FVS:
        logger.info("Initializing FVS P2P System...")
        
        # Generate node ID if not set
        node_id = settings.FVS_NODE_ID or hashlib.sha256(
            f"node_{settings.FVS_P2P_PORT}".encode()
        ).hexdigest()[:12]
        
        # Initialize Vector Store
        fvs_store = FaissVectorStore(
            node_id=node_id,
            dimension=settings.EMBEDDING_MODEL_DIM,
            data_dir=settings.FVS_DATA_DIR
        )
        
        # Initialize P2P Network
        p2p_network = GossipP2P(
            node_id=node_id,
            port=settings.FVS_P2P_PORT,
            fvs_store=fvs_store
        )
        
        # Add bootstrap peers
        for peer in settings.get_bootstrap_peers():
            p2p_network.add_bootstrap_peer(peer)
        
        # Start P2P in background
        asyncio.create_task(p2p_network.start())
        
        logger.info(f"FVS P2P Ready - Node: {node_id}, Port: {settings.FVS_P2P_PORT}")
    
    yield
    
    # Cleanup
    if fvs_store:
        fvs_store.close()
    logger.info("Shutdown complete")

app = FastAPI(
    title="TrustCert AI - P2P Gateway",
    description="Decentralized AI Knowledge System",
    version="2.0.0",
    lifespan=lifespan
)

# ============================================
# AUTHENTICATION
# ============================================

async def verify_api_key(x_api_key: str = Header(None)):
    """Verify API key"""
    settings = get_settings()
    if settings.API_KEY and x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True

# ============================================
# HELPER FUNCTIONS
# ============================================

async def get_embedding(text: str) -> np.ndarray:
    """Get embedding from HuggingFace API"""
    import httpx
    
    settings = get_settings()
    
    url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{settings.EMBEDDING_MODEL_NAME}"
    headers = {"Authorization": f"Bearer {settings.HF_TOKEN}"} if settings.HF_TOKEN else {}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json={"inputs": text})
        
        if response.status_code != 200:
            logger.error(f"Embedding API error: {response.text}")
            raise HTTPException(status_code=500, detail="Embedding service error")
        
        embedding = response.json()
        
        # Handle nested list response
        if isinstance(embedding[0], list):
            embedding = embedding[0]
        
        return np.array(embedding, dtype='float32')

async def generate_response(query: str, context: str) -> str:
    """Generate response using LLM"""
    import httpx
    
    settings = get_settings()
    
    url = f"https://api-inference.huggingface.co/models/{settings.BASE_MODEL_NAME}"
    headers = {"Authorization": f"Bearer {settings.HF_TOKEN}"} if settings.HF_TOKEN else {}
    
    prompt = f"""Based on the following context, answer the question.

Context:
{context}

Question: {query}

Answer:"""
    
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            url, 
            headers=headers, 
            json={
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 512,
                    "temperature": 0.7
                }
            }
        )
        
        if response.status_code != 200:
            logger.error(f"LLM API error: {response.text}")
            return "I apologize, but I couldn't generate a response at this time."
        
        result = response.json()
        
        if isinstance(result, list) and len(result) > 0:
            return result[0].get('generated_text', '').replace(prompt, '').strip()
        
        return "I apologize, but I couldn't generate a response at this time."

# ============================================
# API ENDPOINTS
# ============================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "fvs_enabled": fvs_store is not None,
        "p2p_enabled": p2p_network is not None
    }

@app.get("/stats")
async def get_stats(auth: bool = Depends(verify_api_key)):
    """Get system statistics"""
    stats = {"fvs_enabled": False, "p2p_enabled": False}
    
    if fvs_store:
        stats["fvs_enabled"] = True
        stats["fvs_stats"] = fvs_store.get_stats()
    
    if p2p_network:
        stats["p2p_enabled"] = True
        stats["p2p_stats"] = {
            "peers": len(p2p_network.peers),
            "peer_list": list(p2p_network.peers)[:10]
        }
    
    return stats

@app.post("/assimilate")
async def assimilate(request: AssimilateRequest, auth: bool = Depends(verify_api_key)):
    """
    Assimilate new knowledge
    - Get embedding
    - Store in FVS
    - Announce to P2P network
    """
    if not fvs_store:
        raise HTTPException(status_code=503, detail="FVS not initialized")
    
    try:
        # Get embedding
        embedding = await get_embedding(request.text)
        
        # Generate vector ID
        vec_id = hashlib.sha256(request.text.encode()).hexdigest()[:16]
        
        # Save to FVS
        fvs_store.save(
            text=request.text,
            embedding=embedding,
            vec_id=vec_id,
            metadata={"user_id": request.user_id}
        )
        
        # Announce to P2P
        if p2p_network:
            await p2p_network.announce_vector(vec_id)
        
        logger.info(f"Assimilated: {vec_id}")
        
        return {
            "status": "success",
            "vector_id": vec_id,
            "message": "Knowledge assimilated"
        }
    
    except Exception as e:
        logger.error(f"Assimilation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, auth: bool = Depends(verify_api_key)):
    """
    Chat endpoint with RAG
    - Search local FVS
    - Query P2P peers if needed
    - Generate response
    """
    if not fvs_store:
        raise HTTPException(status_code=503, detail="FVS not initialized")
    
    try:
        # Get query embedding
        query_embedding = await get_embedding(request.query)
        
        # Search local FVS
        results = fvs_store.search(query_embedding, request.top_k)
        
        # Query P2P peers if not enough results
        if len(results) < request.top_k and p2p_network:
            peer_results = await p2p_network.query_peers(
                query_embedding, 
                request.top_k - len(results)
            )
            results.extend(peer_results)
        
        # Deduplicate
        seen = set()
        unique_results = []
        for r in results:
            if r['id'] not in seen:
                seen.add(r['id'])
                unique_results.append(r)
        
        results = unique_results[:request.top_k]
        
        # Build context
        context_text = "\n\n".join([r['text'] for r in results])
        
        # Generate response
        if context_text:
            answer = await generate_response(request.query, context_text)
        else:
            answer = "I don't have enough context to answer this question. Please provide more information."
        
        return ChatResponse(
            answer=answer,
            context=results,
            source="fvs_p2p"
        )
    
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
async def search(query: str, top_k: int = 5, auth: bool = Depends(verify_api_key)):
    """Direct vector search endpoint"""
    if not fvs_store:
        raise HTTPException(status_code=503, detail="FVS not initialized")
    
    try:
        embedding = await get_embedding(query)
        results = fvs_store.search(embedding, top_k)
        
        return {
            "results": results,
            "source": "local"
        }
    
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# P2P MANAGEMENT ENDPOINTS
# ============================================

@app.post("/p2p/add-peer")
async def add_peer(peer_address: str, auth: bool = Depends(verify_api_key)):
    """Manually add a peer"""
    if not p2p_network:
        raise HTTPException(status_code=503, detail="P2P not initialized")
    
    p2p_network.add_bootstrap_peer(peer_address)
    return {"status": "success", "peer": peer_address}

@app.get("/p2p/peers")
async def list_peers(auth: bool = Depends(verify_api_key)):
    """List connected peers"""
    if not p2p_network:
        return {"peers": []}
    
    return {
        "peers": list(p2p_network.peers),
        "total": len(p2p_network.peers)
    }