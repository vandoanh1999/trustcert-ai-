"""
Genesis Core V3 - Pipeline Demo
Demonstrates the full V3 pipeline:
1. Route text using the real SemanticRouter.
2. Query the production-ready WeightIndex.
3. Synthesize a new model using the advanced Synthesizer.
"""
import os
from router.router import SemanticRouter
from weightindex.indexer import PersistentIndex
from synthesizer.main import Synthesizer

# --- Initialization ---
print("Initializing Genesis Core V3 components...")
router = SemanticRouter()
index = PersistentIndex()
synthesizer = Synthesizer()
print("Initialization complete.")
print("-" * 20)

# --- Demo Input ---
text = "Write a Python function that calculates the factorial of a number."

# --- Pipeline Execution ---
print(f"Input Text: '{text}'")

# 1. Routing
domain, query_vec = router.route(text)
print(f"Domain Detected: {domain}")

# 2. Candidate Search
print("Searching for candidate adapters...")
candidates = index.search(query_vec, topk=2)
if not candidates:
    print("No candidates found. Exiting.")
    exit()
print(f"Found Candidates: {[c['id'] for c in candidates]}")

# 3. Synthesis
print("Preparing for synthesis...")
adapter_paths = []
for c in candidates:
    # This logic mirrors the dispatch endpoint to find adapter files
    domain_folder = c['meta'].get('domain', 'general')
    expert_folder_name = f"expert_{domain_folder}"
    # Using the dummy file created by setup.sh for this demo
    path = os.path.join("adapters", expert_folder_name, "adapter.safetensors")
    if os.path.exists(path):
        adapter_paths.append(path)
    else:
        print(f"Warning: Adapter file not found at {path}")

if not adapter_paths:
    print("Could not find adapter files for candidates. Exiting.")
    exit()

synthesized_model = synthesizer.synthesize(adapter_paths)
if synthesized_model:
    output_path = "demo_synthesized_model.safetensors"
    synthesizer.save_model(synthesized_model, output_path)

    first_key = next(iter(synthesized_model))
    print("\n--- Synthesis Successful ---")
    print(f"Synthesized model contains {len(synthesized_model)} layers.")
    print(f"Preview of first layer ('{first_key}'):")
    print(synthesized_model[first_key][:2, :2])
    print(f"Full model saved to: {output_path}")
else:
    print("\n--- Synthesis Failed ---")
