import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from collections import deque
import hashlib
import time
from scipy.optimize import linprog
from scipy.stats import entropy

# ============= #4: PRIVACY ALGEBRA =============
@dataclass
class PrivacyBudget:
    """Differential Privacy budget với composition theorem"""
    epsilon: float
    delta: float
    leakage_vector: np.ndarray  # Per-feature leakage

    def compose(self, other: 'PrivacyBudget') -> 'PrivacyBudget':
        """
        Basic privacy composition: simply add the budgets.
        This is numerically stable and sufficient for this use case.
        """
        epsilon_composed = self.epsilon + other.epsilon
        delta_composed = self.delta + other.delta
        leakage_composed = self.leakage_vector + other.leakage_vector

        return PrivacyBudget(epsilon_composed, delta_composed, leakage_composed)

    def is_acceptable(self, threshold_epsilon: float = 1.0,
                     threshold_delta: float = 1e-5) -> bool:
        """Check if privacy budget is within acceptable limits"""
        return self.epsilon <= threshold_epsilon and self.delta <= threshold_delta


class ComposablePrivacyRouter:
    """Router với privacy algebra - track tổng privacy loss"""

    def __init__(self, base_epsilon: float = 0.1, base_delta: float = 1e-6):
        self.base_epsilon = base_epsilon
        self.base_delta = base_delta
        self.privacy_ledger: Dict[str, List[PrivacyBudget]] = {}

    def compute_query_privacy_cost(self, query: np.ndarray,
                                   nodes: List[str]) -> Dict[str, PrivacyBudget]:
        """
        Tính privacy cost cho mỗi node
        Mỗi node thấy một subset khác nhau của query
        """
        costs = {}
        query_sensitivity = np.linalg.norm(query)

        for node_id in nodes:
            # Node-specific leakage (một số node thấy nhiều hơn)
            # Ví dụ: premium nodes thấy toàn bộ, free nodes chỉ thấy 30%
            visibility = self._get_node_visibility(node_id)

            epsilon = self.base_epsilon / visibility  # Càng thấy nhiều, ε càng cao
            delta = self.base_delta
            leakage = query * visibility  # Leakage vector

            costs[node_id] = PrivacyBudget(epsilon, delta, leakage)

        return costs

    def _get_node_visibility(self, node_id: str) -> float:
        """Node tier → visibility ratio"""
        # Mock: trong thực tế dựa vào node reputation/tier
        return np.random.uniform(0.3, 1.0)

    def track_privacy_usage(self, user_id: str, node_id: str,
                           budget: PrivacyBudget):
        """Track cumulative privacy loss per user"""
        if user_id not in self.privacy_ledger:
            self.privacy_ledger[user_id] = []

        self.privacy_ledger[user_id].append(budget)

    def get_remaining_budget(self, user_id: str) -> PrivacyBudget:
        """Get user's remaining privacy budget"""
        if user_id not in self.privacy_ledger:
            return PrivacyBudget(0.0, 0.0, np.zeros(10))

        # Compose all past budgets
        total_budget = self.privacy_ledger[user_id][0]
        for budget in self.privacy_ledger[user_id][1:]:
            total_budget = total_budget.compose(budget)

        return total_budget


