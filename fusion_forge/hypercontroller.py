"""
Fusion Forge: The Hypercontroller V2

This module contains the core learning component of the Sentient Forge.
The HypercontrollerV2 is a differentiable neural network that learns to
optimally combine expert adapters based on a variety of inputs.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple

# --- Supporting Neural Modules ---

class IntentEncoder(nn.Module):
    """A simple, deterministic, and trainable encoder for text queries."""
    def __init__(self, d_intent=32, token_emb=64, device='cpu'):
        super().__init__()
        self.char_embed = nn.Embedding(256, token_emb)
        nn.init.normal_(self.char_embed.weight, mean=0.0, std=0.02)
        self.proj = nn.Linear(token_emb, d_intent)
        self.device = device

    def forward(self, text: str) -> torch.Tensor:
        b = text.encode("utf8")[:128]
        if len(b) == 0:
            idx = torch.empty(0, dtype=torch.long, device=self.device)
            v = torch.zeros(self.proj.out_features, device=self.device)
        else:
            idx = torch.tensor([c for c in b], dtype=torch.long, device=self.device)
            v = self.char_embed(idx).mean(dim=0)
            v = self.proj(v)
        return torch.tanh(v)

# --- The Main Hypercontroller ---

class HypercontrollerV2(nn.Module):
    """
    Learns to produce optimal `alphas` (mixing weights) and `multipliers`
    (per-layer modulation) for combining expert adapters.
    It is influenced by the query's intent, and the reputation of the candidates.
    """
    def __init__(self, intent_dim: int, hidden_dim: int, num_blocks: int, max_candidates: int = 8):
        super().__init__()
        self.fc1 = nn.Linear(intent_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc_alpha = nn.Linear(hidden_dim, max_candidates)
        self.fc_multi = nn.Linear(hidden_dim, num_blocks * max_candidates)

        # Learnable parameters to weigh the influence of external scores
        self.w_rep = nn.Parameter(torch.tensor(1.0))

        self.num_blocks = num_blocks
        self.max_candidates = max_candidates

    def forward(
        self,
        intent_vector: torch.Tensor,
        reputation_scores: torch.Tensor,
        num_candidates: int
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            intent_vector: A tensor representing the user's query.
            reputation_scores: A tensor of reputation scores for the candidates.
            num_candidates: The actual number of candidates being considered (C).

        Returns:
            A tuple of (alphas, multipliers).
        """
        if reputation_scores.numel() != num_candidates:
            raise ValueError("Number of reputation scores must match the number of candidates.")

        h = torch.tanh(self.fc1(intent_vector))
        h = torch.tanh(self.fc2(h))

        # --- Alpha (Mixing Weight) Generation ---
        raw_alphas = self.fc_alpha(h)[:num_candidates]

        # Bias the raw alpha scores using the experts' reputation
        # The learnable weight `w_rep` controls how much reputation matters.
        reputation_bias = self.w_rep * (reputation_scores - reputation_scores.mean())
        biased_alphas = raw_alphas + reputation_bias

        # Softmax to get the final mixing weights
        alphas = F.softmax(biased_alphas, dim=0)

        # --- Multiplier Generation ---
        raw_multipliers = self.fc_multi(h).view(self.num_blocks, self.max_candidates)[:, :num_candidates]
        # Sigmoid maps the outputs to a (0, 1) range, which we can scale.
        # This prevents extreme values and stabilizes training.
        multipliers = 0.5 + torch.sigmoid(raw_multipliers)  # Range ~[0.5, 1.5]

        return alphas, multipliers
