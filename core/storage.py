"""
Genesis Core V9: Decentralized DHT Storage (Rev 2)

This version includes the fix for the bootstrap port mapping.
"""
import asyncio
import json

from kademlia.network import Server

class DHT:
    def __init__(self, port: int, bootstrap_node: tuple = None):
        self.server = Server()
        self.bootstrap_node = bootstrap_node
        self.port = port

    async def start(self):
        await self.server.listen(self.port)
        if self.bootstrap_node:
            await self.server.bootstrap([self.bootstrap_node])
        print(f"[DHT] Node listening on 0.0.0.0:{self.port}")

    async def stop(self):
        self.server.stop()

    async def set(self, key: str, value: dict):
        serialized_value = json.dumps(value)
        await self.server.set(key, serialized_value)
        print(f"[DHT] SET key='{key}'")

    async def get(self, key: str) -> dict:
        serialized_value = await self.server.get(key)
        if serialized_value:
            print(f"[DHT] GET key='{key}' -> FOUND")
            return json.loads(serialized_value)
        print(f"[DHT] GET key='{key}' -> NOT FOUND")
        return None

async def main():
    print("--- Running DHT Storage Self-Test ---")

    node1_addr = ("127.0.0.1", 8468)
    node2_addr = ("127.0.0.1", 8469)

    node1 = DHT(port=node1_addr[1])
    # Node 2 will bootstrap to Node 1's address
    node2 = DHT(port=node2_addr[1], bootstrap_node=node1_addr)

    await node1.start()
    await node2.start()

    key = "reputation:expert_geology_v2"
    value = {"score": 0.85, "votes": 120}
    print("\n[1] Storing data on Node 1...")
    await node1.set(key, value)

    await asyncio.sleep(1)

    print("\n[2] Retrieving data from Node 2...")
    retrieved_value = await node2.get(key)

    assert retrieved_value is not None
    assert retrieved_value["score"] == 0.85
    print("  - [PASS] Data stored on one node was successfully retrieved from another.")

    await node1.stop()
    await node2.stop()

    print("\n--- DHT Storage Self-Test Passed! ---")

if __name__ == "__main__":
    asyncio.run(main())
