"""
Genesis Core V8: The Decentralized Node (Final Polish - Rev 4)

This version includes the final, correct signature verification logic.
"""
import asyncio
import json
from enum import Enum
from typing import Dict, Any, List

from core.config import *
from core.p2p import Node as P2PNode
from core.security import get_hardware_fingerprint, generate_keys, sign_message, verify_signature
from aurora_trust.reputation_vc import get_reputation
from Crypto.PublicKey import ECC
from core.training import simulate_lora_finetuning

class NodeTier(Enum):
    EPHEMERAL = 1; STABLE = 2; SUPER_NODE = 3

class DecentralizedNode:
    def __init__(self, p2p_node: P2PNode):
        self.p2p = p2p_node; self.tier = NodeTier.EPHEMERAL
        self.fingerprint = get_hardware_fingerprint()
        self.private_key = generate_keys(self.fingerprint)
        self.public_key = self.private_key.public_key()
        self.node_id = self.p2p.node_id
        self.trust_score = get_reputation(self.fingerprint)
        self.contribution_score = 0.0
        self.known_peers: Dict[str, Dict[str, Any]] = {}
        self.pending_proposals: Dict[str, Dict[str, Any]] = {}
        self.fingerprint_registry: Dict[str, str] = {self.node_id: self.fingerprint}
        self.blacklist: List[str] = []
        self.p2p.register_handler(self.handle_p2p_message)
        self._test_processed_messages: List[Dict[str, Any]] = []

    async def join_network(self):
        await self.broadcast_message("NODE_ANNOUNCE", {"fingerprint": self.fingerprint})

    def is_blacklisted(self, fingerprint: str) -> bool:
        return fingerprint in self.blacklist

    def update_tier(self):
        current_tier = self.tier
        if self.trust_score >= NODE_SUPER_NODE_TRUST_THRESHOLD and self.tier == NodeTier.STABLE: self.tier = NodeTier.SUPER_NODE
        elif self.contribution_score >= NODE_STABLE_CONTRIBUTION_THRESHOLD and self.tier == NodeTier.EPHEMERAL: self.tier = NodeTier.STABLE
        if self.tier != current_tier: print(f"[{self.node_id}] Tier updated: {current_tier.name} -> {self.tier.name}")

    def sign_gossip_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        message_bytes = json.dumps(message, sort_keys=True).encode('utf8')
        signature = sign_message(self.private_key, message_bytes)
        return {"payload": message, "signature": signature.hex(), "sender_id": self.node_id, "public_key_pem": self.public_key.export_key(format='PEM'), "fingerprint": self.fingerprint}

    async def broadcast_message(self, message_type: str, data: Dict[str, Any]):
        payload = {"type": message_type, "data": data}
        await self.p2p.broadcast(self.sign_gossip_message(payload))

    async def handle_p2p_message(self, sender_id: str, message: Dict[str, Any]):
        sender_fingerprint = message.get("fingerprint")
        if not sender_fingerprint or self.is_blacklisted(sender_fingerprint):
            return

        try:
            public_key = ECC.import_key(message['public_key_pem'])
            payload_bytes = json.dumps(message['payload'], sort_keys=True).encode('utf8')
            signature = bytes.fromhex(message['signature'])
            if not verify_signature(public_key, payload_bytes, signature):
                return
        except (ValueError, KeyError, TypeError):
            return

        payload = message['payload']
        self._test_processed_messages.append(payload)

        message_type = payload.get('type')
        if message_type == "NODE_ANNOUNCE":
            new_fp = payload['data']['fingerprint']
            for node_id, fp in self.fingerprint_registry.items():
                if fp == new_fp and node_id != sender_id: self.blacklist.append(fp); return
            self.fingerprint_registry[sender_id] = new_fp
        elif message_type == "NEW_EXPERT_PROPOSAL":
            proposal_id = payload['data']['proposal_id']
            if proposal_id not in self.pending_proposals:
                self.pending_proposals[proposal_id] = {"data": payload['data'], "votes": {}}
                if self.tier == NodeTier.SUPER_NODE: self.cast_vote(proposal_id)
        elif message_type == "PROPOSAL_VOTE":
            self.process_proposal_vote(payload['data'])

    def cast_vote(self, proposal_id: str, approve: bool = True):
        if proposal_id not in self.pending_proposals: return
        vote_data = {"approve": approve, "contribution": self.contribution_score, "node_id": self.node_id}
        proposal = self.pending_proposals[proposal_id]
        proposal['votes'][self.node_id] = vote_data
        asyncio.create_task(self.broadcast_message("PROPOSAL_VOTE", {"proposal_id": proposal_id, "vote": vote_data}))
        self.tally_votes(proposal)

    def process_proposal_vote(self, vote_data: Dict[str, Any]):
        proposal_id = vote_data['proposal_id']
        if proposal_id in self.pending_proposals:
            voter_id = vote_data['vote']['node_id']
            self.pending_proposals[proposal_id]['votes'][voter_id] = vote_data['vote']
            self.tally_votes(self.pending_proposals[proposal_id])

    def tally_votes(self, proposal: Dict[str, Any]):
        if not proposal: return
        proposal_id = proposal['data']['proposal_id']

        total_super_node_power = sum(p['contribution'] for p in self.known_peers.values() if p.get('tier') == NodeTier.SUPER_NODE)
        if self.tier == NodeTier.SUPER_NODE: total_super_node_power += self.contribution_score
        if total_super_node_power == 0: return

        total_yes_power = sum(v['contribution'] for v in proposal['votes'].values() if v['approve'])

        if (total_yes_power / total_super_node_power) > NODE_SUPER_NODE_VOTE_THRESHOLD_PERCENT:
            if proposal_id in self.pending_proposals:
                print(f"[{self.node_id}] Proposal {proposal_id} APPROVED!")
                # TODO: Fix race condition before re-enabling autonomous training.
                # For now, we just log the approval and delete the proposal.
                # p_data = proposal['data']
                # simulate_lora_finetuning(p_data['proposed_expert_id'], p_data['dataset_hash'], p_data['proof_of_source'])
                del self.pending_proposals[proposal_id]

    def can_perform_mpc(self) -> bool:
        count = sum(1 for p in self.known_peers.values() if p.get('tier') == NodeTier.SUPER_NODE)
        if self.tier == NodeTier.SUPER_NODE: count += 1
        return count >= NODE_MIN_SUPER_NODES_FOR_MPC
