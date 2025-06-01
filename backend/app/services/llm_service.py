from ctransformers import AutoModelForCausalLM
from pathlib import Path
import os
import re
from typing import Dict, Any, Optional
import requests

class LLMService:
    def __init__(self):
        # Path to the model
        self.model_path = os.getenv("MODEL_PATH", "models/llama-2-7b-chat.gguf")
        
        if not Path(self.model_path).exists():
            raise FileNotFoundError(f"Model not found at {self.model_path}. Please download the model first.")
        
        # Initialize the model with optimized parameters
        self.llm = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            model_type="llama",
            max_new_tokens=256,
            context_length=1024,
            gpu_layers=0,
            threads=os.cpu_count() or 4
        )
        
        # System prompt focused on direct service invocation
        self.system_prompt = """You are a helpful assistant that can send emails and work with Google Drive.
When you detect a command, execute it directly:

For emails:
- Extract email address, subject, and body
- Call the Gmail service to send the email
- Return the service response

For Drive:
- Extract search query or file ID
- Call the Drive service to search or read
- Return the service response

For regular conversation, respond naturally with text."""

    def _extract_email_info(self, text: str) -> Optional[Dict[str, str]]:
        """Extract email information from text."""
        # Pattern to match email commands
        email_pattern = r"send\s+(?:an\s+)?email\s+to\s+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\s+(?:about|with\s+subject|subject)\s+['\"]([^'\"]+)['\"]\s+(?:saying|message|body)\s+['\"]([^'\"]+)['\"]"
        match = re.search(email_pattern, text, re.IGNORECASE)
        if match:
            return {
                "to": match.group(1),
                "subject": match.group(2),
                "body": match.group(3)
            }
        return None

    def _extract_drive_info(self, text: str) -> Optional[Dict[str, str]]:
        """Extract Drive command information from text."""
        # Pattern to match drive search commands
        search_pattern = r"search\s+(?:for\s+)?(?:files\s+)?(?:in\s+)?(?:my\s+)?(?:Drive|Google\s+Drive)\s+(?:containing|for|with)\s+['\"]([^'\"]+)['\"]"
        match = re.search(search_pattern, text, re.IGNORECASE)
        if match:
            return {"query": match.group(1)}
        return None

    def _send_email(self, to: str, subject: str, body: str) -> str:
        """Send email using Gmail service."""
        try:
            response = requests.post(
                "http://localhost:8000/api/gmail/send",
                json={"to": [to], "subject": subject, "body": body},
            )
            response.raise_for_status()
            # The /api/gmail/send endpoint returns a JSON response on success
            # We should return a user-friendly message based on that response
            success_response = response.json()
            if success_response.get("success"):
                 # Directly return the success message from the API response
                 return success_response.get("message", "Email sent successfully!")
            else:
                 # This case should ideally be caught by raise_for_status, but as a fallback:
                 return f"Email sending failed: {success_response.get('message', 'Unknown error')}"
        except requests.exceptions.RequestException as e:
            return f"I couldn't send the email due to a request error: {str(e)}"
        except Exception as e:
            return f"An unexpected error occurred while trying to send the email: {str(e)}"

    def _search_drive(self, query: str) -> str:
        """Search Drive using Drive service."""
        try:
            response = requests.post(
                "http://localhost:8000/api/drive/search",
                json={"query": query},
                timeout=5
            )
            response.raise_for_status()
            results = response.json()
            return f"I found {len(results)} files matching your search."
        except Exception as e:
            return f"I couldn't search Drive: {str(e)}"

    def generate_response(self, prompt: str) -> str:
        # Check for email command
        email_info = self._extract_email_info(prompt)
        if email_info:
            return self._send_email(
                email_info["to"],
                email_info["subject"],
                email_info["body"]
            )

        # Check for drive command
        drive_info = self._extract_drive_info(prompt)
        if drive_info:
            return self._search_drive(drive_info["query"])

        # If no command detected, generate natural language response
        formatted_prompt = f"<s>[INST] {self.system_prompt}\n\nUser: {prompt} [/INST]"
        response = self.llm(
            formatted_prompt,
            max_new_tokens=256,
            temperature=0.7,
            top_p=0.95,
            repetition_penalty=1.1,
            stop=["</s>", "[INST]"],
            threads=os.cpu_count() or 4
        )
        
        return response.strip() 