"""
Genesis Core V8: The Self-Growing Ecosystem Rover (Upgraded)

This agent is responsible for proactively discovering new, valuable
datasets, generating secure proposals, and broadcasting them to the network.
"""
import os
import json
import time
import hashlib
from typing import List, Dict, Any

from core.node import DecentralizedNode # V8 Upgrade

# --- Configuration ---
SIMULATED_DATA_SOURCES = {
    "https://example.com/new_medical_research_2025.json": '[{"study": "Effect of Compound X", "result": "positive"}]',
    "https://example.com/quantum_computing_breakthroughs.txt": "A new qubit stabilization technique was discovered.",
    "https://example.com/ancient_history_scrolls_deciphered.csv": "emperor,reign_start,reign_end\nAugustus,27 BC,14 AD",
}

class EcosystemRover:
    def __init__(self, node: DecentralizedNode):
        self.node = node
        print(f"🌌 Ecosystem Rover initialized on {self.node.node_id}.")

    def scan_for_new_knowledge(self) -> Dict[str, str]:
        """
        Scans simulated data sources. In a real system, this would crawl the web.
        Returns a dictionary of {source_url: content}.
        """
        print(f"\n[{self.node.node_id}] Rover starting scan for new knowledge sources...")
        # This is a simulation of discovering new data
        return SIMULATED_DATA_SOURCES

    def generate_proposal(self, source_url: str, content: str) -> Dict[str, Any]:
        """
        Analyzes a dataset and generates a formal, secure proposal.
        """
        # Item 16: Include hash of dataset and proof-of-source
        dataset_hash = hashlib.sha256(content.encode('utf8')).hexdigest()
        topic = source_url.split('/')[-1].split('.')[0].replace('_', ' ')

        proposal = {
            "proposal_id": f"prop_{topic.split(' ')[0]}_{int(time.time())}",
            "timestamp": int(time.time()),
            "proof_of_source": {
                "url": source_url,
                "retrieval_timestamp": int(time.time())
            },
            "dataset_hash": dataset_hash,
            "proposed_expert_id": f"expert_{topic.replace(' ', '_')}_v1",
            "justification": f"Discovered novel information on '{topic}' from a trusted source."
        }
        return proposal

    async def run_mission(self):
        """Runs a full discovery-to-proposal mission."""
        new_sources = self.scan_for_new_knowledge()
        if not new_sources:
            print(f"[{self.node.node_id}] Mission complete. No new knowledge found.")
            return

        print(f"[{self.node.node_id}] Generating and broadcasting proposals...")
        for url, content in new_sources.items():
            proposal = self.generate_proposal(url, content)
            print(f"  - Broadcasting proposal: {proposal['proposal_id']}")
            # Use the node's broadcast capability to send a signed message
            await self.node.broadcast_message("NEW_EXPERT_PROPOSAL", proposal)

# --- Self-Test ---
async def main():
    from core.p2p import P2PNetwork
    print("--- Running Upgraded Ecosystem Rover Self-Test ---")

    network = P2PNetwork()
    # The Rover will run on a standard Ephemeral node
    rover_node = DecentralizedNode(network.add_node())
    rover = EcosystemRover(rover_node)

    # Create a listener node to verify the broadcast
    listener_node = DecentralizedNode(network.add_node())
    received_proposals = []
    async def handle_msg(sender, msg):
        if msg['payload']['type'] == "NEW_EXPERT_PROPOSAL":
            received_proposals.append(msg['payload']['data'])
    listener_node.p2p.register_handler(handle_msg)

    await rover.run_mission()
    await asyncio.sleep(0.01) # Allow gossip to propagate

    assert len(received_proposals) == len(SIMULATED_DATA_SOURCES)
    first_proposal = received_proposals[0]
    assert 'dataset_hash' in first_proposal
    assert 'proof_of_source' in first_proposal
    assert 'url' in first_proposal['proof_of_source']

    print("\n[PASS] Rover mission completed and broadcasted secure proposals successfully.")
    print(f"  - Example proposal received by listener: {json.dumps(first_proposal, indent=2)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
