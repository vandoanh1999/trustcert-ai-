import pytest
import numpy as np
import os

from genesis_core.crypto.identity import NodeIdentity
from genesis_core.training.job_manager import TrainingJob, JobPublisher, JobSubscriber, MockDHTClient
from genesis_core.routing.router import PersonalizedRouter, Node as RouterNode, User

@pytest.mark.asyncio
async def test_e2e_core_logic():
    # 1. Test Identity Persistence
    identity1 = NodeIdentity(private_key_path="node_private_key.pem")
    peer_id1 = identity1.peer_id

    # Create a new identity object from the same file
    identity2 = NodeIdentity(private_key_path="node_private_key.pem")
    peer_id2 = identity2.peer_id

    assert peer_id1 == peer_id2, "Failed to load persistent identity"

    # 2. Test DHT Job Publishing and Retrieval
    dht_client = MockDHTClient()
    publisher = JobPublisher(dht_client)
    subscriber = JobSubscriber(dht_client)

    job = TrainingJob(
        job_id="test_job_1",
        dataset_url="test_dataset",
        model_base="test_model",
        hyperparameters={"lr": 0.01}
    )
    await publisher.publish_job(job)
    retrieved_job = await subscriber.get_job("test_job_1")

    assert retrieved_job is not None
    assert retrieved_job.job_id == "test_job_1"
    assert retrieved_job.dataset_url == "test_dataset"

    # 3. Test Personalized Router
    router_nodes = [
        RouterNode("node1_peer_id", 0.9, np.array([0.9, 0.1]), 50),
        RouterNode("node2_peer_id", 0.8, np.array([0.1, 0.9]), 30),
    ]
    router = PersonalizedRouter(router_nodes)
    user = User("test_user", "premium")
    query_embedding = np.array([0.8, 0.2]) # Matches node 1

    best_node = router.route_query(user, query_embedding)
    assert best_node.peer_id == "node1_peer_id"

    # Cleanup the generated key file
    os.remove("node_private_key.pem")
