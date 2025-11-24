"""
Genesis Core V4 - Full Pipeline Self-Test
This script verifies that all V4 pillars can initialize and interact correctly.
"""
import os
import numpy as np
import json

# Set PYTHONPATH before local imports
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from router.router import OracleBrain
from weightindex.indexer import PersistentIndex
from synthesizer.main import Synthesizer
# from inference.genesis_inference_core import ChimeraCore # Conceptual

print("--- Running Genesis Core V4 Full Self-Test ---")
has_error = False

# --- Pillar 3: Oracle Brain Initialization ---
print("\n[1] Testing Oracle Brain Initialization...")
try:
    # We need a dummy L2 model for the test to pass in a CI environment
    dummy_l2_path = "l2_router_model/final_model"
    if not os.path.exists(dummy_l2_path):
        print("Creating dummy L2 model for test...")
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        dummy_tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
        dummy_model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=3)
        dummy_model.save_pretrained(dummy_l2_path)
        dummy_tokenizer.save_pretrained(dummy_l2_path)
        dummy_mappings = {"id2label": {"0": "legal", "1": "medical", "2": "code"}, "label2id": {"legal": 0, "medical": 1, "code": 2}}
        with open(os.path.join(dummy_l2_path, "label_mappings.json"), "w") as f: json.dump(dummy_mappings, f)

    oracle_brain = OracleBrain(l2_model_path=dummy_l2_path)
    print("[OK] Oracle Brain initialized.")
except Exception as e:
    print(f"[FAIL] Oracle Brain initialization failed: {e}")
    has_error = True
    sys.exit(1)

# --- Test Other Components ---
print("\n[2] Testing Other Component Initializations...")
try:
    index = PersistentIndex()
    synthesizer = Synthesizer()
    print("[OK] WeightIndex and Synthesizer initialized.")
except Exception as e:
    print(f"[FAIL] Component initialization failed: {e}")
    has_error = True
    sys.exit(1)

# --- Test V4 Pipeline ---
print("\n[3] Testing Full V4 Pipeline...")
test_query = "How do I write a 'hello world' function in Python?"
try:
    # 1. Oracle Brain
    query_vec, domain_probs = oracle_brain.route(test_query)
    assert query_vec.shape == (384,), "Query vector shape is incorrect."
    assert "code" in domain_probs, "Domain probabilities are missing."
    print(f"[OK] Oracle Brain returned vector and probabilities.")

    # 2. WeightIndex
    candidates = index.search(query_vec, topk=1)
    assert len(candidates) > 0, "WeightIndex returned no candidates."
    print(f"[OK] WeightIndex found candidate: {candidates[0]['id']}")

    # 3. Synthesizer
    adapter_paths = [f"adapters/expert_{c['meta']['domain']}/adapter.safetensors" for c in candidates]
    synthesized_model = synthesizer.synthesize(adapter_paths)
    assert synthesized_model is not None, "Synthesizer returned None."
    assert len(synthesized_model) > 0, "Synthesized model is empty."
    print("[OK] Synthesizer created a new model.")

except Exception as e:
    print(f"[FAIL] V4 pipeline test failed: {e}")
    has_error = True
    sys.exit(1)

# --- Final Result ---
if not has_error:
    print("\n--- V4 Self-Test Passed Successfully! ---")
else:
    print("\n--- V4 Self-Test Failed. ---")
    sys.exit(1)
