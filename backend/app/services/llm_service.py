from ctransformers import AutoModelForCausalLM
from pathlib import Path
import os

class LLMService:
    def __init__(self):
        # Path to the model
        self.model_path = os.getenv("MODEL_PATH", "llama.cpp/models/mistral-7b-v0.1.Q4_0.gguf")
        
        if not Path(self.model_path).exists():
            raise FileNotFoundError(f"Model not found at {self.model_path}. Please run download_model.py first")
        
        # Initialize the model
        self.llm = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            model_type="mistral",  # Changed from llama to mistral
            max_new_tokens=512,
            context_length=2048,
            gpu_layers=0  # CPU only
        )
    
    def generate_response(self, prompt: str) -> str:
        # Format the prompt for Mistral
        formatted_prompt = f"<s>[INST] {prompt} [/INST]"
        
        # Generate response with optimized parameters
        response = self.llm(
            formatted_prompt,
            max_new_tokens=512,
            temperature=0.7,
            top_p=0.95,
            repetition_penalty=1.1,
            stop=["</s>", "[INST]"]
        )
        
        return response.strip() 