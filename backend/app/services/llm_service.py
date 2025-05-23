from ctransformers import AutoModelForCausalLM
from pathlib import Path
import os

class LLMService:
    def __init__(self):
        # Path to the model
        self.model_path = os.getenv("MODEL_PATH", "models/llama-2-7b-chat.gguf")
        
        if not Path(self.model_path).exists():
            raise FileNotFoundError(f"Model not found at {self.model_path}. Please download a model and update MODEL_PATH in .env")
        
        # Initialize the model
        self.llm = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            model_type="llama",
            gpu_layers=0  # CPU only
        )
    
    def generate_response(self, prompt: str) -> str:
        # Format the prompt
        formatted_prompt = f"Human: {prompt}\n\nAssistant:"
        
        # Generate response
        response = self.llm(
            formatted_prompt,
            max_new_tokens=512,
            temperature=0.7,
            stop=["Human:", "\n\n"]
        )
        
        return response.strip() 