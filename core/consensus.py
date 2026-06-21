import time
import hashlib
import json
import asyncio
from typing import Dict, List, Set, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class NodeMetrics:
    """Metrics for Proof-of-Contribution"""
    node_id: str
    uptime_score: float  # 0.0 - 1.0
    bandwidth_score: float  # 0.0 - 1.0
    storage_score: float  # 0.0 - 1.0
    contribution_score: float  # Tổng điểm
    last_updated: float
    
    # Statistics
    total_uptime_hours: float = 0.0
    vectors_served: int = 0
    tasks_completed: int = 0
    relay_sessions: int = 0

class ProofOfContribution:
    """
    Proof-of-Contribution: Thuật toán bầu chọn Super Nodes
    - Không cần blockchain (quá nặng)
    - Dùng Gossip Protocol để đồng bộ metrics
    - Election mỗi 24h hoặc khi Super Node offline
    """
    
    def __init__(self, node_id: str, p2p_network):
        self.node_id = node_id
        self.p2p = p2p_network
        
        # Node registry
        self.node_metrics: Dict[str, NodeMetrics] = {}
        
        # Super Node list (elected)
        self.super_nodes: Set[str] = set()
        self.election_interval = 86400  # 24h
        self.last_election = 0
        
        # Self metrics
        self.my_metrics = NodeMetrics(
            node_id=node_id,
            uptime_score=0.0,
            bandwidth_score=0.0,
            storage_score=0.0,
            contribution_score=0.0,
            last_updated=time.time()
        )
        
        # Tracking
        self.startup_time = time.time()
        self.total_online_time = 0.0
        self.last_heartbeat = time.time()
    
    async def start_monitoring(self):
        """Background: Monitor và update metrics"""
        while True:
            try:
                # Update self metrics
                await self._update_self_metrics()
                
                # Broadcast metrics to peers
                await self._broadcast_metrics()
                
                # Check if election needed
                if time.time() - self.last_election > self.election_interval:
                    await self._conduct_election()
                
                await asyncio.sleep(60)  # Every 1 minute
                
            except Exception as e:
                logger.error(f"❌ Monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _update_self_metrics(self):
        """Update metrics của node này"""
        now = time.time()
        
        # 1. Uptime Score
        online_duration = now - self.last_heartbeat
        self.total_online_time += online_duration
        total_time = now - self.startup_time
        uptime_ratio = self.total_online_time / total_time if total_time > 0 else 0
        self.my_metrics.uptime_score = min(1.0, uptime_ratio)
        self.my_metrics.total_uptime_hours = self.total_online_time / 3600
        
        # 2. Bandwidth Score (estimate từ relay sessions)
        # Simplified: Assume mỗi relay session = 1 MB
        estimated_bandwidth_mb = self.my_metrics.relay_sessions * 1.0
        self.my_metrics.bandwidth_score = min(1.0, estimated_bandwidth_mb / 1000)
        
        # 3. Storage Score (từ FVS)
        # Get từ FaissVectorStore
        if hasattr(self, 'fvs_store') and self.fvs_store:
            # Check if it has data_dir attribute and it exists
            if hasattr(self.fvs_store, 'data_dir') and self.fvs_store.data_dir.exists():
                 # Use a simple way to get size if it's a directory
                 storage_mb = sum(f.stat().st_size for f in self.fvs_store.data_dir.glob('**/*') if f.is_file()) / (1024 * 1024)
                 self.my_metrics.storage_score = min(1.0, storage_mb / 10240)  # Max 10GB
        
        # 4. Contribution Score (weighted average)
        weights = {
            'uptime': 0.4,
            'bandwidth': 0.3,
            'storage': 0.2,
            'tasks': 0.1
        }
        
        task_score = min(1.0, self.my_metrics.tasks_completed / 1000)
        
        self.my_metrics.contribution_score = (
            self.my_metrics.uptime_score * weights['uptime'] +
            self.my_metrics.bandwidth_score * weights['bandwidth'] +
            self.my_metrics.storage_score * weights['storage'] +
            task_score * weights['tasks']
        )
        
        self.my_metrics.last_updated = now
        self.last_heartbeat = now
        
        # Store in registry
        self.node_metrics[self.node_id] = self.my_metrics
    
    async def _broadcast_metrics(self):
        """Broadcast metrics qua Gossip"""
        await self.p2p.broadcast({
            "type": "metrics_update",
            "node_id": self.node_id,
            "metrics": {
                "uptime_score": self.my_metrics.uptime_score,
                "bandwidth_score": self.my_metrics.bandwidth_score,
                "storage_score": self.my_metrics.storage_score,
                "contribution_score": self.my_metrics.contribution_score,
                "total_uptime_hours": self.my_metrics.total_uptime_hours,
                "vectors_served": self.my_metrics.vectors_served,
                "tasks_completed": self.my_metrics.tasks_completed,
                "relay_sessions": self.my_metrics.relay_sessions,
                "last_updated": self.my_metrics.last_updated
            }
        })
    
    async def _conduct_election(self):
        """
        Bầu chọn Super Nodes
        - Top 5% nodes theo contribution_score
        - Minimum 3 nodes, Maximum 10 nodes
        """
        logger.info("🗳️ Conducting Super Node election...")
        
        # Filter valid nodes (updated trong 5 phút qua)
        now = time.time()
        valid_nodes = {
            nid: metrics for nid, metrics in self.node_metrics.items()
            if now - metrics.last_updated < 300  # 5 minutes
        }
        
        if len(valid_nodes) < 3:
            logger.warning("⚠️ Not enough nodes for election")
            return
        
        # Sort by contribution score
        sorted_nodes = sorted(
            valid_nodes.items(),
            key=lambda x: x[1].contribution_score,
            reverse=True
        )
        
        # Select top 5% (min 3, max 10)
        num_super = max(3, min(10, int(len(sorted_nodes) * 0.05)))
        # Special case for testing: if we have few nodes, allow more super nodes
        if len(sorted_nodes) < 10:
            num_super = min(len(sorted_nodes), 3)

        new_super_nodes = set([nid for nid, _ in sorted_nodes[:num_super]])
        
        # Announce results
        if new_super_nodes != self.super_nodes:
            self.super_nodes = new_super_nodes
            
            await self.p2p.broadcast({
                "type": "election_result",
                "super_nodes": list(self.super_nodes),
                "timestamp": now,
                "total_nodes": len(valid_nodes)
            })
            
            if self.node_id in self.super_nodes:
                logger.info(f"🌟 ELECTED AS SUPER NODE! (Rank: {sorted_nodes.index((self.node_id, self.my_metrics)) + 1}/{len(valid_nodes)})")
            else:
                logger.info(f"📊 Election completed. Super Nodes: {len(self.super_nodes)}")
        
        self.last_election = now
    
    async def handle_peer_message(self, message: Dict):
        """Xử lý metrics updates từ peers"""
        msg_type = message.get('type')
        
        if msg_type == 'metrics_update':
            node_id = message['node_id']
            metrics_data = message['metrics']
            
            # Update registry
            self.node_metrics[node_id] = NodeMetrics(
                node_id=node_id,
                uptime_score=metrics_data['uptime_score'],
                bandwidth_score=metrics_data['bandwidth_score'],
                storage_score=metrics_data['storage_score'],
                contribution_score=metrics_data['contribution_score'],
                last_updated=metrics_data['last_updated'],
                total_uptime_hours=metrics_data['total_uptime_hours'],
                vectors_served=metrics_data['vectors_served'],
                tasks_completed=metrics_data['tasks_completed'],
                relay_sessions=metrics_data['relay_sessions']
            )
        
        elif msg_type == 'election_result':
            # Accept election result
            self.super_nodes = set(message['super_nodes'])
            self.last_election = message['timestamp']
            
            logger.info(f"🗳️ Election result received: {len(self.super_nodes)} Super Nodes")
    
    def is_super_node(self, node_id: str = None) -> bool:
        """Check if a node is Super Node"""
        target = node_id if node_id else self.node_id
        return target in self.super_nodes
    
    def get_super_nodes(self) -> List[str]:
        """Get list of current Super Nodes"""
        return list(self.super_nodes)
    
    def record_contribution(self, event_type: str, count: int = 1):
        """Record contribution event"""
        if event_type == 'vector_served':
            self.my_metrics.vectors_served += count
        elif event_type == 'task_completed':
            self.my_metrics.tasks_completed += count
        elif event_type == 'relay_session':
            self.my_metrics.relay_sessions += count
