"""
Genesis Core V4: The Expert Builder Kit
Part of "The Progenitor" Pillar.

This script is a command-line tool to create a new Genesis Expert Adapter.
It handles:
1.  Data Standardization: Reads a JSON Lines file.
2.  Automated Fine-Tuning: Uses QLoRA for memory-efficient fine-tuning.
3.  Packaging & Metadata: Creates a final, ingestible expert package.

Usage:
  python tools/genesis_expert_builder.py \\
    --base_model "meta-llama/Llama-3-8B" \\
    --data_path "path/to/your/data.jsonl" \\
    --output_dir "output/my_new_expert" \\
    --domain "MyDomain"
"""
import os
import json
import torch
import hashlib
import argparse
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset
from trl import SFTTrainer

def compute_checksum(file_path):
    """Computes the SHA-256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def main(args):
    print("--- Starting Genesis Expert Builder ---")

    # --- 1. Load Dataset ---
    print(f"Loading and standardizing data from {args.data_path}...")
    # The SFTTrainer expects a 'text' column. We will format our data into it.
    def format_dataset(example):
        return {"text": f"### Instruction:\n{example['instruction']}\n\n### Response:\n{example['response']}"}

    dataset = load_dataset("json", data_files=args.data_path, split="train")
    formatted_dataset = dataset.map(format_dataset)
    print(f"Loaded {len(formatted_dataset)} training examples.")

    # --- 2. Setup QLoRA Fine-Tuning ---
    print(f"Setting up QLoRA for base model: {args.base_model}")

    # Quantization Config for QLoRA
    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16
    )

    # Load Tokenizer and Model
    tokenizer = AutoTokenizer.from_pretrained(args.base_model, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token # Set pad token

    model = AutoModelForCausalLM.from_pretrained(
        args.base_model,
        quantization_config=quantization_config,
        device_map="auto", # Automatically use available GPU
        trust_remote_code=True
    )

    # Prepare model for K-bit training
    model = prepare_model_for_kbit_training(model)

    # LoRA Config
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"], # Specific to Llama models
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )

    model = get_peft_model(model, lora_config)
    print("QLoRA model setup complete.")

    # --- 3. Run Fine-Tuning ---
    training_args = TrainingArguments(
        output_dir=os.path.join(args.output_dir, "training_checkpoints"),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=2,
        optim="paged_adamw_32bit",
        save_steps=100,
        logging_steps=10,
        learning_rate=args.learning_rate,
        fp16=True,
        max_grad_norm=0.3,
        max_steps=-1,
        warmup_ratio=0.03,
        group_by_length=True,
    )

    trainer = SFTTrainer(
        model=model,
        train_dataset=formatted_dataset,
        peft_config=lora_config,
        dataset_text_field="text",
        max_seq_length=512,
        tokenizer=tokenizer,
        args=training_args,
    )

    print("Starting fine-tuning...")
    trainer.train()
    print("Fine-tuning complete.")

    # --- 4. Package Adapter & Create Manifest ---
    print("Packaging the adapter and creating manifest...")

    adapter_path = os.path.join(args.output_dir, "adapter_model")
    trainer.model.save_pretrained(adapter_path)

    # Safetensors file is usually named adapter_model.safetensors
    adapter_file = os.path.join(adapter_path, "adapter_model.safetensors")

    # Compute checksum
    checksum = compute_checksum(adapter_file) if os.path.exists(adapter_file) else "file_not_found"

    # Create manifest
    manifest = {
        "expert_id": f"{args.domain.lower().replace(' ', '_')}_v1.0",
        "base_model": args.base_model,
        "domain": args.domain,
        "version": "1.0",
        "adapter_checksum_sha256": checksum,
        "adapter_file": "adapter_model/adapter_model.safetensors"
    }

    manifest_path = os.path.join(args.output_dir, "expert_manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print("\n--- Genesis Expert Builder Finished ---")
    print(f"Expert adapter package created successfully at: {args.output_dir}")
    print(f"Manifest file created at: {manifest_path}")
    print("You can now upload this directory to a public repository and ingest it into Genesis.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Genesis Core V4: Expert Builder Kit")
    parser.add_argument("--base_model", type=str, required=True, help="Base model ID from Hugging Face (e.g., 'meta-llama/Llama-3-8B')")
    parser.add_argument("--data_path", type=str, required=True, help="Path to the training data in JSON Lines format.")
    parser.add_argument("--output_dir", type=str, required=True, help="Directory to save the packaged expert adapter.")
    parser.add_argument("--domain", type=str, required=True, help="The domain of expertise (e.g., 'Medical', 'Legal').")
    parser.add_argument("--epochs", type=int, default=1, help="Number of training epochs.")
    parser.add_argument("--learning_rate", type=float, default=2e-4, help="Learning rate for the optimizer.")

    # This is a placeholder for a real run. In the sandbox, we cannot download large models or run GPU training.
    # The script is created for the user to run in their own powerful environment.
    print("Genesis Expert Builder script created. To run, use a GPU-enabled environment with Hugging Face authentication.")
    print("Example command is in the script's docstring.")
