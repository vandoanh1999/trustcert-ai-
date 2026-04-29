"""
Genesis Core V9: Architect Governance Layer Self-Test

This script verifies the end-to-end governance workflow, from Super Node
approval to the final Architect signature verification.
"""
import asyncio
import json

from core.p2p import P2PNetwork
from core.node import DecentralizedNode
from core.architect import ARCHITECT_PUBLIC_KEY
from core.security import sign_message
from Crypto.PublicKey import ECC

# --- Architect's Private Key (for test simulation ONLY) ---
# This is the private key corresponding to the public key in core/architect.py
ARCHITECT_PRIVATE_KEY_PEM = """-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgCgwHXoz2GAkUQ9g8
rpr+kFXli4gZRBdOpjLRtEWQdrShRANCAAQgjIhEJMvBHWgOXVoXDI59Jy0XWW9U
mq1bZ9eg9QJe92sfF79+KgZ7uThRM6cthxTf5Cxaz76QWlEpVPt/Cml6
-----END PRIVATE KEY-----"""
ARCHITECT_PRIVATE_KEY = ECC.import_key(ARCHITECT_PRIVATE_KEY_PEM)


async def main():
    print("--- Running V9 Governance Layer Self-Test ---")

    network = P2PNetwork()
    # A single, powerful Super Node is enough to test the logic
    super_node = DecentralizedNode(network.add_node())
    super_node.trust_score = 0.9; super_node.contribution_score = 100
    super_node.update_tier(); super_node.update_tier()

    # 1. A proposal is received and approved by the Super Node
    proposal_data = {
        "proposal_id": "prop_final_test_v1",
        "proposed_expert_id": "expert_final_v1",
        "dataset_hash": "final_hash",
        "proof_of_source": {"url": "https://example.com/final_test_data"} # Add missing field
    }
    proposal_id = proposal_data['proposal_id']

    print("\n[1] Super Node approves proposal, awaiting Architect...")
    # Manually trigger the approval process
    super_node.pending_proposals[proposal_id] = {"data": proposal_data, "votes": {}}
    super_node.cast_vote(proposal_id, approve=True)

    await asyncio.sleep(0.01)

    # Verify the node is now awaiting the Architect
    assert proposal_id in super_node.awaiting_architect
    assert proposal_id not in super_node.pending_proposals
    print("  - [PASS] Node has correctly moved proposal to 'awaiting_architect' state.")

    # 2. The Architect signs the proposal data and broadcasts the approval
    print("\n[2] Architect broadcasts signature...")
    message_to_sign = json.dumps(proposal_data, sort_keys=True).encode('utf8')
    architect_signature = sign_message(ARCHITECT_PRIVATE_KEY, message_to_sign)

    approval_payload = {
        "type": "ARCHITECT_APPROVAL",
        "data": {
            "proposal_id": proposal_id,
            "signature": architect_signature.hex()
        }
    }

    # IMPORTANT: The message must be signed by some node (even if the Architect signs the data inside)
    # The node's handle_p2p_message expects the outer wrapper with sender_id, public_key_pem, etc.
    signed_message = super_node.sign_gossip_message(approval_payload)

    # Simulate an external broadcast to the node
    await super_node.handle_p2p_message("ARCHITECT_BROADCASTER", signed_message)

    # 3. Verify the final outcome
    print("\n[3] Verifying final execution...")
    # If the signature was valid, the proposal should be removed from the awaiting state
    if proposal_id not in super_node.awaiting_architect:
        print("  - [PASS] Proposal was executed and removed from 'awaiting_architect' state.")
    else:
        print("  - [FAIL] Proposal still in awaiting_architect state.")
        exit(1)

    print("\n--- V9 Governance Layer Self-Test Passed! ---")

if __name__ == "__main__":
    asyncio.run(main())
