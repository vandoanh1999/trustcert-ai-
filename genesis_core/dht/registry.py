import json
from typing import List, Dict, Any

from genesis_core.dht.network import KademliaNode
from genesis_core.routing.router import Node as RouterNode

class NodeRegistry:
    """
    Manages the registration and discovery of expert nodes on the DHT.
    """
    REGISTRY_KEY = "expert_node_registry"

    def __init__(self, dht_node: KademliaNode):
        self.dht = dht_node

    async def _get_registry(self) -> List[Dict[str, Any]]:
        """Retrieves the raw registry list from the DHT."""
        raw_registry = await self.dht.get(self.REGISTRY_KEY)
        if raw_registry:
            return json.loads(raw_registry)
        return []

    async def register_node(self, node_info: RouterNode):
        """
        Registers a new expert node to the DHT.
        """
        registry = await self._get_registry()

        # Avoid duplicate registrations
        if any(n["peer_id"] == node_info.peer_id for n in registry):
            print(f"Node {node_info.peer_id} is already registered.")
            return

        registry.append(node_info.dict())
        await self.dht.set(self.REGISTRY_KEY, json.dumps(registry))
        print(f"Registered expert node: {node_info.peer_id}")

    async def get_all_nodes(self) -> List[RouterNode]:
        """
        Retrieves all registered expert nodes from the DHT.
        """
        registry = await self._get_registry()
        return [RouterNode(**node_data) for node_data in registry]

if __name__ == '__main__':
    import asyncio
    import numpy as np

    async def main():
        # --- Example Usage ---
        # Create a bootstrap node and a new node
        bootstrap_node = KademliaNode(host="127.0.0.1", port=8470)
        new_node = KademliaNode(host="127.0.0.1", port=8471)

        await bootstrap_node.start()
        await new_node.start(bootstrap_nodes=[("127.0.0.1", 8470)])

        # 1. Register a new expert node
        registry = NodeRegistry(new_node)
        expert_node_info = RouterNode(
            peer_id="expert_node_1",
            reputation=0.95,
            expertise=np.array([0.9, 0.1, 0.0]).tolist(), # Convert numpy array to list for JSON
            latency=50.0
        )
        await registry.register_node(expert_node_info)

        # 2. Discover all registered nodes from the bootstrap node
        discoverer_registry = NodeRegistry(bootstrap_node)
        all_nodes = await discoverer_registry.get_all_nodes()

        print("\n--- Discovered Nodes ---")
        for node in all_nodes:
            print(f"Peer ID: {node.peer_id}, Reputation: {node.reputation}")

        bootstrap_node.stop()
        new_node.stop()

    asyncio.run(main())
