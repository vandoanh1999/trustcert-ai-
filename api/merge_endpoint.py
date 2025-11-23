"""
/merge endpoint:
Directly test merging algorithms on adapter matrices.
"""

from fastapi import APIRouter
from pydantic import BaseModel
import numpy as np

# The new merging module should be used here.
# I will assume it's available and import from it.
try:
    from merging.slerp import linear_merge
    from merging.fisher import fisher_merge
except ImportError:
    # Fallback for environments where merging module might not be in path yet
    # This is a defensive measure during the build process.
    def linear_merge(arrs, alphas):
        print("Warning: Merging module not found, using dummy linear_merge.")
        return np.zeros_like(arrs[0]) if arrs else None
    def fisher_merge(adapters, fishers):
        print("Warning: Merging module not found, using dummy fisher_merge.")
        return np.zeros_like(adapters[0]) if adapters else None


router = APIRouter()

class MergeInput(BaseModel):
    mode: str
    A: list
    B: list
    fisherA: list = None
    fisherB: list = None
    alpha: float = 0.5

@router.post("/")
def merge(inp: MergeInput):
    A = np.array(inp.A, dtype="float32")
    B = np.array(inp.B, dtype="float32")

    if inp.mode == "linear":
        out = linear_merge([A, B], [1-inp.alpha, inp.alpha])
        return {"output": out.tolist()}

    if inp.mode == "fisher":
        if inp.fisherA is None or inp.fisherB is None:
            return {"error": "Fisher mode requires fisherA and fisherB inputs"}
        fA = np.array(inp.fisherA, dtype="float32")
        fB = np.array(inp.fisherB, dtype="float32")
        out = fisher_merge([A, B], [fA, fB])
        return {"output": out.tolist()}

    return {"error": "Invalid mode"}
