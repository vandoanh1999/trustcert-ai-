"""
Linear / SLERP-style merging utilities.

Notes:
- For adapters (small tensors): linear weighted average is often effective.
- slerp_vec provided for vector interpolation (session embedding style).
"""
import numpy as np
from .utils import weighted_sum
from typing import List

def linear_merge(arrs: List[np.ndarray], alphas: List[float] = None) -> np.ndarray:
    """
    Weighted linear merge of numpy arrays (same shape).
    alphas length must match arrs; defaults to equal weights.
    """
    if alphas is None:
        alphas = [1.0] * len(arrs)
    return weighted_sum(arrs, alphas)

def slerp_vec(v1: np.ndarray, v2: np.ndarray, t: float) -> np.ndarray:
    """
    Spherical linear interpolation between two vectors.
    Approximate, numerically stable.
    """
    v1 = v1.astype("float64")
    v2 = v2.astype("float64")
    n1 = np.linalg.norm(v1) + 1e-12
    n2 = np.linalg.norm(v2) + 1e-12
    v1n = v1 / n1
    v2n = v2 / n2
    dot = np.clip(np.dot(v1n, v2n), -1.0, 1.0)
    omega = np.arccos(dot)
    if np.abs(omega) < 1e-6:
        return v1.astype("float32")
    so = np.sin(omega)
    out = (np.sin((1.0 - t) * omega) / so) * v1 + (np.sin(t * omega) / so) * v2
    return out.astype("float32")
