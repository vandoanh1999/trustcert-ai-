from pydantic import BaseModel
import numpy as np
from typing import List, Dict

# Use Pydantic for automatic validation and serialization
class Node(BaseModel):
    peer_id: str
    reputation: float
    expertise: List[float]  # Use a list for JSON compatibility
    latency: float

class User:
    def __init__(self, user_id: str, tier: str = "standard"):
        self.user_id = user_id
        self.tier = tier

class PersonalizedRouter:
    """
    Intelligently routes queries to the best nodes based on a multi-factor
    scoring algorithm.
    """
    def __init__(self, nodes: List[Node]):
        self.nodes = {node.peer_id: node for node in nodes}
        # Tier-based weights: [reputation, semantic_similarity, 1/latency]
        # Semantic similarity should be the most important factor.
        self.tier_weights = {
            "free": np.array([0.3, 0.5, 0.2]),
            "standard": np.array([0.2, 0.6, 0.2]),
            "premium": np.array([0.1, 0.7, 0.2]),
        }

    def _cosine_similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """Calculates the cosine similarity between two vectors."""
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

    def _normalize(self, scores: np.ndarray) -> np.ndarray:
        """Normalizes scores to a 0-1 range."""
        min_val = np.min(scores)
        max_val = np.max(scores)
        if max_val == min_val:
            return np.zeros_like(scores)
        return (scores - min_val) / (max_val - min_val)

    def route_query(self, user: User, query_embedding: np.ndarray) -> Node:
        """
        Selects the best node for a given user and query.
        """
        if not self.nodes:
            raise ValueError("No nodes available to route to.")

        scores = []
        node_list = list(self.nodes.values())

        for node in node_list:
            # 1. Calculate semantic similarity (convert list to numpy array)
            expertise_vector = np.array(node.expertise)
            semantic_similarity = self._cosine_similarity(query_embedding, expertise_vector)

            # 2. Get reputation and latency
            reputation = node.reputation
            # Use inverse latency, so higher is better
            inverse_latency = 1.0 / node.latency if node.latency > 0 else 0.0

            scores.append([reputation, semantic_similarity, inverse_latency])

        scores_matrix = np.array(scores)

        # Normalize each factor across all nodes
        normalized_scores = np.zeros_like(scores_matrix)
        for i in range(scores_matrix.shape[1]):
            normalized_scores[:, i] = self._normalize(scores_matrix[:, i])

        # Get the weights for the user's tier
        weights = self.tier_weights.get(user.tier, self.tier_weights["standard"])

        # Calculate the final weighted score for each node
        final_scores = np.dot(normalized_scores, weights)

        # Select the node with the highest score
        best_node_index = np.argmax(final_scores)
        return node_list[best_node_index]

if __name__ == '__main__':
    # --- Example Usage ---
    # Create some dummy nodes
    nodes = [
        Node(peer_id="node_A", reputation=0.9, expertise=[0.8, 0.2, 0.1], latency=50), # High rep, good match
        Node(peer_id="node_B", reputation=0.7, expertise=[0.1, 0.9, 0.2], latency=100), # Lower rep, bad match
        Node(peer_id="node_C", reputation=0.8, expertise=[0.7, 0.3, 0.1], latency=20), # Good rep, good match, low latency
    ]

    # Create a router
    router = PersonalizedRouter(nodes)

    # Create a user and a query
    user = User("user_123", tier="premium")
    query_embedding = np.array([0.85, 0.15, 0.05]) # A query that strongly matches node A & C

    # Route the query
    best_node = router.route_query(user, query_embedding)

    print(f"User Tier: {user.tier}")
    print(f"Query Embedding: {query_embedding}")
    print(f"Best node selected: {best_node.peer_id}")
    print(f" -> Reputation: {best_node.reputation}")
    print(f" -> Latency: {best_node.latency}ms")
    print(f" -> Expertise Vector: {best_node.expertise}")
