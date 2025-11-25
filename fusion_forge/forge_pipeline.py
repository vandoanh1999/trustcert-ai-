"""
Fusion Forge: The Differentiable Forging Pipeline

This module orchestrates the entire process of synthesizing a new model
in a way that is end-to-end differentiable, allowing the Hypercontroller
to be trained.
"""
import torch
import torch.nn as nn
from typing import List, Tuple, Callable

# A simple base model for demonstration purposes
class TinyForgeableModel(nn.Module):
    def __init__(self, d_model=128, num_blocks=2):
        super().__init__()
        self.d_model = d_model
        self.num_blocks = num_blocks
        self.blocks = nn.ModuleList([
            nn.Sequential(nn.Linear(d_model, d_model), nn.ReLU())
            for _ in range(num_blocks)
        ])
        self.head = nn.Linear(d_model, 1)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, List[torch.Tensor]]:
        """Returns final prediction and a list of intermediate activations."""
        activations = []
        h = x
        for block in self.blocks:
            h = block(h)
            activations.append(h)
        return self.head(h), activations

def apply_low_rank_forging(
    base_model: TinyForgeableModel,
    input_tensor: torch.Tensor,
    expert_factors: List[List[Tuple[torch.Tensor, torch.Tensor, torch.Tensor]]],
    alphas: torch.Tensor,
    multipliers: torch.Tensor
) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    Applies the low-rank corrections during a forward pass. This entire
    function is differentiable.

    Returns:
        A tuple of (final_predictions, final_activations).
    """
    if not isinstance(base_model, TinyForgeableModel):
        raise TypeError("This forging pipeline is designed for TinyForgeableModel.")

    num_candidates = len(expert_factors)
    h = input_tensor
    final_activations = None

    for i, block in enumerate(base_model.blocks):
        h = block(h) # Base model's computation

        # --- Differentiable Forging Step ---
        # A correction is calculated based on the expert factors and the
        # Hypercontroller's outputs (alphas and multipliers), then added.
        correction = torch.zeros_like(h)
        for c_idx in range(num_candidates):
            U, S, Vt = expert_factors[c_idx][i]

            # Project, scale, and re-project
            projected = h @ Vt.T  # (B, r)
            scaled = projected * S.unsqueeze(0) # (B, r)
            reprojected = scaled @ U.T # (B, d_model)

            # Weigh the correction by alpha and multiplier
            coefficient = alphas[c_idx] * multipliers[i, c_idx]
            correction += coefficient * reprojected

        h = h + correction # Apply the forged correction
        final_activations = h

    predictions = base_model.head(h)
    return predictions, final_activations

# Wrapper for a complete training step
def run_forge_training_step(
    hypercontroller: nn.Module,
    base_model: TinyForgeableModel,
    intent_vector: torch.Tensor,
    reputation_scores: torch.Tensor,
    expert_factors: List,
    probe_batch: torch.Tensor,
    optimizer: torch.optim.Optimizer,
    loss_lambdas: dict
) -> dict:
    """
    Executes a single training step for the Hypercontroller.
    """
    from .aurora_loss import compute_ci_loss, compute_tda_reg

    optimizer.zero_grad()

    # 1. Get forging parameters from the Hypercontroller
    num_candidates = len(expert_factors)
    alphas, multipliers = hypercontroller(intent_vector, reputation_scores, num_candidates)

    # 2. Run the differentiable forging process
    forged_preds, forged_acts = apply_low_rank_forging(
        base_model, probe_batch, expert_factors, alphas, multipliers
    )
    forged_preds = forged_preds.view(-1)

    # 3. Get base model's behavior for comparison
    with torch.no_grad():
        base_preds, base_acts_list = base_model(probe_batch)
        base_preds = base_preds.view(-1)
        base_acts = base_acts_list[-1] # Use final layer activations

    # 4. Calculate Aurora Loss components
    task_loss = F.mse_loss(forged_preds, base_preds.detach())
    loss_ci = compute_ci_loss(forged_preds, probe_batch)
    tda_reg = compute_tda_reg(base_acts.detach(), forged_acts)

    # 5. Combine into the final Aurora Loss and backpropagate
    aurora_loss = (
        task_loss +
        loss_lambdas.get('ci', 1.0) * loss_ci +
        loss_lambdas.get('tda', 0.5) * tda_reg
    )
    aurora_loss.backward()
    optimizer.step()

    return {
        "total_loss": aurora_loss.item(),
        "task_loss": task_loss.item(),
        "loss_ci": loss_ci.item(),
        "tda_reg": tda_reg.item(),
        "alphas": alphas.detach().cpu().numpy()
    }
