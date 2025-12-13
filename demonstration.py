import asyncio
import numpy as np

from genesis_core.dht.network import KademliaNode
from genesis_core.dht.registry import NodeRegistry
from genesis_core.training.job_manager import JobPublisher, JobSubscriber, TrainingJob
from genesis_core.routing.router import PersonalizedRouter, Node as RouterNode, User

async def main():
    """
    A comprehensive end-to-end demonstration of the Genesis Core V9 architecture.
    """
    print("---  Genesis Core V9: End-to-End Demonstration ---")

    # 1. Initialize the Network
    print("\n[1] Initializing Kademlia network with 4 nodes...")
    nodes = [KademliaNode("127.0.0.1", 8500 + i) for i in range(4)]
    bootstrap_node_info = ("127.0.0.1", 8500)

    # Start bootstrap node first, then others connect to it
    await nodes[0].start()
    await asyncio.gather(*(node.start(bootstrap_nodes=[bootstrap_node_info]) for node in nodes[1:]))

    # 2. Register Expert Nodes
    print("\n[2] Two nodes are registering as experts on the DHT...")
    expert_registry = NodeRegistry(nodes[1]) # Node 1 will do the registration

    expert_node_1 = RouterNode(
        peer_id="expert_math_wizard",
        reputation=0.98,
        expertise=[0.9, 0.1, 0.1], # Strong in math
        latency=30.0
    )
    expert_node_2 = RouterNode(
        peer_id="expert_history_buff",
        reputation=0.95,
        expertise=[0.1, 0.9, 0.1], # Strong in history
        latency=50.0
    )

    await expert_registry.register_node(expert_node_1)
    await expert_registry.register_node(expert_node_2)

    # 3. A Super Node Publishes a Training Job
    print("\n[3] A 'Super Node' (Node 0) is publishing a new training job...")
    publisher = JobPublisher(nodes[0])
    new_job = TrainingJob(
        job_id="train_expert_history_v2",
        dataset_url="s3://genesis-data/history_qa_2025.csv",
        model_base="phi-3-mini",
        hyperparameters={"epochs": 5, "learning_rate": 1e-4}
    )
    await publisher.publish_job(new_job)

    # 4. A Worker Node Retrieves the Job
    print("\n[4] A 'Worker Node' (Node 2) is retrieving the training job...")
    subscriber = JobSubscriber(nodes[2])
    retrieved_job = await subscriber.get_job("train_expert_history_v2")

    if retrieved_job:
        print(f" -> Worker node successfully retrieved job: {retrieved_job.job_id}")
    else:
        print(" -> Worker node failed to retrieve the job.")

    # 5. A User Query is Routed by the Personalized Router
    print("\n[5] A 'Premium User' is making a query about history...")

    # The router can be on any node, let's use Node 3
    node_discoverer = NodeRegistry(nodes[3])
    live_nodes = await node_discoverer.get_all_nodes()

    if not live_nodes:
        print(" -> Router could not find any live expert nodes.")
        return

    print(f" -> Router has discovered {len(live_nodes)} expert nodes from the DHT.")

    router = PersonalizedRouter(live_nodes)
    user = User("premium_user_123", tier="premium")

    # Query embedding strong in 'history'
    query_embedding = np.array([0.2, 0.8, 0.1])

    best_node = router.route_query(user, query_embedding)

    print(f"\n -> Personalized Router selected: '{best_node.peer_id}'")
    print(f"    - Reputation: {best_node.reputation}")
    print(f"    - Latency: {best_node.latency}ms")
    print(f"    - Expertise Match: {np.dot(query_embedding, np.array(best_node.expertise))}")

    # 6. Cleanup
    print("\n[6] Shutting down all nodes...")
    for node in nodes:
        node.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDemonstration stopped by user.")
