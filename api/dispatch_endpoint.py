"""
V3 Dispatch Endpoint
- Uses the real SemanticRouter.
- Uses the new, powerful Synthesizer.
- Simulates retrieving adapter file paths from metadata.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from router.router import SemanticRouter
from weightindex.indexer import PersistentIndex
from synthesizer.main import Synthesizer
import os

router = APIRouter()

# Initialize V3 components
router_inst = SemanticRouter()
index = PersistentIndex()
synthesizer = Synthesizer()

class DispatchInput(BaseModel):
    text: str
    topk: int = 3

@router.post("/")
def dispatch(inp: DispatchInput):
    print(f"Received dispatch request for text: '{inp.text}'")

    # 1. Use the new "Brain" to get a high-quality semantic vector
    domain, query_vec = router_inst.route(inp.text)
    print(f"Routed to domain: {domain}")

    # 2. Query the production-ready WeightIndex
    candidates = index.search(query_vec, topk=inp.topk)
    print(f"Found {len(candidates)} candidates.")

    if not candidates:
        return {"domain": domain, "message": "No suitable adapters found."}

    # 3. Prepare for the new "Heart"
    # In a real system, the metadata would contain the path to the .safetensors file.
    # We will simulate this by constructing the path based on the adapter ID.
    adapter_paths = []
    for c in candidates:
        # Example: id 'expert_math_v1' -> path 'adapters/expert_math/adapter.safetensors'
        # This is a convention-based approach.
        domain_folder = c['meta'].get('domain', 'general')
        expert_folder_name = f"expert_{domain_folder}" # Convention
        # NOTE: This assumes a simplified file naming. A real system would store the
        # exact filename in the metadata.
        path = os.path.join("adapters", expert_folder_name, "adapter.safetensors")
        if os.path.exists(path):
            adapter_paths.append(path)
        else:
             print(f"Warning: Could not find adapter file at constructed path: {path}")

    if not adapter_paths:
        return {"domain": domain, "candidates": candidates, "message": "Candidates found, but could not locate adapter files."}

    # 4. Use the new Synthesizer to perform an advanced merge
    synthesized_model = synthesizer.synthesize(adapter_paths)

    if synthesized_model is None:
        return {"domain": domain, "candidates": candidates, "message": "Synthesis failed."}

    # For the response, let's show a preview of the first synthesized layer
    first_layer_key = next(iter(synthesized_model))
    first_layer_preview = synthesized_model[first_layer_key].flatten()[:10].tolist()

    return {
        "domain": domain,
        "candidates": [c['id'] for c in candidates],
        "synthesized_model_layers": list(synthesized_model.keys()),
        "synthesized_model_preview": {
            "first_layer_key": first_layer_key,
            "first_layer_shape": synthesized_model[first_layer_key].shape,
            "first_layer_preview": first_layer_preview
        }
    }
