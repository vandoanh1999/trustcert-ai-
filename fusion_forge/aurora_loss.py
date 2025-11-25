"""
Fusion Forge: The Aurora Loss

This module implements the "conscience" of the Sentient Forge.
The Aurora Loss is a composite loss function that guides the Hypercontroller's
learning process. It balances three critical objectives:
1.  **Task Fidelity (Task Loss):** Is the synthesized model still good at the
    base task? (Not implemented here, assumed external)
2.  **Causal Integrity (CI Loss):** Does the model break fundamental causal
    rules? We use a trusted oracle (SCM) to check this.
3.  **Topological Stability (TDA Reg):** Does the model's internal structure
    (topology) remain stable, or has it become chaotic? We use a proxy
    based on the spectrum of its activation matrices.
"""
import torch
import torch.nn.functional as F
from typing import Callable, List, Tuple, Optional

# Integrate with our new ZK Proof system for penalties
from aurora_trust.zk_proofs import CausalEffectCircuit, compute_zk_penalty

DTYPE = torch.float32

# --- Causal Integrity (CI) Loss ---

def scm_oracle_predict(probe_batch: torch.Tensor) -> torch.Tensor:
    """
    Stub for a trusted Structural Causal Model (SCM) oracle.
    In a real system, this would be an external, audited model that provides a
    "ground truth" for causal effects (Interventional Treatment Effects, ITE).
    For this simulation, it returns a fixed target value.
    """

    return torch.tensor(0.3, dtype=DTYPE, device=probe_batch.device)

def compute_ci_loss(
    forged_predictions: torch.Tensor,
    probe_batch: torch.Tensor
) -> torch.Tensor:
    """
    Computes the Causal Integrity (CI) loss.
    It measures the difference between the causal effect observed in the
    synthesized model (`tau_forge`) and the effect predicted by a trusted
    SCM oracle (`tau_target`).
    """
    # 1. Calculate tau_forge from the synthesized model's predictions
    B = forged_predictions.shape[0]
    if B % 2 != 0:
        raise ValueError("CI loss requires an even-sized batch for pairwise comparison.")

    half = B // 2
    control_preds = forged_predictions[:half]
    treat_preds = forged_predictions[half:]
    tau_forge = (treat_preds - control_preds).mean()

    # 2. Query the trusted SCM oracle to get the target causal effect
    tau_target = scm_oracle_predict(probe_batch)

    # 3. The CI loss is the squared difference between the two
    loss_ci = F.mse_loss(tau_forge, tau_target.to(tau_forge.device))

    # 4. (V6 Evolution) Add a ZK penalty if causal integrity cannot be proven
    zk_circuit = CausalEffectCircuit(eps=1e-5)
    zk_penalty = compute_zk_penalty(tau_forge, tau_target, zk_circuit)

    return loss_ci + zk_penalty

# --- Topological Data Analysis (TDA) Regularization ---

def compute_tda_reg(
    base_activations: torch.Tensor,
    forged_activations: torch.Tensor,
    k: int = 12
) -> torch.Tensor:
    """
    Computes the Topological Data Analysis (TDA) regularization term.
    This acts as a proxy for topological stability by comparing the singular
    value spectra of the base model's and the forged model's activations.
    A large divergence in the spectra suggests a chaotic change in the
    model's internal structure.
    """
    if base_activations.shape != forged_activations.shape:
        raise ValueError("Base and forged activations must have the same shape.")

    # Center the activation matrices
    base_centered = base_activations - base_activations.mean(dim=0, keepdim=True)
    forged_centered = forged_activations - forged_activations.mean(dim=0, keepdim=True)

    try:
        # Get the singular values (spectra) of the matrices
        _, s_base, _ = torch.linalg.svd(base_centered, full_matrices=False)
        _, s_forged, _ = torch.linalg.svd(forged_centered, full_matrices=False)
    except Exception:
        # Fallback for older torch versions
        s_base = torch.svd(base_centered).S
        s_forged = torch.svd(forged_centered).S

    # Compare the top-k singular values
    k_min = min(k, s_base.numel(), s_forged.numel())
    s_base_top_k = s_base[:k_min]
    s_forged_top_k = s_forged[:k_min]

    # The regularization term is the mean squared relative difference
    # between the spectra.
    relative_diff = (s_forged_top_k / (s_base_top_k + 1e-6)) - 1.0
    tda_reg = torch.mean(relative_diff ** 2)

    return tda_reg
