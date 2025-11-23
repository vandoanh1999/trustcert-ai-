"""
Genesis Core V3 - Self Test
- Ensures V3 components initialize and interact correctly.
"""
import os
import numpy as np
from router.router import SemanticRouter
from weightindex.indexer import PersistentIndex
from synthesizer.main import Synthesizer

print("--- Running Genesis Core V3 Self-Test ---")

# 1. Initialize Components
print("Initializing components...")
try:
    router = SemanticRouter()
    index = PersistentIndex()
    synthesizer = Synthesizer()
    print("[OK] All components initialized.")
except Exception as e:
    print(f"[FAIL] Component initialization failed: {e}")
    exit(1)

# 2. Test Routing
print("\nTesting Router...")
text = "What was the primary cause of the American Civil War?"
domain, qv = router.route(text)
assert domain == "history", f"Domain mismatch, expected 'history', got '{domain}'"
assert qv.shape == (384,), f"Vector shape mismatch, expected (384,), got {qv.shape}"
print("[OK] Router produced correct domain and vector shape.")

# 3. Test Index Search
print("\nTesting WeightIndex...")
candidates = index.search(qv, topk=1)
assert len(candidates) > 0, "Index search returned no candidates."
assert "id" in candidates[0] and "meta" in candidates[0], "Candidate format is incorrect."
print(f"[OK] Index search returned {len(candidates)} candidate(s). Found: {candidates[0]['id']}")

# 4. Test Synthesizer
print("\nTesting Synthesizer...")
adapter_paths = []
for c in candidates:
    domain_folder = c['meta'].get('domain', 'general')
    expert_folder_name = f"expert_{domain_folder}"
    path = os.path.join("adapters", expert_folder_name, "adapter.safetensors")
    if os.path.exists(path):
        adapter_paths.append(path)

assert len(adapter_paths) > 0, "Could not find adapter files for synthesis test."
model_dict = synthesizer.synthesize(adapter_paths)
assert model_dict is not None, "Synthesis returned None."
assert len(model_dict) > 0, "Synthesized model has no layers."
first_layer = next(iter(model_dict.values()))
assert isinstance(first_layer, np.ndarray), "Synthesized layer is not a numpy array."
print("[OK] Synthesizer produced a valid model dictionary.")

print("\n--- Self-Test Passed Successfully! ---")
