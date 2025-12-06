"""
Genesis Core V9: The Chimera Core (Live Intelligence)

This is the high-performance inference engine for the Genesis system,
now powered by a real LLM.
"""
import os
from llama_cpp import Llama
from typing import List, Tuple

from core.dispatch_tracker import record_dispatch_event

class ChimeraCore:
    # ... (class definition remains the same) ...
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ChimeraCore, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    def __init__(self, base_model_path: str = "Phi-3-mini-4k-instruct-q4.gguf", n_gpu_layers: int = 0, verbose: bool = False):
        if self._initialized: return
        if not os.path.exists(base_model_path):
            raise FileNotFoundError(f"Base model not found at: {base_model_path}. Please run 'setup.sh' or download it.")
        print(f"--- Initializing Chimera Core with REAL model ---")
        print(f"Loading base model: {base_model_path}")
        self.llm = Llama(model_path=base_model_path, n_gpu_layers=n_gpu_layers, n_ctx=2048, verbose=verbose)
        self.current_adapters = []
        self._initialized = True
        print("--- Chimera Core Initialized Successfully ---")
    def generate_response(self, instruction: str, adapter_paths: List[str] = None) -> Tuple[str, str]:
        dispatch_id = record_dispatch_event(adapter_paths or [])
        prompt = f"<|user|>\n{instruction}<|end|>\n<|assistant|>\n"
        print("Generating real response...")
        output = self.llm(prompt, max_tokens=256, stop=["<|end|>"], echo=False)
        response_text = output["choices"][0]["text"].strip()
        return dispatch_id, response_text

# --- Automated Test Mode ---
if __name__ == '__main__':
    print("--- Chimera Core Automated Test ---")
    try:
        core = ChimeraCore()

        instruction = "Explain the concept of a 'Mixture of Experts' in AI, in three sentences."
        print(f"\n> {instruction}")

        _, response = core.generate_response(instruction)
        print(f"\nGenesis: {response}\n")

        # Add an assertion to make it a real test
        assert len(response) > 20
        assert "expert" in response.lower()
        print("[PASS] Generated a valid, on-topic response.")

    except FileNotFoundError as e:
        print(f"\nError: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

    print("\n--- Automated Test Complete ---")
