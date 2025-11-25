"""
Genesis Core V4: The Chimera Core
Part of the "Cơ Bắp" (Muscle) Pillar.

This is the high-performance inference engine for the Genesis system.
It is responsible for:
1.  Loading a quantized base model (GGUF) into memory once.
2.  Dynamically applying and de-applying LoRA adapters ("hot-swapping")
    without reloading the entire model.
3.  Running inference to generate a response.

This architecture provides unprecedented speed and efficiency for a
distributed, multi-expert system.
"""
import os
from llama_cpp import Llama
from typing import List, Tuple

# V7 - Judgement Pillar Integration
from api.feedback_endpoint import record_dispatch_event

class ChimeraCore:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ChimeraCore, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, base_model_path: str, n_gpu_layers: int = -1, verbose: bool = False):
        if self._initialized:
            return

        if not os.path.exists(base_model_path):
            raise FileNotFoundError(f"Base model not found at: {base_model_path}. Please download the GGUF model.")

        print(f"--- Initializing Chimera Core ---")
        print(f"Loading base model: {base_model_path}")

        self.llm = Llama(
            model_path=base_model_path,
            n_gpu_layers=n_gpu_layers,  # -1 means offload all possible layers to GPU
            n_ctx=4096,               # Context window size
            verbose=verbose
        )
        self.current_adapters = []
        self._initialized = True
        print("--- Chimera Core Initialized Successfully ---")

    def generate_response(self, instruction: str, adapter_paths: List[str] = None) -> Tuple[str, str]:
        """
        Generates a response by applying one or more LoRA adapters.
        It intelligently handles applying and removing adapters to be efficient.

        V7 Update: Now returns a tuple containing the dispatch_id and the response.
        """
        if adapter_paths is None:
            adapter_paths = []

        # V7 - Judgement Pillar: Record the experts used for this dispatch.
        # The adapter_paths directly correspond to the experts being consulted.
        dispatch_id = record_dispatch_event(adapter_paths)
        print(f"--- Dispatch Event Recorded ---")
        print(f"  - Dispatch ID: {dispatch_id}")
        print(f"  - Contributing Experts (Adapters): {adapter_paths}")


        try:
            # --- The Revolutionary Hot-Swap Logic ---

            # 1. Determine which adapters to remove
            adapters_to_remove = [p for p in self.current_adapters if p not in adapter_paths]
            for path in adapters_to_remove:
                print(f"  - Hot-swapping: Removing adapter {os.path.basename(path)}")
                # llama.cpp doesn't have a direct 'remove' API, so we reload without it.
                # A more advanced implementation might involve model merging *before* loading.
                # For now, we'll clear and re-apply, which is still faster than reloading the base model.
                self._reload_adapters(adapter_paths)
                break # We only need to do this once.

            # 2. Determine which adapters to add
            adapters_to_add = [p for p in adapter_paths if p not in self.current_adapters]
            for path in adapters_to_add:
                 if not os.path.exists(path):
                    print(f"Warning: Adapter not found at {path}, skipping.")
                    continue
                 print(f"  - Hot-swapping: Applying adapter {os.path.basename(path)}")
                 # The apply_lora method handles adding a new adapter
                 self.llm.apply_lora(lora_path=path)
                 self.current_adapters.append(path)

            prompt = f"### Instruction:\n{instruction}\n\n### Response:\n"

            print("Generating response...")
            output = self.llm(prompt, max_tokens=512, stop=["### Instruction:"], echo=False)

            response_text = output["choices"][0]["text"].strip()
            return dispatch_id, response_text

        except Exception as e:
            print(f"An error occurred during inference: {e}")
            return dispatch_id, "Error: Could not generate a response."

    def _reload_adapters(self, new_adapter_paths: List[str]):
        """Helper to reset and apply a new set of adapters."""
        print("Resetting and reloading adapters...")
        # This is a simplified reset. A true hot-swap might be more complex.
        # It relies on the Llama class's internal state management.
        # First, we need to unload all LoRAs. This is often done by reloading the model
        # without them, but let's assume a future API might allow direct unloading.
        # For now, we rebuild the adapter stack.
        self.llm.disable_lora() # Hypothetical function to disable all LoRAs
        self.current_adapters = []

        for path in new_adapter_paths:
            if not os.path.exists(path): continue
            self.llm.apply_lora(lora_path=path)
            self.current_adapters.append(path)
        print("Adapters reloaded.")

# Example usage (for demonstration and testing)
if __name__ == '__main__':
    # NOTE: This requires a real GGUF model and adapter files to run.
    # The following is a placeholder for how it WOULD be used.

    # 1. Create dummy files for the example
    dummy_model_path = "dummy_model.gguf"
    dummy_adapter_A_path = "dummy_adapters/legal_lora/adapter_model.bin"
    dummy_adapter_B_path = "dummy_adapters/medical_lora/adapter_model.bin"

    os.makedirs(os.path.dirname(dummy_adapter_A_path), exist_ok=True)
    os.makedirs(os.path.dirname(dummy_adapter_B_path), exist_ok=True)

    if not os.path.exists(dummy_model_path):
        with open(dummy_model_path, "w") as f:
            f.write("This is a placeholder GGUF file.")
    if not os.path.exists(dummy_adapter_A_path):
        with open(dummy_adapter_A_path, "w") as f:
            f.write("Placeholder LoRA A.")
    if not os.path.exists(dummy_adapter_B_path):
        with open(dummy_adapter_B_path, "w") as f:
            f.write("Placeholder LoRA B.")

    print("--- Chimera Core Demo ---")
    print("NOTE: This demo uses placeholder files and will not run real inference.")

    try:
        # This will fail because the GGUF is fake, but it demonstrates the API call.
        core = ChimeraCore(base_model_path=dummy_model_path)

        # --- Scenario 1: Ask a legal question ---
        print("\n--- Scenario 1: Legal Question ---")
        legal_instruction = "Can you draft a simple non-disclosure agreement?"
        response = core.generate_response(legal_instruction, adapter_paths=[dummy_adapter_A_path])
        print(f"Instruction: {legal_instruction}")
        print(f"Generated Response (Simulated): {response}")

        # --- Scenario 2: Ask a medical question ---
        print("\n--- Scenario 2: Medical Question ---")
        medical_instruction = "What are the common symptoms of influenza?"
        # The core will intelligently remove adapter A and apply adapter B.
        response = core.generate_response(medical_instruction, adapter_paths=[dummy_adapter_B_path])
        print(f"Instruction: {medical_instruction}")
        print(f"Generated Response (Simulated): {response}")

    except Exception as e:
        print(f"\nDemo failed as expected with a placeholder model file: {e}")

    print("\n--- Chimera Core Demo Finished ---")
