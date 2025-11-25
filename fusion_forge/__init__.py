"""
Genesis Core V6: The Fusion Forge

This is the new heart of Genesis, a Sentient Forge capable of learning
how to optimally synthesize new AI experts.
"""

from .hypercontroller import HypercontrollerV2, IntentEncoder
from .aurora_loss import compute_ci_loss, compute_tda_reg
from .forge_pipeline import TinyForgeableModel, apply_low_rank_forging, run_forge_training_step

__all__ = [
    "HypercontrollerV2",
    "IntentEncoder",
    "compute_ci_loss",
    "compute_tda_reg",
    "TinyForgeableModel",
    "apply_low_rank_forging",
    "run_forge_training_step"
]
