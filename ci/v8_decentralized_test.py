"""
Genesis Core V8: Decentralized Network Self-Test (Converged & Corrected)

This script simulates a multi-node network to verify the complete
decentralized and Super Node logic from Phase 2. This version includes
a convergence waiter and a corrected test setup for the MPC fallback.
"""
import asyncio
from typing import List

from core.p2p import P2PNetwork
from core.node import DecentralizedNode, NodeTier

async def wait_for_convergence(nodes: List[DecentralizedNode], expected_messages: int):
    """Waits until all nodes have received an expected number of messages."""
    for _ in range(5):
        all_converged = True
        for node in nodes:
            if node.tier != NodeTier.SUPER_NODE:
                if len(node.pending_proposals.get("prop_astro_v1_12345", {}).get("votes", {})) < expected_messages:
                    all_converged = False
                    break
        if all_converged:
            print("  - Network has converged.")
            return
        await asyncio.sleep(0.1)
    print("  - Warning: Network did not converge in time.")

async def main():
    print("--- Running V8 Decentralized Network Self-Test ---")

    network = P2PNetwork()
    nodes = [DecentralizedNode(network.add_node()) for _ in range(5)]

    print("\n[1] Configuring Node Tiers and Initial State...")
    # Node 1, 2, 3: Super Nodes (3 are needed for MPC)
    nodes[0].contribution_score = 50.0; nodes[0].trust_score = 0.8; nodes[0].update_tier(); nodes[0].update_tier()
    nodes[1].contribution_score = 25.0; nodes[1].trust_score = 0.9; nodes[1].update_tier(); nodes[1].update_tier()
    nodes[2].contribution_score = 20.0; nodes[2].trust_score = 0.85; nodes[2].update_tier(); nodes[2].update_tier()

    # Node 4: Stable Node
    nodes[3].contribution_score = 15.0; nodes[3].update_tier()

    # Node 5: Ephemeral Node (will act as Rover)

    for node in nodes:
        for other_node in nodes:
            if node.node_id != other_node.node_id:
                node.known_peers[other_node.node_id] = {"tier": other_node.tier, "contribution": other_node.contribution_score}

    print("  - Network Initialized:")
    for node in nodes:
        print(f"    - {node.node_id}: {node.tier.name}, Trust={node.trust_score}, Contrib={node.contribution_score}")

    print("\n[2] Simulating Rover Proposal and Super Node Voting...")
    rover_node = nodes[4]
    proposal = {"proposal_id": "prop_astro_v1_12345", "expert_id": "expert_astrophysics_v1", "proof_of_source": "dataset_hash_xyz"}

    print(f"  - {rover_node.node_id} (Rover) is broadcasting a new expert proposal...")
    await rover_node.broadcast_message("NEW_EXPERT_PROPOSAL", proposal)

    await wait_for_convergence(nodes, expected_messages=3) # Wait for the 3 votes

    print("\n  - Verifying proposal status...")
    proposal_still_pending = any("prop_astro_v1_12345" in node.pending_proposals for node in nodes)

    if not proposal_still_pending:
        print("  - [PASS] Proposal was approved and removed from pending list.")
    else:
        print("  - [FAIL] Proposal was not approved.")
        exit(1)

    print("\n[3] Testing Decentralized MPC Fallback...")
    assert nodes[0].can_perform_mpc() == True
    print("  - [PASS] MPC is correctly enabled with 3 Super Nodes.")

    print("  - Simulating one Super Node going offline...")
    offline_node_id = nodes[1].node_id
    for node in nodes:
        if offline_node_id in node.known_peers:
            node.known_peers[offline_node_id]['tier'] = NodeTier.STABLE

    assert nodes[0].can_perform_mpc() == False
    print("  - [PASS] MPC is correctly disabled when a Super Node goes offline.")

    print("\n--- V8 Decentralized Network Self-Test Passed! ---")

if __name__ == "__main__":
    asyncio.run(main())
