import pytest
import numpy as np
import os
import json

from genesis_core.routing.router import MathematicallyGroundedRouter, AdvancedNode

def test_advanced_router_e2e():
    """
    A comprehensive test for the MathematicallyGroundedRouter.
    """
    # Create nodes
    nodes = [
        AdvancedNode("node_A", 0.9, np.random.rand(10), 50, 0.1, 0.85, 500),
        AdvancedNode("node_B", 0.85, np.random.rand(10), 30, 0.15, 0.90, 800),
        AdvancedNode("node_C", 0.95, np.random.rand(10), 20, 0.20, 0.95, 1000),
        AdvancedNode("node_D", 0.8, np.random.rand(10), 100, 0.05, 0.70, 300),
    ]

    router = MathematicallyGroundedRouter(nodes)

    query = np.random.rand(10)
    user_id = "user_123"

    # 1. Test routing with guarantees
    selected, proof = router.route_with_guarantees(
        query, user_id,
        latency_max=100.0,
        cost_max=0.5,
        privacy_min=0.2 + 1e-9 # Add a small epsilon for floating point
    )

    assert len(selected) > 0
    assert proof.verify_constraints()
    assert proof.decision_id is not None
    assert proof.proof_hash is not None

    # 2. Test counterfactual learning
    node_confidences = {n: nodes[i].reported_confidence for i, n in enumerate(selected)}
    actual_successes = {n: (True if i == 0 else False) for i, n in enumerate(selected)} # Make one fail
    observed_reward = 0.85

    router.learn_with_counterfactuals(
        selected, node_confidences, actual_successes, observed_reward
    )

    # Check if reputation was updated
    assert nodes[0].reputation != 0.9 or nodes[1].reputation != 0.85 or nodes[2].reputation != 0.95

    # 3. Test privacy budget tracking
    for i in range(3):
        router.route_with_guarantees(
            np.random.rand(10), user_id,
            latency_max=100.0, cost_max=0.5, privacy_min=0.2
        )

    remaining_budget = router.privacy_router.get_remaining_budget(user_id)
    assert remaining_budget.epsilon < float('inf')

    # 4. Test audit trail export
    audit_file = "test_audit_trail.json"
    if os.path.exists(audit_file):
        os.remove(audit_file)

    router.export_audit_trail(audit_file)

    assert os.path.exists(audit_file)
    with open(audit_file, 'r') as f:
        audit_data = json.load(f)
    assert len(audit_data) == 4 # 1 initial + 3 in loop

    os.remove(audit_file)
