"""
Genesis Core V4: L2 Router Training Script
Part of "The Oracle Brain" Pillar.

This script fine-tunes a small transformer model for text classification.
The goal is to create a fast, accurate L2 Router that can determine the
domain of a user's query based on its semantic meaning, not just keywords.

Usage:
  python l2_router_training/train_l2_router.py \\
    --data_path "l2_router_training/data/dataset.jsonl" \\
    --output_dir "l2_router_model" \\
    --model_name "distilbert-base-uncased"
"""
import os
import json
import torch
import argparse
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import load_dataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

def main(args):
    print("--- Starting L2 Router Training ---")

    # --- 1. Load and Prepare Dataset ---
    print(f"Loading dataset from {args.data_path}...")
    dataset = load_dataset("json", data_files=args.data_path, split="train")

    # Create label mappings
    labels = dataset.unique("label")
    id2label = {i: label for i, label in enumerate(labels)}
    label2id = {label: i for i, label in enumerate(labels)}
    num_labels = len(labels)

    print(f"Found {num_labels} unique labels: {labels}")

    # Split dataset
    train_texts, eval_texts, train_labels, eval_labels = train_test_split(
        dataset["text"], dataset["label"], test_size=0.2, stratify=dataset["label"]
    )

    # --- 2. Tokenize Data ---
    print(f"Loading tokenizer for '{args.model_name}'...")
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)

    train_encodings = tokenizer(train_texts, truncation=True, padding=True)
    eval_encodings = tokenizer(eval_texts, truncation=True, padding=True)

    # Convert labels to IDs
    def labels_to_ids(label_list, mapping):
        return [mapping[lbl] for lbl in label_list]

    train_labels_ids = labels_to_ids(train_labels, label2id)
    eval_labels_ids = labels_to_ids(eval_labels, label2id)

    class GenesisDataset(torch.utils.data.Dataset):
        def __init__(self, encodings, labels):
            self.encodings = encodings
            self.labels = labels

        def __getitem__(self, idx):
            item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
            item['labels'] = torch.tensor(self.labels[idx])
            return item

        def __len__(self):
            return len(self.labels)

    train_dataset = GenesisDataset(train_encodings, train_labels_ids)
    eval_dataset = GenesisDataset(eval_encodings, eval_labels_ids)
    print("Dataset prepared and tokenized.")

    # --- 3. Load and Configure Model ---
    print(f"Loading model '{args.model_name}' for sequence classification...")
    model = AutoModelForSequenceClassification.from_pretrained(
        args.model_name,
        num_labels=num_labels,
        id2label=id2label,
        label2id=label2id
    )

    # --- 4. Train the Model ---
    def compute_metrics(pred):
        labels = pred.label_ids
        preds = pred.predictions.argmax(-1)
        precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='weighted')
        acc = accuracy_score(labels, preds)
        return {'accuracy': acc, 'f1': f1, 'precision': precision, 'recall': recall}

    training_args = TrainingArguments(
        output_dir=os.path.join(args.output_dir, "training_checkpoints"),
        num_train_epochs=3,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        warmup_steps=50,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=10,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        compute_metrics=compute_metrics,
    )

    print("Starting fine-tuning...")
    trainer.train()
    print("Fine-tuning complete.")

    # --- 5. Save the Final Model ---
    final_path = os.path.join(args.output_dir, "final_model")
    trainer.save_model(final_path)
    tokenizer.save_pretrained(final_path)
    print(f"L2 Router model saved successfully to: {final_path}")

    # Save the label mapping as well, it's crucial for inference
    with open(os.path.join(final_path, "label_mappings.json"), "w") as f:
        json.dump({"id2label": id2label, "label2id": label2id}, f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Genesis Core V4: L2 Router Trainer")
    parser.add_argument("--model_name", type=str, default="distilbert-base-uncased", help="Base transformer model for classification.")
    parser.add_argument("--data_path", type=str, required=True, help="Path to the training data in JSON Lines format.")
    parser.add_argument("--output_dir", type=str, required=True, help="Directory to save the fine-tuned L2 router model.")

    # As before, this script is for the user's environment.
    print("L2 Router training script created. Use in a GPU environment.")
    print("Example command is in the script's docstring.")
