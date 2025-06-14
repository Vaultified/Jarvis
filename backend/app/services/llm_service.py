import re
import logging
import os
from pathlib import Path
import multiprocessing
from llama_cpp import Llama
from .prompt_handler import PromptHandler

logger = logging.getLogger(__name__)

class LLMService:
    # Pre-compile regex patterns for efficiency
    EMAIL_PATTERN = re.compile(r"send an email to ([^\s]+) about ([^:]+): (.+)")
    
    def __init__(self):
        # Initialize the prompt handler
        self.prompt_handler = PromptHandler()
        
        # Path to the GGUF model
        self.model_path = os.getenv("MODEL_PATH", "models/llama-2-7b-chat.gguf")
        if not Path(self.model_path).exists():
            raise FileNotFoundError(
                f"Model not found at {self.model_path}. "
                "Please make sure the model file exists in the models directory."
            )
            
        # Use all available CPU cores for n_threads
        n_threads = multiprocessing.cpu_count()
        logger.info(f"Detected {n_threads} CPU cores for Llama model.")
        
        # Load model using llama.cpp
        logger.info(f"Loading model from {self.model_path}...")
        try:
            self.model = Llama(
                model_path=self.model_path,
                n_ctx=2048,  # Context window
                n_threads=n_threads
            )
            logger.info("Model loaded successfully!")
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise
        
        # System prompt for command instructions
        self.system_prompt = """You are a helpful AI assistant. Your responses should be natural and conversational, just like ChatGPT.

For regular conversation:
- Be friendly and helpful
- Keep responses concise and relevant
- Don't use templates or placeholders
- Don't include instruction tokens or formatting
- Don't include names or labels

For email commands, respond with exactly:
send an email to [email] about [subject] saying [message]

For Drive commands:
- To list all folders: list all folders in my Drive
- To search in a folder: list files in my Drive in "[folder_name]"
- To search for files: search my Drive for "[query]"
- To read a PDF: read the PDF [pdf_name]
- To query PDF content: what's in the PDF [pdf_name] about [topic]

Example of natural conversation:
User: Hi
Assistant: Hello! How can I help you today?

User: How are you?
Assistant: I'm doing well, thank you for asking! How can I assist you today?

User: What's the weather like?
Assistant: I don't have access to real-time weather information, but I'd be happy to help you with other tasks!"""

    def generate_response(self, prompt: str) -> str:
        try:
            # Use the prompt handler to process the prompt
            result = self.prompt_handler.handle_prompt(prompt)
            
            # If the prompt handler returned a result, use it
            if result is not None:
                # Check if it's an error response
                if hasattr(result, 'isError') and result.isError:
                    return result.content[0].text
                    
                # Check if it's an image response
                if result.content and len(result.content) > 0:
                    content = result.content[0]
                    if content.mimeType and content.mimeType.startswith('image/'):
                        # For image responses, return the base64 data directly
                        return content.text
                    else:
                        # For text responses
                        return content.text
                
            # If no specific intent was matched or there was an error,
            # fall back to the LLM for general conversation
            formatted_prompt = f"[INST] {self.system_prompt}\n\nUser: {prompt} [/INST]"
            logger.info("Generating natural language response...")
            output = self.model(
                formatted_prompt,
                max_tokens=256,
                temperature=0.7,
                top_p=0.95,
                repeat_penalty=1.1,
                stop=["User:", "\n\n"]
            )
            response = output["choices"][0]["text"]
            cleaned_output = response.strip()
            cleaned_output = re.sub(r'\[/INST\]', '', cleaned_output)
            cleaned_output = re.sub(r'User:|Assistant:', '', cleaned_output)
            cleaned_output = re.sub(r'\[.*?\]', '', cleaned_output)
            cleaned_output = cleaned_output.strip()
            logger.info("Response generated successfully")
            return cleaned_output
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}", exc_info=True)
            return f"An error occurred: {str(e)}"