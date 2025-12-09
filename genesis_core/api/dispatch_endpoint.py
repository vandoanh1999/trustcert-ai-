"""
Genesis Core V7: The V7 Dispatch Endpoint

This is the primary functional endpoint for the Genesis ecosystem.
It receives a user query, simulates expert selection, and uses the
Chimera Core to generate a response.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Tuple

from inference.genesis_inference_core import ChimeraCore

router = APIRouter()

# --- I/O Models ---
class DispatchRequest(BaseModel):
    instruction: str = Field(..., description="The user's query or instruction.")
    # In a real system, the Oracle Brain would determine the experts.
    # For V7's API, we'll allow the user to specify them for now.
    expert_adapters: List[str] = Field(..., description="A list of expert adapter paths to consult.")

class DispatchResponse(BaseModel):
    dispatch_id: str = Field(..., description="The unique ID for this transaction, used for feedback.")
    response: str = Field(..., description="The generated response from the expert network.")

# --- Endpoint Logic ---

# Initialize the Chimera Core.
# In a real production app, this would be a singleton managed more carefully.
# For now, we point it to the dummy model created by setup.sh.
try:
    chimera_core = ChimeraCore(base_model_path="dummy_model.gguf", verbose=False)
except Exception as e:
    print(f"Warning: Could not initialize ChimeraCore. The API may not function. Error: {e}")
    chimera_core = None

@router.post("/", response_model=DispatchResponse)
async def dispatch_query(request: DispatchRequest):
    """
    Processes a user's instruction by dispatching it to the selected experts.
    """
    if not chimera_core:
        raise HTTPException(status_code=503, detail="Inference engine (ChimeraCore) is not available.")

    if not request.instruction or not request.expert_adapters:
        raise HTTPException(status_code=400, detail="Instruction and a list of expert_adapters are required.")

    try:
        # The generate_response method now returns a tuple: (dispatch_id, response_text)
        dispatch_id, response_text = chimera_core.generate_response(
            instruction=request.instruction,
            adapter_paths=request.expert_adapters
        )

        if "Error:" in response_text:
            raise HTTPException(status_code=500, detail=response_text)

        return DispatchResponse(dispatch_id=dispatch_id, response=response_text)

    except Exception as e:
        # This will catch errors during the inference process itself.
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during dispatch: {str(e)}")