# ============= #7: COUNTERFACTUAL CREDIT ASSIGNMENT =============
class CounterfactualCreditAssigner:
    """
    Causal inference để gán credit chính xác
    "Node X đóng góp bao nhiêu vào kết quả cuối?"
    """

    def __init__(self):
        self.history = deque(maxlen=1000)

    def compute_shapley_credit(self, selected_nodes: List[str],
                               node_contributions: Dict[str, float],
                               final_reward: float) -> Dict[str, float]:
        """
        Simplified Shapley value cho credit assignment
        Credit(i) = Σ [V(S ∪ {i}) - V(S)] / |all subsets|
        """
        n = len(selected_nodes)
        credits = {node: 0.0 for node in selected_nodes}

        # Sample subsets (full Shapley is 2^n, too expensive)
        num_samples = min(100, 2 ** n)

        for _ in range(num_samples):
            # Random subset
            subset_size = np.random.randint(0, n)
            subset = np.random.choice(selected_nodes, subset_size, replace=False).tolist()

            for node in selected_nodes:
                if node not in subset:
                    # Marginal contribution: V(S ∪ {node}) - V(S)
                    with_node = self._estimate_coalition_value(
                        subset + [node], node_contributions
                    )
                    without_node = self._estimate_coalition_value(
                        subset, node_contributions
                    )
                    marginal = with_node - without_node

                    credits[node] += marginal / num_samples

        # Normalize to sum to final_reward
        total_credit = sum(credits.values())
        if total_credit > 0:
            credits = {k: v / total_credit * final_reward for k, v in credits.items()}

        return credits

    def _estimate_coalition_value(self, coalition: List[str],
                                  contributions: Dict[str, float]) -> float:
        """
        Estimate value of a coalition
        V(S) = f(individual contributions, synergies)
        """
        if not coalition:
            return 0.0

        # Simple model: weighted average with diminishing returns
        values = [contributions.get(node, 0.0) for node in coalition]
        base_value = np.mean(values)

        # Synergy bonus (ensemble diversity)
        diversity_bonus = np.std(values) * 0.1 if len(values) > 1 else 0.0

        return base_value + diversity_bonus

    def estimate_counterfactual_reward(self, selected_nodes: List[str],
                                      node_to_remove: str,
                                      observed_reward: float) -> float:
        """
        Ước lượng: "Nếu không có node X thì reward là bao nhiêu?"
        Dùng historical data để estimate
        """
        # Find similar past decisions without this node
        similar_without_node = [
            record for record in self.history
            if node_to_remove not in record['nodes']
            and len(set(record['nodes']) & set(selected_nodes)) >= len(selected_nodes) // 2
        ]

        if not similar_without_node:
            # No data: assume average penalty
            return observed_reward * 0.8

        # Average reward of similar decisions
        avg_reward = np.mean([r['reward'] for r in similar_without_node])
        return avg_reward

    def record_decision(self, nodes: List[str], reward: float):
        """Record decision for future counterfactual estimates"""
        self.history.append({'nodes': nodes, 'reward': reward})


# ============= #2: MECHANISM DESIGN (SIMPLIFIED) =============
class IncentiveCompatibleScorer:
    """
    Proper scoring rules để incentivize truthful reporting
    Node tối ưu lợi ích ⟺ report đúng confidence
    """

    def brier_score(self, predicted_confidence: float,
                   actual_success: bool) -> float:
        """
        Brier score: proper scoring rule
        Score = -(p - y)²
        """
        y = 1.0 if actual_success else 0.0
        return -(predicted_confidence - y) ** 2

    def log_score(self, predicted_confidence: float,
                 actual_success: bool) -> float:
        """
        Log score: another proper scoring rule
        Score = log(p) if success else log(1-p)
        """
        p = np.clip(predicted_confidence, 1e-8, 1 - 1e-8)
        if actual_success:
            return np.log(p)
        else:
            return np.log(1 - p)

    def compute_node_reward(self, node_confidence: float,
                           actual_success: bool,
                           base_reward: float,
                           slashing_rate: float = 0.5) -> float:
        """
        Reward mechanism:
        - Proper scoring rule reward
        - Slashing if overconfident but wrong
        """
        # Proper scoring component
        scoring_reward = self.brier_score(node_confidence, actual_success)

        # Slashing component: high confidence + wrong = severe penalty
        if not actual_success and node_confidence > 0.7:
            slashing_penalty = slashing_rate * base_reward * node_confidence
        else:
            slashing_penalty = 0.0

        total_reward = base_reward * (1 + scoring_reward) - slashing_penalty
        return max(0.0, total_reward)  # Non-negative


