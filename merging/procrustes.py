"""
Orthogonal Procrustes alignment utilities.

Use case:
- Align layer matrices A to B before merging when permutation/rotation differences exist.
- Works on 2D matrices (n x m). For higher dims, flatten/reshape per-layer.
"""
import numpy as np

def orthogonal_procrustes(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """
    Find orthogonal matrix R minimizing ||A R - B||_F and return A @ R.
    A and B should be 2D arrays with same shape.
    """
    if A.ndim != 2 or B.ndim != 2:
        raise ValueError("A and B must be 2D matrices")
    if A.shape != B.shape:
        raise ValueError("A and B must have same shape")
    # Compute A^T B
    M = A.T @ B
    U, _, Vt = np.linalg.svd(M, full_matrices=False)
    R = U @ Vt
    return (A @ R).astype("float32")
