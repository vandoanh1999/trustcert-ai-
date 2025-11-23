"""
Fisher-weighted merging (diagonal fisher approximation).

Expected inputs:
- adapters: list of numpy arrays (same shape)
- fishers: list of numpy arrays (same shape) containing fisher diagonal estimates for each adapter

Output: merged numpy array (float32)
"""
import numpy as np
from typing import List

def fisher_merge(adapters: List[np.ndarray], fishers: List[np.ndarray], eps: float = 1e-8) -> np.ndarray:
    if len(adapters) == 0:
        raise ValueError("No adapters provided")
    if len(adapters) != len(fishers):
        raise ValueError("Adapters and fishers must be same length")
    base_shape = adapters[0].shape
    for a in adapters:
        if a.shape != base_shape:
            raise ValueError("Adapter shape mismatch")
    for f in fishers:
        if f.shape != base_shape:
            raise ValueError("Fisher shape mismatch")
    numerator = np.zeros(base_shape, dtype="float64")
    denom = np.zeros(base_shape, dtype="float64")
    for a, f in zip(adapters, fishers):
        numerator += a.astype("float64") * f.astype("float64")
        denom += f.astype("float64")
    merged = numerator / (denom + eps)
    return merged.astype("float32")
