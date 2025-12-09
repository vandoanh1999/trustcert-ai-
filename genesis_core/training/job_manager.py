import json
from pydantic import BaseModel
from typing import Dict, Any

# Placeholder for a real DHT client
class MockDHTClient:
    def __init__(self):
        self.store = {}

    async def set(self, key: str, value: str):
        print(f"[DHT] Setting key '{key}'")
        self.store[key] = value

    async def get(self, key: str):
        print(f"[DHT] Getting key '{key}'")
        return self.store.get(key)

class TrainingJob(BaseModel):
    """
    Data structure for a LoRA training job.
    """
    job_id: str
    dataset_url: str
    model_base: str
    hyperparameters: Dict[str, Any]

class JobPublisher:
    """
    Publishes new training jobs to the DHT.
    """
    def __init__(self, dht_client: MockDHTClient):
        self.dht = dht_client

    async def publish_job(self, job: TrainingJob):
        """
        Serializes and publishes a training job to the DHT.
        """
        job_key = f"training_job::{job.job_id}"
        job_json = job.model_dump_json()
        await self.dht.set(job_key, job_json)
        print(f"Published training job '{job.job_id}' to the DHT.")

class JobSubscriber:
    """
    Subscribes to and processes new training jobs from the DHT.
    """
    def __init__(self, dht_client: MockDHTClient):
        self.dht = dht_client

    async def get_job(self, job_id: str) -> TrainingJob:
        """
        Retrieves and deserializes a training job from the DHT.
        """
        job_key = f"training_job::{job_id}"
        job_json = await self.dht.get(job_key)
        if job_json:
            job_data = json.loads(job_json)
            return TrainingJob(**job_data)
        return None

if __name__ == '__main__':
    import asyncio

    async def main():
        # --- Example Usage ---
        dht_client = MockDHTClient()

        # 1. A Super Node publishes a new job
        publisher = JobPublisher(dht_client)
        new_job = TrainingJob(
            job_id="lora_expert_crypto_v1",
            dataset_url="s3://genesis-datasets/crypto_news_2024.csv",
            model_base="phi-3-mini",
            hyperparameters={"learning_rate": 0.0001, "epochs": 3}
        )
        await publisher.publish_job(new_job)

        # 2. A Training Node subscribes to the job
        subscriber = JobSubscriber(dht_client)
        retrieved_job = await subscriber.get_job("lora_expert_crypto_v1")

        if retrieved_job:
            print("\n--- Training Node ---")
            print(f"Retrieved job: {retrieved_job.job_id}")
            print(f"Dataset: {retrieved_job.dataset_url}")
            print(f"Model Base: {retrieved_job.model_base}")
            print(f"Hyperparameters: {retrieved_job.hyperparameters}")
            # Here, the training node would kick off the actual training process
        else:
            print("Job not found.")

    asyncio.run(main())
