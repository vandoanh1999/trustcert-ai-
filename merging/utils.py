"""
Utility helpers for merging module.
"""
import numpy as np
from typing import List

def ensure_same_shape(arrs: List[np.ndarray]):
    if not arrs:
        raise ValueError("No arrays provided")
    base = arrs[0].shape
    for a in arrs:
        if a.shape != base:
            raise ValueError(f"Shape mismatch: expected {base}, got {a.shape}")

def weighted_sum(arrs: List[np.ndarray], weights: List[float]):
    ensure_same_shape(arrs)
    total = sum(weights) if sum(weights) != 0 else 1.0
    acc = None
    for a, w in zip(arrs, weights):
        if acc is None:
            acc = a.astype("float32") * (w / total)
        else:
            acc = acc + a.astype("float32") * (w / total)
    return acc
