import time
import logging
import random
import hashlib
import asyncio
from typing import Dict, List, Set, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class NodeMetrics:
    total_uptime_hours: float = 0.0
    successful_dispatches: int = 0
    trust_score: float = 0.5
    contribution_score: float = 0.0
    tasks_completed: int = 0

class ProofOfContribution:
    """
    V8 Consensus: Proof of Contribution (PoC)
    - Thay thế Proof of Work bằng Trust & Contribution scores
    - Các Super Node (Trust > 0.8) vận hành mạng lưới
    - Ring Consensus cho việc validation
    """

    def __init__(self, node_id: str, p2p_network=None):
        self.node_id = node_id
        self.p2p = p2p_network
        self.trust_scores: Dict[str, float] = {node_id: 1.0}
        self.contribution_scores: Dict[str, float] = {node_id: 1.0}
        self.super_nodes: Set[str] = {node_id}
        self.my_metrics = NodeMetrics()

    def is_super_node(self, node_id: str) -> bool:
        """Check if node is a Super Node"""
        return node_id in self.super_nodes

    def get_super_nodes(self) -> List[str]:
        """Get all super nodes"""
        return list(self.super_nodes)

    def get_trust(self, node_id: str) -> float:
        return self.trust_scores.get(node_id, 0.5)

    def sign_message(self, message: str) -> str:
        """Simplified signing for PoC"""
        return hashlib.sha256(f"{self.node_id}:{message}".encode()).hexdigest()

    def validate_message(self, node_id: str, message: str, signature: str) -> bool:
        """Verify message from a peer"""
        expected = hashlib.sha256(f"{node_id}:{message}".encode()).hexdigest()
        return signature == expected

    def update_scores(self, node_id: str, trust_delta: float, contrib_delta: float):
        """Cập nhật điểm số dựa trên hành vi mạng lưới"""
        self.trust_scores[node_id] = max(0.0, min(1.0, self.get_trust(node_id) + trust_delta))
        self.contribution_scores[node_id] = self.contribution_scores.get(node_id, 0.0) + contrib_delta

        # Promotion to Super Node
        if self.trust_scores[node_id] > 0.8 and self.contribution_scores[node_id] > 100:
            self.super_nodes.add(node_id)
            logger.info(f"🌟 Node {node_id} promoted to SUPER NODE")

    async def start_monitoring(self):
        """Monitor network and update consensus state"""
        while True:
            await asyncio.sleep(60)
            logger.debug(f"Consensus monitor heartbeat for {self.node_id}")

    async def run_election(self):
        """Run super node election based on contribution"""
        logger.info(f"🗳️ Running election for {self.node_id}")
        # Simplified election logic
        if self.my_metrics.total_uptime_hours > 50 and self.my_metrics.successful_dispatches > 10:
            self.super_nodes.add(self.node_id)
            return True
        return False
