"""
Genesis Core V8: Anti-Sybil Mechanism Self-Test (Rev 2)

This version uses a robust test harness to verify the Anti-Sybil mechanism.
"""
import asyncio
from unittest.mock import patch

from core.p2p import P2PNetwork
from core.node import DecentralizedNode

async def main():
    print("--- Running V8 Anti-Sybil Self-Test (Rev 2) ---")

    network = P2PNetwork()

    good_node = DecentralizedNode(network.add_node())
    sybil_fingerprint = "sybil_fingerprint_abc123"

    with patch('core.node.get_hardware_fingerprint', return_value=sybil_fingerprint):
        sybil_node_1 = DecentralizedNode(network.add_node())
        sybil_node_2 = DecentralizedNode(network.add_node())

    print(f"\n[1] Network Setup: ...") # Simplified logging

    print("\n[2] Nodes announcing themselves...")
    await good_node.join_network()
    await sybil_node_1.join_network()
    await sybil_node_2.join_network()

    await asyncio.sleep(0.01)

    print("\n[3] Verifying Sybil attack detection...")
    assert sybil_fingerprint in good_node.blacklist
    print(f"  - [PASS] Good node has blacklisted the Sybil fingerprint.")

    print("\n[4] Verifying that blacklisted nodes are ignored...")
    # Get the number of messages processed before the attack
    messages_before_spam = len(good_node._test_processed_messages)

    # The Sybil node broadcasts a malicious message
    await sybil_node_1.broadcast_message("MALICIOUS_SPAM", {})
    await asyncio.sleep(0.01)

    # Get the number of messages processed after the attack
    messages_after_spam = len(good_node._test_processed_messages)

    # The number of processed messages should not have changed
    assert messages_before_spam == messages_after_spam
    print("  - [PASS] Good node did not add the malicious message to its processed list.")

    print("\n--- V8 Anti-Sybil Self-Test Passed! ---")

if __name__ == "__main__":
    asyncio.run(main())
