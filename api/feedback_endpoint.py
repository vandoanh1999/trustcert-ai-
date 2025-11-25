"""
Genesis Core V7: The Judgement Pillar Feedback Endpoint

This endpoint allows users to provide feedback on a given dispatch response,
closing the learning loop for the Aurora Trust reputation system.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict
import uuid

# In a real application, this would be a persistent database (e.g., Redis, SQL)
# For this simulation, we'll use a simple in-memory dictionary.
dispatch_history_db: Dict[str, List[str]] = {}

from aurora_trust.reputation_vc import update_reputation_with_feedback

router = APIRouter()

class FeedbackInput(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0, description="The user's rating for the response, from 0.0 (terrible) to 1.0 (perfect).")
    ground_truth: str = Field(None, description="Optional: The correct or ideal response.")

@router.post("/{dispatch_id}")
def receive_feedback(dispatch_id: str, feedback: FeedbackInput):
    """
    Receives feedback for a specific dispatch event and updates the reputation
    of the experts who contributed to it.
    """
    print(f"--- Received Feedback for Dispatch ID: {dispatch_id} ---")

    # 1. Retrieve the expert IDs associated with this dispatch event.
    #    In a real system, this would be a lookup in a persistent database.
    if dispatch_id not in dispatch_history_db:
        raise HTTPException(status_code=404, detail="Dispatch ID not found. Cannot process feedback.")

    contributing_experts = dispatch_history_db[dispatch_id]
    print(f"Found contributing experts: {contributing_experts}")

    # 2. Apply the feedback to update the reputation of each expert.
    #    The `update_reputation_with_feedback` function handles the EMA calculation.
    if not contributing_experts:
        return {"status": "feedback_received_no_experts_to_update"}

    for expert_id in contributing_experts:
        update_reputation_with_feedback(expert_id, feedback.score)

    # 3. (Future) Log the ground_truth for future fine-tuning or analysis.
    if feedback.ground_truth:
        print(f"Ground truth received for future analysis: '{feedback.ground_truth[:100]}...'")

    return {
        "status": "feedback_processed_successfully",
        "dispatch_id": dispatch_id,
        "updated_experts": contributing_experts,
        "applied_score": feedback.score
    }

# This is a helper function to be used by the main dispatch endpoint
# to record which experts were used for a given request.
def record_dispatch_event(expert_ids: List[str]) -> str:
    """Creates a unique ID for a dispatch event and records the experts used."""
    dispatch_id = str(uuid.uuid4())
    dispatch_history_db[dispatch_id] = expert_ids
    return dispatch_id

# --- Frontend Simulation Helper Endpoint ---
class MockDispatchInput(BaseModel):
    dispatch_id: str
    experts: List[str]

@router.post("/register_mock_dispatch")
def register_mock_dispatch(data: MockDispatchInput):
    """
    Allows the frontend to register a simulated dispatch event.
    This is for demonstration purposes only.
    """
    dispatch_history_db[data.dispatch_id] = data.experts
    return {"status": "mock_dispatch_registered", "dispatch_id": data.dispatch_id}
