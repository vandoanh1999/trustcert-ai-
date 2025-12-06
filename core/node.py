"""
Genesis Core V9: The Decentralized Node (Final Bugfix)

This version includes the final fix for the Anti-Sybil regression.
"""
import asyncio
import json
from enum import Enum
from typing import Dict, Any, List

from core.config import *
from core.p2p import Node as P2PNode
from core.security import get_hardware_fingerprint, generate_keys, sign_message, verify_signature
from core.architect import verify_architect_signature
from aurora_trust.reputation_vc import get_reputation
from Crypto.PublicKey import ECC
from core.training import simulate_lora_finetuning

class NodeTier(Enum):
    EPHEMERAL = 1; STABLE = 2; SUPER_NODE = 3

class DecentralizedNode:
    def __init__(self, p2p_node: P2PNode):
        # ... (init is the same)
        self.p2p = p2p_node; self.tier = NodeTier.EPHEMERAL
        self.fingerprint = get_hardware_fingerprint()
        self.private_key = generate_keys(self.fingerprint)
        self.public_key = self.private_key.public_key()
        self.node_id = self.p2p.node_id
        self.trust_score = get_reputation(self.fingerprint)
        self.contribution_score = 0.0
        self.known_peers: Dict[str, Dict[str, Any]] = {}
        self.pending_proposals: Dict[str, Dict[str, Any]] = {}
        self.awaiting_architect: Dict[str, Dict[str, Any]] = {}
        self.fingerprint_registry: Dict[str, str] = {self.node_id: self.fingerprint}
        self.blacklist: List[str] = []
        self.p2p.register_handler(self.handle_p2p_message)
        self._test_processed_messages: List[Dict[str, Any]] = []

    async def join_network(self): await self.broadcast_message("NODE_ANNOUNCE", {"fingerprint": self.fingerprint})
    def is_blacklisted(self, fp): return fp in self.blacklist
    def update_tier(self):
        # ... (same)
        ct = self.tier
        if self.trust_score >= NODE_SUPER_NODE_TRUST_THRESHOLD and self.tier==NodeTier.STABLE: self.tier=NodeTier.SUPER_NODE
        elif self.contribution_score >= NODE_STABLE_CONTRIBUTION_THRESHOLD and self.tier==NodeTier.EPHEMERAL: self.tier=NodeTier.STABLE
        if self.tier != ct: print(f"[{self.node_id}] Tier updated: {ct.name} -> {self.tier.name}")

    def sign_gossip_message(self, msg):
        # ... (same)
        mb = json.dumps(msg, sort_keys=True).encode('utf8')
        sig = sign_message(self.private_key, mb)
        return {"payload": msg, "signature": sig.hex(), "sender_id": self.node_id, "public_key_pem": self.public_key.export_key(format='PEM'), "fingerprint": self.fingerprint}

    async def broadcast_message(self, mt, d): await self.p2p.broadcast(self.sign_gossip_message({"type": mt, "data": d}))

    async def handle_p2p_message(self, sender_id: str, message: Dict[str, Any]):
        # --- FINAL FIX: Process NODE_ANNOUNCE before other checks ---
        payload = message.get('payload', {})
        message_type = payload.get('type')

        if message_type == "NODE_ANNOUNCE":
            new_fp = payload.get('data', {}).get('fingerprint')
            if not new_fp: return
            for node_id, fp in self.fingerprint_registry.items():
                if fp == new_fp and node_id != sender_id:
                    self.blacklist.append(fp)
                    return
            self.fingerprint_registry[sender_id] = new_fp

        # Now, perform blacklist and signature checks for all other messages
        sender_fingerprint = message.get("fingerprint")
        if not sender_fingerprint or self.is_blacklisted(sender_fingerprint):
            return

        try:
            public_key = ECC.import_key(message['public_key_pem'])
            payload_bytes = json.dumps(payload, sort_keys=True).encode('utf8')
            if not verify_signature(public_key, payload_bytes, bytes.fromhex(message['signature'])): return
        except: return

        self._test_processed_messages.append(payload)

        if message_type == "ARCHITECT_APPROVAL": self.process_architect_approval(payload['data'])
        elif message_type == "NEW_EXPERT_PROPOSAL":
            pid = payload['data']['proposal_id']
            if pid not in self.pending_proposals:
                self.pending_proposals[pid] = {"data": payload['data'], "votes": {}}
                if self.tier == NodeTier.SUPER_NODE: self.cast_vote(pid)
        elif message_type == "PROPOSAL_VOTE": self.process_proposal_vote(payload['data'])

    # ... (rest of the class is unchanged) ...
    def process_architect_approval(self, approval_data):
        pid = approval_data.get('proposal_id'); sig = approval_data.get('signature')
        if not pid or not sig: return
        if pid in self.awaiting_architect:
            pdata = self.awaiting_architect[pid]
            msg_to_verify = json.dumps(pdata, sort_keys=True).encode('utf8')
            if verify_architect_signature(msg_to_verify, bytes.fromhex(sig)):
                simulate_lora_finetuning(pdata['proposed_expert_id'], pdata['dataset_hash'], pdata['proof_of_source'])
                del self.awaiting_architect[pid]
    def tally_votes(self, proposal):
        pid = proposal['data']['proposal_id']
        total_power = sum(p['contribution'] for p in self.known_peers.values() if p.get('tier')==NodeTier.SUPER_NODE)
        if self.tier == NodeTier.SUPER_NODE: total_power += self.contribution_score
        if total_power == 0: return
        yes_power = sum(v['contribution'] for v in proposal['votes'].values() if v['approve'])
        if (yes_power / total_power) > NODE_SUPER_NODE_VOTE_THRESHOLD_PERCENT:
            if pid in self.pending_proposals:
                self.awaiting_architect[pid] = proposal['data']
                asyncio.create_task(self.broadcast_message("REQUEST_ARCHITECT_APPROVAL", {"proposal_id": pid}))
                del self.pending_proposals[pid]
    def cast_vote(self, p_id, approve=True):
        if p_id not in self.pending_proposals: return
        vote_data = {"approve": approve, "contribution": self.contribution_score, "node_id": self.node_id}
        prop = self.pending_proposals[p_id]
        prop['votes'][self.node_id] = vote_data
        asyncio.create_task(self.broadcast_message("PROPOSAL_VOTE", {"proposal_id": p_id, "vote": vote_data}))
        self.tally_votes(prop)
    def process_proposal_vote(self, vote_data):
        pid = vote_data['proposal_id']
        if pid in self.pending_proposals:
            self.pending_proposals[pid]['votes'][vote_data['vote']['node_id']] = vote_data['vote']
            self.tally_votes(self.pending_proposals[pid])
    def can_perform_mpc(self):
        count = sum(1 for p in self.known_peers.values() if p.get('tier') == NodeTier.SUPER_NODE)
        if self.tier == NodeTier.SUPER_NODE: count += 1
        return count >= NODE_MIN_SUPER_NODES_FOR_MPC
