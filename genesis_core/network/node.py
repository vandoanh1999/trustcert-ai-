import trio
from typing import Optional

from libp2p import new_host
from libp2p.crypto.secp256k1 import create_new_key_pair
from libp2p.security.noise.transport import (
    PROTOCOL_ID as NOISE_PROTOCOL_ID,
    Transport as NoiseTransport,
)
from libp2p.transport.tcp.tcp import TCP

from genesis_core.crypto.identity import NodeIdentity


async def create_p2p_node(identity: Optional[NodeIdentity] = None):
    """
    Creates and configures a new libp2p host using a persistent
    cryptographic identity.

    :param identity: A NodeIdentity object. If None, a default one will be created.
    """
    # Use our new persistent identity system
    if identity is None:
        identity = NodeIdentity()

    # Use the factory function to create the libp2p-compatible KeyPair
    # from our raw private key bytes.
    hex_key = identity.private_key.serialize()
    secret = bytes.fromhex(hex_key)
    key_pair = create_new_key_pair(secret)

    # Create a Noise security transport
    noise_transport = NoiseTransport(
        libp2p_keypair=key_pair,
        # Noise transport requires the raw secp256k1 private key
        noise_privkey=identity.private_key,
    )

    # Create a security options dictionary
    security_options = {NOISE_PROTOCOL_ID: noise_transport}

    # Create a host
    host = new_host(
        key_pair=key_pair,
        sec_opt=security_options,
        # Use a specific transport for clarity
        transport_opt={TCP: {}},
    )
    return host


async def main():
    """
    Main function to run the P2P node.
    """
    node = await create_p2p_node()
    async with node.run(listen_addrs=["/ip4/0.0.0.0/tcp/0"]):
        print("P2P Node has started.")
        print("Listening on:", node.get_addrs())
        # Keep the node running
        await trio.sleep_forever()


if __name__ == "__main__":
    try:
        trio.run(main)
    except KeyboardInterrupt:
        print("\nNode shutting down...")
