import asyncio
from kademlia.network import Server

class KademliaNode:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = Server()

    async def start(self, bootstrap_nodes=None):
        """
        Starts the Kademlia node and bootstraps it to the network.
        """
        await self.server.listen(self.port)
        if bootstrap_nodes:
            await self.server.bootstrap(bootstrap_nodes)
        print(f"Kademlia node started on {self.host}:{self.port}")

    async def get(self, key):
        """
        Retrieves a value from the DHT.
        """
        return await self.server.get(key)

    async def set(self, key, value):
        """
        Sets a value in the DHT.
        """
        await self.server.set(key, value)

    def stop(self):
        """
        Stops the Kademlia node.
        """
        self.server.stop()
