import hashlib
import numpy as np
import logging
import time
import json
from typing import Set, List, Any, Dict, Optional
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

class UserTier(Enum):
    EPHEMERAL = "EPHEMERAL"
    STABLE = "STABLE"
    VIP_PRO = "VIP_PRO"

@dataclass
class UserProfile:
    user_id: str
    tier: UserTier
    contribution_score: float
    last_active: float
    verified_credentials: List[str]
    total_queries: int = 0
    preferred_topics: Set[str] = field(default_factory=set)
    daily_interaction_time: float = 0.0

class ProfileBasedRouter:
    """
    P-RAG (Personalized RAG) Router
    - Routes queries based on user tier and history
    - Upgrades users based on contribution
    - Optimizes resource allocation
    """

    def __init__(self, fvs_store=None, p2p_network=None, consensus=None):
        self.fvs = fvs_store
        self.p2p = p2p_network
        self.consensus = consensus
        self.user_profiles: Dict[str, UserProfile] = {}

        # Routing policy
        self.tier_limits = {
            UserTier.EPHEMERAL: {"max_top_k": 5, "priority": 0},
            UserTier.STABLE: {"max_top_k": 10, "priority": 1},
            UserTier.VIP_PRO: {"max_top_k": 25, "priority": 2}
        }

    def get_or_create_profile(self, user_id: str) -> UserProfile:
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(
                user_id=user_id,
                tier=UserTier.EPHEMERAL,
                contribution_score=0.0,
                last_active=time.time(),
                verified_credentials=[]
            )
        return self.user_profiles[user_id]

    def _get_profile(self, user_id: str) -> Optional[UserProfile]:
        return self.user_profiles.get(user_id)

    async def route_query(self, user_id: str, query_embedding: np.ndarray,
                          top_k: int = 5) -> List[Dict]:
        """
        Route query with P-RAG optimizations
        """
        profile = self.get_or_create_profile(user_id)

        # 1. Apply tier-based limits
        limits = self.tier_limits[profile.tier]
        final_top_k = min(top_k, limits['max_top_k'])

        # 2. Select target nodes based on tier
        # VIP users get routed to nodes with higher reputation/uptime
        target_nodes = self._select_nodes_for_tier(profile.tier)

        # 3. Execute distributed search
        if self.p2p:
            results = await self.p2p.query_peers(query_embedding, top_k=final_top_k)
        else:
            results = []

        # 4. Update activity
        profile.last_active = time.time()
        profile.total_queries += 1

        return results

    def _select_nodes_for_tier(self, tier: UserTier) -> List[str]:
        """Filter nodes based on performance metrics for higher tiers"""
        if not self.p2p:
            return []
        all_peers = list(self.p2p.peers)
        if tier == UserTier.EPHEMERAL:
            return all_peers

        # Simplified: higher tiers use nodes with > 0.8 trust
        # In real system, this would use self.p2p.peer_trust_scores
        return all_peers

    def record_contribution(self, user_id: str, score: float):
        """Record user contribution and check for upgrades"""
        profile = self.get_or_create_profile(user_id)
        profile.contribution_score += score

        # Check for upgrades
        if profile.tier == UserTier.EPHEMERAL and profile.contribution_score > 10.0:
            profile.tier = UserTier.STABLE
            logger.info(f"⬆️ User {user_id} upgraded to STABLE")

        if profile.tier == UserTier.STABLE and profile.contribution_score > 100.0:
            profile.tier = UserTier.VIP_PRO
            logger.info(f"⬆️ User {user_id} upgraded to VIP PRO")

    async def update_profile(self, user_id: str, activity_type: str):
        """Update profile based on activity"""
        profile = self.get_or_create_profile(user_id)
        if activity_type == 'query':
            profile.contribution_score += 0.1
        elif activity_type == 'contribution':
            profile.contribution_score += 5.0

        # Re-check upgrades
        self.record_contribution(user_id, 0)
