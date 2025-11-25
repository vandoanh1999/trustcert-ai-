"""
Genesis Core V5 - The Arbiter Era Self-Test
This script verifies the full, end-to-end V5 pipeline, including the
Arbiter's certification step.
"""
import os
import json
import numpy as np

# Set PYTHONPATH before local imports
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from router.router import OracleBrain
from weightindex.indexer import PersistentIndex
from synthesizer.main import Synthesizer
from arbiter import Arbiter

print("--- Running Genesis Core V5 Full Self-Test ---")
has_error = False

# --- Component Initialization ---
print("\n[1] Initializing All V5 Components...")
try:
    # Ensure a dummy L2 model exists for the test
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
    index = PersistentIndex()
    synthesizer = Synthesizer()
    arbiter = Arbiter()
    print("[OK] All V5 components initialized successfully.")
except Exception as e:
    print(f"[FAIL] Component initialization failed: {e}")
    sys.exit(1)

# --- V5 Pipeline Test ---
print("\n[2] Testing Full V5 Pipeline with Arbiter Certification...")
test_query = "Write a Python script to list all files in a directory."
try:
    # 1. Oracle Brain
    query_vec, domain_probs = oracle_brain.route(test_query)
    assert "code" in domain_probs

    # 2. WeightIndex
    candidates = index.search(query_vec, topk=1)
    assert len(candidates) > 0

    # 3. Synthesizer
    adapter_paths = [f"adapters/expert_{c['meta']['domain']}/adapter.safetensors" for c in candidates]
    synthesized_model = synthesizer.synthesize(adapter_paths)
    assert synthesized_model is not None

    # 4. (Simulated) Inference
    simulated_response = f"Generated response for: {test_query}"

    # 5. Arbiter
    metadata = {"candidates": [c['id'] for c in candidates]}
    report, certificate = arbiter.inspect_and_certify(test_query, simulated_response, metadata)

    print(f"[OK] Arbiter verification status: {report['status']}")
    assert report['status'] == "PASSED", "Arbiter safety check failed."
    assert certificate is not None, "Arbiter failed to generate a certificate."
    assert "signature" in certificate and "data_hash" in certificate, "Certificate format is invalid."
    print("[OK] Trust Certificate generated successfully.")

except Exception as e:
    print(f"[FAIL] V5 pipeline test failed: {e}")
    has_error = True
    sys.exit(1)

# --- Final Result ---
if not has_error:
    print("\n--- V5 Self-Test Passed Successfully! ---")
else:
    print("\n--- V5 Self-Test Failed. ---")
    sys.exit(1)