# ============= #8: PROOF-CARRYING DECISIONS =============
@dataclass
class RoutingProof:
    """
    Self-contained proof of routing decision
    Auditable, reproducible, verifiable
    """
    decision_id: str
    timestamp: float
    query_hash: str
    selected_nodes: List[str]

    # Constraints satisfied
    latency_constraint: Tuple[float, float]  # (required, actual)
    cost_constraint: Tuple[float, float]
    privacy_constraint: Tuple[float, float]

    # Scores breakdown
    node_scores: Dict[str, Dict[str, float]]  # {node: {factor: score}}
    final_weights: np.ndarray

    # Privacy accounting
    privacy_budget_used: PrivacyBudget

    # Signature (zkVM proof in production)
    proof_hash: str

    def verify_constraints(self) -> bool:
        """Verify all constraints were satisfied"""
        latency_ok = self.latency_constraint[1] <= self.latency_constraint[0]
        cost_ok = self.cost_constraint[1] <= self.cost_constraint[0]
        # Lower epsilon is better (more private), so actual must be <= required max.
        privacy_ok = self.privacy_constraint[1] <= self.privacy_constraint[0]

        return latency_ok and cost_ok and privacy_ok

    def to_audit_log(self) -> Dict:
        """Export as JSON for auditing"""
        return {
            'decision_id': self.decision_id,
            'timestamp': self.timestamp,
            'query_hash': self.query_hash,
            'selected_nodes': self.selected_nodes,
            'constraints': {
                'latency': {'required': self.latency_constraint[0],
                          'actual': self.latency_constraint[1]},
                'cost': {'required': self.cost_constraint[0],
                       'actual': self.cost_constraint[1]},
                'privacy': {'required': self.privacy_constraint[0],
                          'actual': self.privacy_constraint[1]}
            },
            'scores': self.node_scores,
            'weights': self.final_weights.tolist(),
            'privacy_budget': {
                'epsilon': self.privacy_budget_used.epsilon,
                'delta': self.privacy_budget_used.delta
            },
            'proof_hash': self.proof_hash,
            'constraints_satisfied': self.verify_constraints()
        }


# ============= INTEGRATED BREAKTHROUGH ROUTER =============
@dataclass
class AdvancedNode:
    peer_id: str
    reputation: float
    expertise: np.ndarray
    latency: float
    cost_per_query: float
    reported_confidence: float  # Self-reported confidence (for mechanism design)
    stake: float


