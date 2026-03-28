from enum import Enum
from dataclasses import dataclass
import time
import logging
import hashlib
from typing import List, Dict, Set
import numpy as np

logger = logging.getLogger(__name__)

class UserTier(Enum):
    """User tiers based on behavior"""
    EPHEMERAL = "ephemeral"  # Hỏi ất ơ
    STABLE = "stable"  # High engagement
    VIP_PRO = "vip_pro"  # Super users

@dataclass
class UserProfile:
    """User behavioral profile"""
    user_id: str
    tier: UserTier
    daily_interaction_time: float  # minutes
    total_queries: int
    contribution_score: float  # 0.0 - 1.0
    preferred_topics: List[str]
    last_active: float
    
    # Pre-fetch optimization
    pre_computed_topics: Set[str] = None
    cache_hit_rate: float = 0.0

class ProfileBasedRouter:
    """
    P-RAG Router: Phân luồng dựa trên User Profile
    - EPHEMERAL: Local only, no P2P
    - STABLE: Hybrid P2P + Pre-fetch
    - VIP_PRO: Super Nodes only, dedicated cache
    """
    
    def __init__(self, fvs_store, p2p_network, consensus):
        self.fvs = fvs_store
        self.p2p = p2p_network
        self.consensus = consensus
        
        # User profiles
        self.profiles: Dict[str, UserProfile] = {}
        
        # VIP cache (in-memory)
        self.vip_cache: Dict[str, List[Dict]] = {}
    
    async def route_query(self, user_id: str, query_embedding: np.ndarray, 
                         top_k: int = 5) -> List[Dict]:
        """
        Main routing logic
        """
        # Get or create profile
        profile = await self._get_profile(user_id)
        
        if profile.tier == UserTier.VIP_PRO:
            return await self._vip_search(user_id, query_embedding, top_k)
        
        elif profile.tier == UserTier.STABLE:
            return await self._stable_search(user_id, query_embedding, top_k, profile)
        
        else:  # EPHEMERAL
            return await self._ephemeral_search(query_embedding, top_k)
    
    async def _vip_search(self, user_id: str, query_embedding: np.ndarray, 
                         top_k: int) -> List[Dict]:
        """
        VIP PRO search: Super fast, dedicated resources
        """
        logger.info(f"🌟 VIP PRO search for {user_id}")
        
        # 1. Check VIP cache first
        cache_key = hashlib.sha256(query_embedding.tobytes()).hexdigest()[:16]
        if cache_key in self.vip_cache:
            logger.info("⚡ VIP cache hit")
            return self.vip_cache[cache_key]
        
        # 2. Search only on Super Nodes (fastest, most reliable)
        super_nodes = self.consensus.get_super_nodes()
        results = []
        
        for super_node in super_nodes:
            try:
                node_results = await self.p2p.query_specific_peer(
                    super_node, query_embedding, top_k
                )
                results.extend(node_results)
            except:
                continue
        
        # Deduplicate and sort
        results = self._deduplicate_results(results)[:top_k]
        
        # 3. Cache result
        self.vip_cache[cache_key] = results
        
        return results
    
    async def _stable_search(self, user_id: str, query_embedding: np.ndarray,
                            top_k: int, profile: UserProfile) -> List[Dict]:
        """
        STABLE user search: Hybrid local + P2P
        """
        logger.info(f"🌐 STABLE search for {user_id}")
        
        results = []
        
        # 1. Check pre-computed cache (nếu query match với preferred topics)
        # ... (implementation)
        
        # 2. Local search
        local_results = self.fvs.search(query_embedding, top_k)
        results.extend(local_results)
        
        # 3. Query Stable peers (nếu cần thêm)
        if len(results) < top_k:
            peer_results = await self.p2p.query_peers(
                query_embedding,
                top_k - len(results),
                tier_filter="stable"  # Chỉ hỏi Stable nodes
            )
            results.extend(peer_results)
        
        return self._deduplicate_results(results)[:top_k]
    
    async def _ephemeral_search(self, query_embedding: np.ndarray, 
                               top_k: int) -> List[Dict]:
        """
        EPHEMERAL user search: Local only, minimal resources
        """
        logger.info("💨 EPHEMERAL search (local only)")
        
        # Chỉ search local, KHÔNG broadcast P2P
        return self.fvs.search(query_embedding, top_k)
    
    async def _get_profile(self, user_id: str) -> UserProfile:
        """Get or create user profile"""
        if user_id not in self.profiles:
            # Create new profile
            self.profiles[user_id] = UserProfile(
                user_id=user_id,
                tier=UserTier.EPHEMERAL,  # Default
                daily_interaction_time=0.0,
                total_queries=0,
                contribution_score=0.0,
                preferred_topics=[],
                last_active=time.time()
            )
        
        return self.profiles[user_id]
    
    async def update_profile(self, user_id: str, event: str):
        """Update profile based on events"""
        profile = await self._get_profile(user_id)
        
        if event == 'query':
            profile.total_queries += 1
            
            # Upgrade tier nếu đủ điều kiện
            if profile.total_queries > 100 and profile.daily_interaction_time > 60:
                if profile.tier == UserTier.EPHEMERAL:
                    profile.tier = UserTier.STABLE
                    logger.info(f"⬆️ User {user_id} upgraded to STABLE")
            
            if profile.total_queries > 1000 and profile.contribution_score > 0.8:
                if profile.tier == UserTier.STABLE:
                    profile.tier = UserTier.VIP_PRO
                    logger.info(f"⬆️ User {user_id} upgraded to VIP PRO")
        
        elif event == 'contribution':
            profile.contribution_score = min(1.0, profile.contribution_score + 0.01)
        
        profile.last_active = time.time()
    
    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate results"""
        seen = set()
        unique = []
        
        for r in sorted(results, key=lambda x: x.get('score', 0), reverse=True):
            if r['id'] not in seen:
                seen.add(r['id'])
                unique.append(r)
        
        return unique
    
    async def schedule_pre_computation(self, user_id: str):
        """
        Schedule pre-computation for STABLE users
        - Runs during off-peak hours
        """
        profile = await self._get_profile(user_id)
        
        if profile.tier != UserTier.STABLE:
            return
        
        # Get preferred topics
        topics = profile.preferred_topics
        if not topics:
            return
        
        # Submit pre-compute tasks to DTQ
        for topic in topics:
            await self.dtq.submit_task(
                task_type='pre_compute_rag',
                payload={
                    'user_id': user_id,
                    'topic': topic
                },
                priority=TaskPriority.LOW,
                schedule_time='off_peak'  # 10PM - 6AM
            )
        
        logger.info(f"📅 Scheduled pre-computation for {user_id}: {topics}")