# services/trainer/main.py
from fastapi import FastAPI
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import get_peft_model, LoraConfig
from qdrant_client import QdrantClient, models
import httpx
import uuid

app = FastAPI(title="Trainer Service (Registry-Aware)")

# Load model 1 lần
model_name = "meta-llama/Meta-Llama-3-8B-Instruct"
model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto", torch_dtype=torch.float16)
tokenizer = AutoTokenizer.from_pretrained(model_name)
qdrant = QdrantClient("http://qdrant:6333")
client = httpx.Client()

# Tạo collection cho LoRA Registry
try:
    qdrant.get_collection(collection_name="lora_registry")
except Exception:
    qdrant.recreate_collection(
        collection_name="lora_registry",
        vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE) # Giả sử BAAI/bge-small
    )

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

    lora_path = f"/app/lora_storage/lora_{user_id}_{source_id}.safetensors"
    lora_model.save_pretrained(lora_path)

    # 1. TẠO EMBEDDING ĐẠI DIỆN CHO LORA NÀY
    # Dùng chính content để làm vector đại diện
    content_vector_resp = client.post("http://embedder:8002/embed", json={"texts": [content]})
    content_vector = content_vector_resp.json()[0]

    # 2. ĐĂNG KÝ LORA VÀO QDRANT
    qdrant.upsert(
        collection_name="lora_registry",
        points=[
            models.PointStruct(
                id=str(uuid.uuid4()), # ID duy nhất
                vector=content_vector,
                payload={
                    "path": lora_path,
                    "user_id": user_id,
                    "source_id": source_id
                }
            )
        ]
    )

    # Free memory
    del lora_model
    torch.cuda.empty_cache()

    return {"lora_path": lora_path}
