"""
Quick test for merging algorithms.
"""

import numpy as np

# Defensive import for build process
try:
    from merging.slerp import linear_merge
    from merging.fisher import fisher_merge
except ImportError:
    print("Warning: Merging module not available for merge_test.py")
    # Define dummy functions so the script doesn't crash if run prematurely
    def linear_merge(arrs, alphas): return np.zeros_like(arrs[0])
    def fisher_merge(a, f): return np.zeros_like(a[0])


A = np.random.rand(4,4).astype("float32")
B = np.random.rand(4,4).astype("float32")

print("Linear merge:")
print(linear_merge([A, B], [0.5, 0.5]))

print("\nFisher merge:")
fA = np.random.rand(4,4).astype("float32")
fB = np.random.rand(4,4).astype("float32")
print(fisher_merge([A, B], [fA, fB]))
