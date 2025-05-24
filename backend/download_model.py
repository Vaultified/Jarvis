from huggingface_hub import hf_hub_download
import os

def download_mistral_model():
    # Create models directory if it doesn't exist
    models_dir = "llama.cpp/models"
    os.makedirs(models_dir, exist_ok=True)
    
    # Download the model
    print("Downloading Mistral model...")
    model_path = hf_hub_download(
        repo_id="TheBloke/Mistral-7B-v0.1-GGUF",
        filename="mistral-7b-v0.1.Q4_0.gguf",
        local_dir=models_dir
    )
    print(f"Model downloaded successfully to: {model_path}")
    return model_path

if __name__ == "__main__":
    download_mistral_model() 