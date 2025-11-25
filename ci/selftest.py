"""
Genesis Core V6 - The Sentient Forge Full Self-Test

This script is the ultimate verification of the V6 architecture.
It ensures all pillars work in concert:
- Oracle Brain with Reputation
- WeightIndex
- Aurora Trust (Reputation, VC, ZK Proofs)
- Fusion Forge (Hypercontroller)
- The full, integrated dispatch pipeline.
"""
import os
import json
import torch
import sys

# --- Setup ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- V6 Pillar Imports ---
from router.router import OracleBrain
from weightindex.indexer import PersistentIndex
from fusion_forge.hypercontroller import HypercontrollerV2
from aurora_trust.reputation_vc import get_reputation, load_reputation_db, save_reputation_db
from aurora_trust.zk_proofs import CausalEffectCircuit, zk_prove, zk_verify

def setup_test_environment():
    """Creates all necessary dummy files for a successful test run."""
    print("--- Setting up V6 Test Environment ---")

    # 1. Dummy L2 Router Model
    dummy_l2_path = "l2_router_model/final_model"
    if not os.path.exists(dummy_l2_path):
        print("Creating dummy L2 model...")
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        dummy_tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
        dummy_model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=2)
        dummy_model.save_pretrained(dummy_l2_path)
        dummy_tokenizer.save_pretrained(dummy_l2_path)
        dummy_mappings = {"id2label": {"0": "tech", "1": "legal"}, "label2id": {"tech": 0, "legal": 1}}
        with open(os.path.join(dummy_l2_path, "label_mappings.json"), "w") as f: json.dump(dummy_mappings, f)

    # 2. Dummy Reputation Database
    print("Creating dummy reputation DB...")
    save_reputation_db({"expert_code_v1": 0.75, "expert_math_v1": 0.6})

def run_test():
    print("\n--- Running Genesis Core V6 Full Self-Test ---")
    has_error = False

    # 1. Component Initialization
    print("\n[1] Initializing V6 Components...")
    try:
        oracle_brain = OracleBrain()
        index = PersistentIndex()
        hypercontroller = HypercontrollerV2(intent_dim=32, hidden_dim=64, num_blocks=2, max_candidates=4)
        print("[OK] All components initialized.")
    except Exception as e:
        print(f"[FAIL] Initialization failed: {e}")
        sys.exit(1)

    # 2. V6 Pipeline Test
    print("\n[2] Testing Full V6 Pipeline...")
    test_query = "How to implement a binary search tree in Python?"
    try:
        # Oracle Brain (Routing)
        query_vec, _ = oracle_brain.route(test_query)

        # WeightIndex (Candidate Selection)
        candidates = index.search(query_vec.cpu().numpy(), topk=2)
        assert len(candidates) > 0, "WeightIndex found no candidates."
        print(f"  - Found candidates: {[c['id'] for c in candidates]}")

        # Oracle Brain (Context Gathering with Reputation)
        intent_vec, rep_tensor = oracle_brain.gather_context_for_forge(test_query, candidates)
        assert rep_tensor.numel() == len(candidates), "Reputation tensor shape mismatch."
        print(f"  - Gathered reputation scores: {rep_tensor.numpy().round(2)}")

        # Hypercontroller (Decision Making)
        alphas, _ = hypercontroller(intent_vec, rep_tensor, len(candidates))
        assert alphas.numel() == len(candidates), "Alphas shape mismatch."
        print(f"  - Hypercontroller chose alphas: {alphas.detach().numpy().round(3)}")

        # Aurora Trust (ZK Proof Simulation)
        circuit = CausalEffectCircuit(eps=0.1)
        proof = zk_prove(tau_forge=0.25, tau_target=0.28, circuit=circuit)
        is_verified = zk_verify(proof)
        assert is_verified, "ZK Proof verification failed."
        print("  - ZK Proof for Causal Integrity: VERIFIED")

        # Aurora Trust (Reputation Update Simulation)
        from aurora_trust.reputation_vc import compute_and_issue_contributions
        contributions = compute_and_issue_contributions(
            [c['id'] for c in candidates],
            alphas,
            {"loss_ci": 0.02, "tda_reg": 0.03}
        )
        assert len(contributions) == len(candidates), "Contribution calculation failed."
        print(f"  - Issued VCs and updated reputation for {len(contributions)} experts.")

    except Exception as e:
        print(f"[FAIL] V6 pipeline test failed: {e}")
        has_error = True
        sys.exit(1)

    # Final Result
    if not has_error:
        print("\n--- V6 Self-Test Passed Successfully! ---")
    else:
        print("\n--- V6 Self-Test Failed. ---")
        sys.exit(1)

if __name__ == "__main__":
    setup_test_environment()
    run_test()