class MathematicallyGroundedRouter:
    """
    Router với đảm bảo toán học:
    - Privacy algebra (composable DP)
    - Counterfactual credit
    - Incentive-compatible scoring
    - Proof-carrying decisions
    """

    def __init__(self, nodes: List[AdvancedNode]):
        self.nodes = {n.peer_id: n for n in nodes}

        # Privacy subsystem
        self.privacy_router = ComposablePrivacyRouter()

        # Credit assignment subsystem
        self.credit_assigner = CounterfactualCreditAssigner()

        # Mechanism design subsystem
        self.scorer = IncentiveCompatibleScorer()

        # Audit trail
        self.audit_trail: List[RoutingProof] = []

    def route_with_guarantees(self, query: np.ndarray, user_id: str,
                             latency_max: float, cost_max: float,
                             privacy_min: float) -> Tuple[List[str], RoutingProof]:
        """
        Route with mathematical guarantees
        Returns selected nodes + auditable proof
        """
        decision_id = hashlib.sha256(
            f"{user_id}:{time.time()}".encode()
        ).hexdigest()[:16]

        query_hash = hashlib.sha256(query.tobytes()).hexdigest()[:16]

        # 1. PRIVACY BUDGET CHECK
        remaining_budget = self.privacy_router.get_remaining_budget(user_id)
        if not remaining_budget.is_acceptable():
            raise ValueError(f"User {user_id} exceeded privacy budget")

        # 2. COMPUTE PRIVACY COSTS PER NODE
        node_ids = list(self.nodes.keys())
        privacy_costs = self.privacy_router.compute_query_privacy_cost(
            query, node_ids
        )

        # 3. CONSTRAINT SATISFACTION PROBLEM
        # Variables: x[i] ∈ {0,1} for each node
        # Constraints:
        #   Σ latency[i] * x[i] ≤ latency_max
        #   Σ cost[i] * x[i] ≤ cost_max
        #   min privacy[i] * x[i] ≥ privacy_min

        node_scores = {}
        feasible_nodes = []

        for node_id in node_ids:
            node = self.nodes[node_id]

            # Check hard constraints
            if (node.latency <= latency_max and
                node.cost_per_query <= cost_max and
                privacy_costs[node_id].epsilon <= privacy_min):

                # Compute multi-factor score
                semantic_sim = np.dot(query, node.expertise) / (
                    np.linalg.norm(query) * np.linalg.norm(node.expertise) + 1e-8
                )
                trust = node.reputation
                latency_score = 1.0 / (node.latency + 1.0)
                cost_score = 1.0 / (node.cost_per_query + 0.1)

                score_breakdown = {
                    'semantic': semantic_sim,
                    'trust': trust,
                    'latency': latency_score,
                    'cost': cost_score
                }

                final_score = (
                    0.4 * semantic_sim +
                    0.3 * trust +
                    0.2 * latency_score +
                    0.1 * cost_score
                )

                node_scores[node_id] = score_breakdown
                feasible_nodes.append((node_id, final_score))

        if not feasible_nodes:
            raise ValueError("No nodes satisfy constraints")

        # 4. SELECT TOP-K
        feasible_nodes.sort(key=lambda x: x[1], reverse=True)
        selected = [node_id for node_id, _ in feasible_nodes[:3]]

        # 5. TRACK PRIVACY USAGE
        for node_id in selected:
            self.privacy_router.track_privacy_usage(
                user_id, node_id, privacy_costs[node_id]
            )

        # 6. COMPUTE ACTUAL METRICS
        total_latency = sum(self.nodes[n].latency for n in selected)
        total_cost = sum(self.nodes[n].cost_per_query for n in selected)
        min_privacy = min(privacy_costs[n].epsilon for n in selected)

        # 7. CREATE PROOF
        proof = RoutingProof(
            decision_id=decision_id,
            timestamp=time.time(),
            query_hash=query_hash,
            selected_nodes=selected,
            latency_constraint=(latency_max, total_latency),
            cost_constraint=(cost_max, total_cost),
            privacy_constraint=(privacy_min, min_privacy),
            node_scores=node_scores,
            final_weights=np.array([0.4, 0.3, 0.2, 0.1]),
            privacy_budget_used=privacy_costs[selected[0]],  # Representative
            proof_hash=hashlib.sha256(
                f"{decision_id}:{selected}".encode()
            ).hexdigest()
        )

        self.audit_trail.append(proof)

        return selected, proof

    def learn_with_counterfactuals(self, selected_nodes: List[str],
                                  node_confidences: Dict[str, float],
                                  actual_successes: Dict[str, bool],
                                  observed_reward: float):
        """
        Learn from feedback với counterfactual credit assignment
        và incentive-compatible rewards
        """
        # 1. COUNTERFACTUAL CREDIT ASSIGNMENT
        node_contributions = {
            node: 1.0 if actual_successes[node] else 0.0
            for node in selected_nodes
        }

        credits = self.credit_assigner.compute_shapley_credit(
            selected_nodes, node_contributions, observed_reward
        )

        # 2. INCENTIVE-COMPATIBLE REWARDS
        for node_id in selected_nodes:
            confidence = node_confidences[node_id]
            success = actual_successes[node_id]
            base_reward = credits[node_id]

            # Compute reward với proper scoring rule + slashing
            final_reward = self.scorer.compute_node_reward(
                confidence, success, base_reward
            )

            print(f"  {node_id}: credit={base_reward:.3f}, "
                  f"confidence={confidence:.2f}, reward={final_reward:.3f}")

            # Update node reputation based on reward
            node = self.nodes[node_id]
            alpha = 0.1
            node.reputation = (1 - alpha) * node.reputation + alpha * (final_reward / base_reward)

        # 3. RECORD FOR FUTURE COUNTERFACTUALS
        self.credit_assigner.record_decision(selected_nodes, observed_reward)

    def export_audit_trail(self, filename: str = "audit_trail.json"):
        """Export audit trail for external verification"""
        import json
        audit_data = [proof.to_audit_log() for proof in self.audit_trail]
        with open(filename, 'w') as f:
            json.dump(audit_data, f, indent=2)
        print(f"Audit trail exported to {filename}")
