"""
Genesis Core V9: The Chimera Core (Live Intelligence)

This is the high-performance inference engine for the Genesis system,
now powered by a complete, in-house Generative Transformer model.
"""
import torch
from typing import List, Tuple, Dict, Any

from genesis_core.inference.transformer_model import GenerativeTransformer

# --- Simple Tokenizer for Demonstration ---
class SimpleTokenizer:
    """A basic, character-level tokenizer for demonstration purposes."""
    def __init__(self):
        # Simple vocabulary: lowercase letters, numbers, and basic punctuation
        chars = "abcdefghijklmnopqrstuvwxyz0123456789 .,?!<>"
        self.vocab = {ch: i+2 for i, ch in enumerate(chars)}
        self.vocab["<pad>"] = 0
        self.vocab["<eos>"] = 1 # End of Sentence token
        self.reverse_vocab = {i: ch for ch, i in self.vocab.items()}
        self.eos_token_id = 1

    @property
    def vocab_size(self):
        return len(self.vocab)

    def encode(self, text: str) -> List[int]:
        """Converts a string to a list of token IDs."""
        return [self.vocab.get(ch, 0) for ch in text.lower()]

    def decode(self, token_ids: List[int]) -> str:
        """Converts a list of token IDs back to a string."""
        return "".join([self.reverse_vocab.get(id, "") for id in token_ids])

class ChimeraCore:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ChimeraCore, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, verbose: bool = False):
        if self._initialized: return

        print("--- Initializing Chimera Core with Generative Transformer ---")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = SimpleTokenizer()

        # Define the model configuration
        model_config: Dict[str, Any] = {
            "vocab_size": self.tokenizer.vocab_size,
            "d_model": 128,
            "num_heads": 4,
            "num_layers": 3,
            "max_seq_len": 128,
        }

        self.model = GenerativeTransformer(model_config).to(self.device)
        self.model.eval() # Set model to evaluation mode
        self._initialized = True
        print(f"--- Chimera Core Initialized on device: {self.device} ---")

    @torch.no_grad()
    def generate_response(self, instruction: str, max_new_tokens: int = 50) -> Tuple[str, str]:
        """
        Generates a text response using the auto-regressive Transformer model.
        """
        print(f"Generating response for: '{instruction}'")

        # 1. Tokenize the input instruction
        input_ids = self.tokenizer.encode(instruction)
        input_tensor = torch.tensor([input_ids], device=self.device)

        # 2. Auto-regressive generation loop
        for _ in range(max_new_tokens):
            # Get model predictions (logits)
            logits = self.model(input_tensor)

            # Get the predicted token for the very last position
            next_token_logits = logits[:, -1, :]
            next_token_id = torch.argmax(next_token_logits, dim=-1).unsqueeze(-1)

            # Stop if the model predicts the end-of-sentence token
            if next_token_id.item() == self.tokenizer.eos_token_id:
                break

            # Append the predicted token to the input and continue
            input_tensor = torch.cat([input_tensor, next_token_id], dim=1)

        # 3. Decode the generated tokens into a text response
        generated_ids = input_tensor[0].tolist()
        response_text = self.tokenizer.decode(generated_ids)

        dispatch_id = "transformer-dispatch-001"
        return dispatch_id, response_text

# --- Automated Test Mode ---
if __name__ == '__main__':
    print("--- Chimera Core Automated Test ---")
    try:
        core = ChimeraCore()

        instruction = "hello world"
        print(f"\n> Instruction: '{instruction}'")

        _, response = core.generate_response(instruction)
        print(f"\n> Genesis raw response: '{response}'")

        # The actual output is deterministic but effectively gibberish
        # as the model is not trained. The test is to ensure it *generates*
        # something without crashing.
        generated_text = response[len(instruction):].strip()
        print(f"> Generated text: '{generated_text}'")

        assert len(generated_text) > 0
        print("\n[PASS] Model generated a response without crashing.")

    except Exception as e:
        import traceback
        print(f"\nAn unexpected error occurred: {e}")
        traceback.print_exc()

    print("\n--- Automated Test Complete ---")
