"""
Genesis Core V4: The Central Dispatch Endpoint

This endpoint orchestrates the entire V4 pipeline:
1.  **Oracle Brain:** Get a semantic query vector and a probability
    distribution over domains.
2.  **WeightIndex:** Find the best candidate adapters, potentially from
    multiple high-probability domains.
3.  **Synthesizer:** Forge a new hybrid expert from the candidates.
4.  **Chimera Core:** (Conceptually) Load the synthesized adapter and
    generate a response.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from router.router import OracleBrain
from weightindex.indexer import PersistentIndex
from synthesizer.main import Synthesizer
# from inference.genesis_inference_core import ChimeraCore # Concept for full integration
import os

# --- V4 Component Initialization ---
# These are singletons and will be initialized once on startup
router = APIRouter()
oracle_brain = OracleBrain()
index = PersistentIndex()
synthesizer = Synthesizer()

# Conceptual: The Chimera Core would be initialized with a path to a base GGUF model
# CHIMERA_BASE_MODEL = os.environ.get("CHIMERA_BASE_MODEL", "path/to/your/model.gguf")
# if os.path.exists(CHIMERA_BASE_MODEL):
#     chimera_core = ChimeraCore(base_model_path=CHIMERA_BASE_MODEL)
# else:
#     chimera_core = None
#     print("Warning: Chimera Core base model not found. Inference will be disabled.")


class DispatchInput(BaseModel):
    text: str
    top_k_experts: int = 2
    domain_probability_threshold: float = 0.1 # Consider domains with >10% probability

class DispatchResponse(BaseModel):
    query: str
    domain_probabilities: Dict[str, float]
    selected_candidates: List[Dict]
    # synthesized_response: str # The final output from Chimera Core

router = APIRouter()

@router.post("/", response_model=DispatchResponse)
def dispatch(inp: DispatchInput):
    print(f"--- V4 Dispatch Request ---")
    print(f"Query: '{inp.text}'")

    # 1. Oracle Brain routes the query
    query_vec, domain_probs = oracle_brain.route(inp.text)
    print(f"Domain Probabilities: {domain_probs}")

    # 2. Select candidates from high-probability domains
    # This is the "Multi-Expert Synthesis" logic
    all_candidates = []
    for domain, prob in domain_probs.items():
        if prob >= inp.domain_probability_threshold:
            # For now, we search for all candidates and then sort.
            # A more advanced strategy could weight searches by probability.
            all_candidates.extend(index.search(query_vec, topk=inp.top_k_experts))

    # Sort all candidates by similarity and pick the best unique ones
    unique_candidates = {c['id']: c for c in all_candidates}
    sorted_candidates = sorted(unique_candidates.values(), key=lambda c: c['similarity'], reverse=True)
    final_candidates = sorted_candidates[:inp.top_k_experts]

    if not final_candidates:
        raise HTTPException(status_code=404, detail="No suitable expert adapters found.")

    print(f"Selected Candidates: {[c['id'] for c in final_candidates]}")

    # 3. Synthesize a new "Hybrid Expert"
    adapter_paths = []
    # This logic needs to be updated to use the manifest file from the Progenitor pillar
    # For now, we'll keep the convention-based path finding.
    for c in final_candidates:
        # manifest_path = f"adapters/{c['id']}/expert_manifest.json" -> Future state
        domain_folder = c['meta'].get('domain', 'general')
        path = f"adapters/expert_{domain_folder}/adapter.safetensors"
        if os.path.exists(path):
            adapter_paths.append(path)

    if not adapter_paths:
        raise HTTPException(status_code=500, detail="Could not find adapter files for selected candidates.")

    # Note: The V4 synthesizer expects paths to LoRA adapters, not full models
    synthesized_lora = synthesizer.synthesize(adapter_paths)

    if not synthesized_lora:
        raise HTTPException(status_code=500, detail="Synthesis of hybrid expert failed.")

    # 4. (Conceptual) Use Chimera Core for Inference
    # if chimera_core:
    #     # We would need to save the synthesized lora to a temp file
    #     temp_lora_path = "temp_synthesized_lora.safetensors"
    #     synthesizer.save_model(synthesized_lora, temp_lora_path)
    #
    #     # The Chimera Core performs hot-swap and generates the final response
    #     final_response = chimera_core.generate_response(inp.text, adapter_paths=[temp_lora_path])
    #     os.remove(temp_lora_path) # Clean up
    # else:
    #     final_response = "Inference core not available. Synthesis was successful."

    # For now, since we can't run real inference, we'll return the details of the process
    final_response = f"Successfully synthesized a hybrid expert from: {[c['id'] for c in final_candidates]}"


    return {
        "query": inp.text,
        "domain_probabilities": domain_probs,
        "selected_candidates": final_candidates,
        # "synthesized_response": final_response
    }
