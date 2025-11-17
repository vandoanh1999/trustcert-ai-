from fastapi import FastAPI
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import get_peft_model, LoraConfig
from qdrant_client import QdrantClient, models
import httpx
import uuid
import boto3
import os
from pathlib import Path
from ..common import config

app = FastAPI(title="Trainer Service (Registry-Aware)")

# --- Khởi tạo Clients ---
model = AutoModelForCausalLM.from_pretrained(config.BASE_MODEL_NAME, device_map="auto", torch_dtype=torch.float16)
tokenizer = AutoTokenizer.from_pretrained(config.BASE_MODEL_NAME)
qdrant = QdrantClient(host=config.QDRANT_HOST, port=config.QDRANT_PORT)
client = httpx.Client()
s3_client = boto3.client(
    's3',
    endpoint_url=config.S3_ENDPOINT_URL,
    aws_access_key_id=config.S3_ACCESS_KEY_ID,
    aws_secret_access_key=config.S3_SECRET_ACCESS_KEY
)

# --- Logic khởi động ---
@app.on_event("startup")
def startup_event():
    # ... (logic tạo Qdrant collection và S3 bucket) ...

@app.post("/train_lora")
def train_lora(content: str, user_id: str, source_id: str):
    lora_config = LoraConfig(
        r=2,
        lora_alpha=4,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    lora_model = get_peft_model(model, lora_config)
    lora_model.train()

    inputs = tokenizer(content, return_tensors="pt", truncation=True, max_length=512).to(model.device)
    optimizer = torch.optim.AdamW(lora_model.parameters(), lr=1e-5)

    for epoch in range(3):
        outputs = lora_model(**inputs, labels=inputs["input_ids"])
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

    temp_lora_dir = f"/tmp/lora_{user_id}_{source_id}"
    lora_model.save_pretrained(temp_lora_dir)

    s3_lora_path = f"loras/{user_id}/{source_id}"
    for root, dirs, files in os.walk(temp_lora_dir):
        for file in files:
            local_path = os.path.join(root, file)
            s3_key = f"{s3_lora_path}/{file}"
            s3_client.upload_file(local_path, config.S3_BUCKET_NAME, s3_key)

    content_vector_resp = client.post(f"{config.EMBEDDER_URL}/embed", json={"texts": [content]})
    content_vector = content_vector_resp.json()[0]

    qdrant.upsert(
        collection_name="lora_registry",
        points=[
            models.PointStruct(
                id=str(uuid.uuid4()),
                vector=content_vector,
                payload={
                    "path": s3_lora_path,
                    "user_id": user_id,
                    "source_id": source_id
                }
            )
        ]
    )

    del lora_model
    torch.cuda.empty_cache()

    return {"lora_path": s3_lora_path}
