"""
Genesis Core V7: Dispatch Tracker

This module manages the state of dispatch events, breaking the circular
dependency between the API and Inference layers.
"""
import uuid
from typing import List, Dict

# This is the shared, in-memory database that tracks which experts
# were used for a given dispatch ID.
dispatch_history_db: Dict[str, List[str]] = {}

def record_dispatch_event(expert_ids: List[str]) -> str:
    """Creates a unique ID for a dispatch event and records the experts used."""
    dispatch_id = str(uuid.uuid4())
    dispatch_history_db[dispatch_id] = expert_ids
    return dispatch_id
