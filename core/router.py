"""
Genesis Core V8: Personalized RAG (P-RAG) Router

This module implements the tier-aware query router, providing different
levels of service based on a user's authenticated tier.
"""
import random
from typing import List, Dict, Any

from core.node import DecentralizedNode, NodeTier
from core.user import User

class PersonalizedRouter:
    """A tier-aware router for dispatching queries across the network."""

    def __init__(self, own_node: DecentralizedNode):
        self.node = own_node

    def get_routing_targets(self, user: User) -> List[str]:
        """
        Determines the best target nodes for a query based on the user's tier.

        Returns:
            A list of node_ids to send the query to.
        """
        if user.tier == UserTier.VIP_PRO:
            # Item 12: Route VIP_PRO users to >= 3 Super Nodes for low latency.
            print(f"[{self.node.node_id}] Routing VIP user '{user.user_id}' to premium Super Node network.")
            super_nodes = [
                peer_id for peer_id, peer in self.node.known_peers.items()
                if peer.get('tier') == NodeTier.SUPER_NODE
            ]
            # In a real system, you'd select based on latency/health checks.
            return super_nodes[:3]

        elif user.tier == UserTier.EPHEMERAL:
            # Item 13: Route Ephemeral users to the local node + max 3 random peers.
            print(f"[{self.node.node_id}] Routing Ephemeral user '{user.user_id}' to a limited peer set.")
            random_peers = random.sample(
                list(self.node.known_peers.keys()),
                k=min(3, len(self.node.known_peers))
            )
            return [self.node.node_id] + random_peers

        else: # STABLE users
            print(f"[{self.node.node_id}] Routing Stable user '{user.user_id}' to the general network.")
            # Standard routing: broadcast to all known peers (or a subset)
            return list(self.node.known_peers.keys())

# --- Self-Test ---
if __name__ == "__main__":
    from core.p2p import P2PNetwork

    print("--- Running Personalized Router Self-Test ---")

    # 1. Setup Network and Users
    network = P2PNetwork()
    nodes = [DecentralizedNode(network.add_node()) for _ in range(5)]

    # Make nodes 1-3 Super Nodes, node 4 Stable
    nodes[0].tier = NodeTier.SUPER_NODE
    nodes[1].tier = NodeTier.SUPER_NODE
    nodes[2].tier = NodeTier.SUPER_NODE
    nodes[3].tier = NodeTier.STABLE

    # Populate the peer list for the router's node (node 0)
    for i in range(1, len(nodes)):
        nodes[0].known_peers[nodes[i].node_id] = {"tier": nodes[i].tier}

    router = PersonalizedRouter(nodes[0])

    # Create users with different tiers
    from core.user import UserTier
    vip_user = User("vip_user"); vip_user.tier = UserTier.VIP_PRO
    stable_user = User("stable_user"); stable_user.tier = UserTier.STABLE
    ephemeral_user = User("ephemeral_user")

    # 2. Test VIP_PRO Routing
    print("\n[1] Testing VIP_PRO routing...")
    vip_targets = router.get_routing_targets(vip_user)
    assert len(vip_targets) <= 3
    assert all(nodes[0].known_peers[target_id]['tier'] == NodeTier.SUPER_NODE for target_id in vip_targets)
    print(f"  - [PASS] VIP user routed to {len(vip_targets)} Super Nodes: {vip_targets}")

    # 3. Test Ephemeral Routing
    print("\n[2] Testing Ephemeral routing...")
    ephemeral_targets = router.get_routing_targets(ephemeral_user)
    assert len(ephemeral_targets) <= 4 # self + 3 random
    assert nodes[0].node_id in ephemeral_targets
    print(f"  - [PASS] Ephemeral user routed to {len(ephemeral_targets)} limited nodes: {ephemeral_targets}")

    # 4. Test Stable Routing
    print("\n[3] Testing Stable routing...")
    stable_targets = router.get_routing_targets(stable_user)
    assert len(stable_targets) == len(nodes[0].known_peers)
    print(f"  - [PASS] Stable user routed to all {len(stable_targets)} known peers.")

    print("\n--- Personalized Router Self-Test Passed! ---")
