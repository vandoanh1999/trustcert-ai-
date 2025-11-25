"""
Genesis Core V7: The Self-Knowledge Pillar (Ecosystem Rover)

This agent is responsible for proactively discovering new, valuable
datasets and proposing the creation of new experts to enrich the
Genesis ecosystem.
"""
import os
import json
import time
from typing import List, Dict, Any

# --- Configuration ---
PROPOSAL_DIR = "expert_proposals"
SIMULATED_DATA_SOURCES = [
    "./simulated_data/new_medical_research_2025.json",
    "./simulated_data/quantum_computing_breakthroughs.txt",
    "./simulated_data/ancient_history_scrolls_deciphered.csv",
    "./simulated_data/existing_dataset_finance.csv" # A source that might already be covered
]

# --- Helper Functions ---
def setup_simulation():
    """Creates dummy data sources for the rover to discover."""
    os.makedirs("simulated_data", exist_ok=True)
    with open(SIMULATED_DATA_SOURCES[0], "w") as f:
        json.dump([{"study": "Effect of Compound X", "result": "positive"}], f)
    with open(SIMULATED_DATA_SOURCES[1], "w") as f:
        f.write("A new qubit stabilization technique was discovered.")
    with open(SIMULATED_DATA_SOURCES[2], "w") as f:
        f.write("emperor,reign_start,reign_end\nAugustus,27 BC,14 AD")
    with open(SIMULATED_DATA_SOURCES[3], "w") as f:
        f.write("ticker,price\nGEN,100")

def is_topic_already_covered(topic: str, existing_experts: List[str]) -> bool:
    """
    A simple simulation to check if a new topic is already covered by
    existing experts. In a real system, this would involve semantic search.
    """
    for expert in existing_experts:
        if topic in expert:
            return True
    return False

# --- Rover Core Logic ---
class EcosystemRover:
    def __init__(self, existing_experts: List[str]):
        self.existing_experts = existing_experts
        os.makedirs(PROPOSAL_DIR, exist_ok=True)
        print("🌌 Ecosystem Rover initialized.")

    def scan_for_new_knowledge(self) -> List[str]:
        """
        Scans simulated data sources for new information.
        Returns a list of paths to newly discovered, valuable datasets.
        """
        print("\n--- Rover starting scan for new knowledge sources... ---")
        potential_sources = []
        for source_path in SIMULATED_DATA_SOURCES:
            if os.path.exists(source_path):
                # Simple check: does the topic seem new?
                topic = os.path.basename(source_path).split('.')[0].split('_')[0]
                if not is_topic_already_covered(topic, self.existing_experts):
                    print(f"  - Found promising new source: {source_path} (Topic: {topic})")
                    potential_sources.append(source_path)
                else:
                    print(f"  - Skipping source (topic '{topic}' likely covered): {source_path}")
        return potential_sources

    def generate_proposal(self, dataset_path: str) -> Dict[str, Any]:
        """
        Analyzes a dataset and generates a formal proposal for creating
        a new expert.
        """
        topic = os.path.basename(dataset_path).split('.')[0]
        proposal = {
            "proposal_id": f"prop_{topic}_{int(time.time())}",
            "timestamp": int(time.time()),
            "source_dataset": dataset_path,
            "proposed_expert_id": f"expert_{topic}_v1",
            "justification": f"Dataset at {dataset_path} contains novel information on the topic of '{topic.replace('_', ' ')}'. A specialized expert would improve system performance in this domain.",
            "status": "pending_review"
        }
        return proposal

    def save_proposal(self, proposal: Dict[str, Any]):
        """Saves a proposal to a file for human review."""
        filename = os.path.join(PROPOSAL_DIR, f"{proposal['proposal_id']}.json")
        with open(filename, "w") as f:
            json.dump(proposal, f, indent=2)
        print(f"  - Saved new expert proposal to: {filename}")

    def run_mission(self):
        """Runs a full discovery-to-proposal mission."""
        new_sources = self.scan_for_new_knowledge()
        if not new_sources:
            print("--- Mission complete. No new valuable knowledge found this cycle. ---")
            return

        print("\n--- Generating proposals for new experts... ---")
        for source in new_sources:
            proposal = self.generate_proposal(source)
            self.save_proposal(proposal)

        print("--- Mission complete. New expert proposals are ready for review. ---")

# --- Example Execution ---
if __name__ == "__main__":
    print("--- Running a manual Ecosystem Rover mission ---")
    setup_simulation()

    # Simulate the current state of the network
    current_experts = [
        "expert_finance_v2",
        "expert_legal_v1"
    ]

    rover = EcosystemRover(existing_experts=current_experts)
    rover.run_mission()
