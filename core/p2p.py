"""
Genesis Core V8: Simulated P2P Gossip Network

This module simulates a basic P2P network where nodes can broadcast
and receive messages. It's the foundation for the decentralized logic.
"""
import asyncio
from typing import Dict, Any, List, Callable

class Node:
    """Represents a single node in the network."""
    def __init__(self, node_id: str, network: 'P2PNetwork'):
        self.node_id = node_id
        self.network = network
        self.message_handler: Callable = None

    async def send(self, target_node_id: str, message: Dict[str, Any]):
        """Sends a direct message to another node."""
        await self.network.direct_message(self.node_id, target_node_id, message)

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcasts a message to all other nodes in the network."""
        await self.network.gossip(self.node_id, message)

    def register_handler(self, handler: Callable):
        """Registers a callback function to handle incoming messages."""
        self.message_handler = handler

    async def receive_message(self, sender_id: str, message: Dict[str, Any]):
        """Called by the network to deliver a message to this node."""
        if self.message_handler:
            await self.message_handler(sender_id, message)

class P2PNetwork:
    """A simulation of the P2P network layer."""
    def __init__(self):
        self.nodes: Dict[str, Node] = {}

    def add_node(self) -> Node:
        """Adds a new node to the network and returns it."""
        node_id = f"node_{len(self.nodes) + 1}"
        node = Node(node_id, self)
        self.nodes[node_id] = node
        print(f"[P2P] Node {node_id} joined the network.")
        return node

    async def gossip(self, sender_id: str, message: Dict[str, Any]):
        """Simulates a gossip broadcast to all nodes except the sender."""
        # V8 Update: Access the type from the payload for logging
        message_type = message.get("payload", {}).get("type", "UNKNOWN")
        print(f"[P2P Gossip] {sender_id} broadcasting: {message_type}")
        for node_id, node in self.nodes.items():
            if node_id != sender_id:
                # In a real network, this would be a UDP broadcast or random peer selection
                await node.receive_message(sender_id, message)

    async def direct_message(self, sender_id: str, target_node_id: str, message: Dict[str, Any]):
        """Simulates a direct message to a specific node."""
        if target_node_id in self.nodes:
            await self.nodes[target_node_id].receive_message(sender_id, message)

# --- Example Usage & Self-Test ---
async def main():
    print("--- Running P2P Network Self-Test ---")

    # 1. Setup Network and Nodes
    network = P2PNetwork()
    node1 = network.add_node()
    node2 = network.add_node()
    node3 = network.add_node()

    # 2. Define message handlers
    received_messages = {node2.node_id: [], node3.node_id: []}

    async def handler_n2(sender_id, msg):
        print(f"  - {node2.node_id} received message from {sender_id}")
        received_messages[node2.node_id].append(msg)

    async def handler_n3(sender_id, msg):
        print(f"  - {node3.node_id} received message from {sender_id}")
        received_messages[node3.node_id].append(msg)

    node2.register_handler(handler_n2)
    node3.register_handler(handler_n3)

    # 3. Test Broadcast
    print("\n[1] Testing broadcast from node1...")
    await node1.broadcast({"type": "NEW_EXPERT_PROPOSAL", "expert_id": "expert_astro_v1"})

    # Allow for async operations to complete
    await asyncio.sleep(0.01)

    assert len(received_messages[node2.node_id]) == 1
    assert len(received_messages[node3.node_id]) == 1
    assert received_messages[node2.node_id][0]['type'] == "NEW_EXPERT_PROPOSAL"
    print("  - [PASS] Broadcast received by all other nodes.")

if __name__ == "__main__":
    asyncio.run(main())
