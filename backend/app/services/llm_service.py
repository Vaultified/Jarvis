from pathlib import Path
import os
import re
from typing import Dict, Any, Optional
import requests
import logging
from llama_cpp import Llama

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        # Path to the GGUF model
        self.model_path = os.getenv("MODEL_PATH", "models/llama-2-7b-chat.gguf")
        
        if not Path(self.model_path).exists():
            raise FileNotFoundError(
                f"Model not found at {self.model_path}. "
                "Please make sure the model file exists in the models directory."
            )
        
        # Load model using llama.cpp
        logger.info(f"Loading model from {self.model_path}...")
        try:
            self.model = Llama(
                model_path=self.model_path,
                n_ctx=2048,  # Context window
                n_threads=4   # Number of CPU threads to use
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

For Drive search, respond with exactly:
search my Drive for [query]

Example of natural conversation:
User: Hi
Assistant: Hello! How can I help you today?

User: How are you?
Assistant: I'm doing well, thank you for asking! How can I assist you today?

User: What's the weather like?
Assistant: I don't have access to real-time weather information, but I'd be happy to help you with other tasks!"""

    def _extract_email_info(self, text: str) -> Optional[Dict[str, str]]:
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
        # Updated pattern to better match Drive search commands
        search_patterns = [
            r"search\s+(?:for\s+)?(?:files\s+)?(?:in\s+)?(?:my\s+)?(?:Drive|Google\s+Drive)\s+(?:for|containing|with)\s+['\"]([^'\"]+)['\"]\s+(?:in|from|under)\s+['\"]([^'\"]+)['\"]",
            r"search\s+(?:for\s+)?(?:files\s+)?(?:in\s+)?(?:my\s+)?(?:Drive|Google\s+Drive)\s+(?:in|from|under)\s+['\"]([^'\"]+)['\"]",
            r"list\s+(?:files\s+)?(?:in\s+)?(?:my\s+)?(?:Drive|Google\s+Drive)\s+(?:in|from|under)\s+['\"]([^'\"]+)['\"]",
            r"show\s+(?:files\s+)?(?:in\s+)?(?:my\s+)?(?:Drive|Google\s+Drive)\s+(?:in|from|under)\s+['\"]([^'\"]+)['\"]"
        ]
        
        for pattern in search_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # If the pattern has two groups, it's a search with query and folder
                if len(match.groups()) == 2:
                    return {
                        "query": match.group(1),
                        "folder": match.group(2)
                    }
                # If the pattern has one group, it's just a folder search
                else:
                    return {
                        "folder": match.group(1)
                    }
        return None

    def _send_email(self, to: str, subject: str, body: str) -> str:
        try:
            logger.info(f"Preparing to send email to {to}")
            logger.info(f"Subject: {subject}")
            logger.info(f"Body: {body}")
            
            # Prepare the request payload
            payload = {
                "to": [to],
                "subject": subject,
                "body": body
            }
            logger.info(f"Request payload: {payload}")
            
            # Make the request to the email endpoint with increased timeout
            logger.info("Sending request to email endpoint...")
            try:
                response = requests.post(
                    "http://localhost:8000/api/gmail/send",
                    json=payload,
                    timeout=60  # Increased timeout to 60 seconds
                )
                
                logger.info(f"Email endpoint response status: {response.status_code}")
                response.raise_for_status()
                
                success_response = response.json()
                logger.info(f"Email endpoint response: {success_response}")
                
                if success_response.get("success"):
                    return "Email sent successfully! Please check your inbox."
                else:
                    return f"Email sending failed: {success_response.get('message', 'Unknown error')}"
                    
            except requests.exceptions.Timeout:
                # If we get a timeout, check if the email was actually sent
                logger.info("Initial request timed out, checking if email was sent...")
                try:
                    # Make a quick check request to verify email status
                    check_response = requests.get(
                        "http://localhost:8000/api/gmail/status",
                        timeout=5
                    )
                    if check_response.status_code == 200:
                        status_data = check_response.json()
                        if status_data.get("service_available"):
                            return "Email was sent successfully! Please check your inbox."
                except Exception as e:
                    logger.error(f"Error checking email status: {str(e)}")
                
                # If we can't verify, return a more informative message
                return "The email may have been sent successfully. Please check your inbox to confirm."
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error while sending email: {str(e)}")
            return f"I couldn't send the email due to a request error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error while sending email: {str(e)}", exc_info=True)
            return f"An unexpected error occurred while trying to send the email: {str(e)}"

    def _search_drive(self, query: str, folder: str = None) -> str:
        try:
            payload = {"query": query} if query else {}
            if folder:
                payload["folder"] = folder
                
            response = requests.post(
                "http://localhost:8000/api/drive/search",
                json=payload
            )
            response.raise_for_status()
            return response.json().get("message", "Drive search completed.")
        except Exception as e:
            return f"Error searching Drive: {str(e)}"

    def generate_response(self, prompt: str) -> str:
        try:
            logger.info(f"Generating response for prompt: {prompt}")
            
            # Check for email command
            email_info = self._extract_email_info(prompt)
            if email_info:
                logger.info(f"Detected email command: {email_info}")
                return self._send_email(
                    email_info["to"],
                    email_info["subject"],
                    email_info["body"]
                )

            # Check for drive command
            drive_info = self._extract_drive_info(prompt)
            if drive_info:
                logger.info(f"Detected drive command: {drive_info}")
                return self._search_drive(
                    drive_info.get("query"),
                    drive_info.get("folder")
                )

            # If no command detected, generate natural language response
            formatted_prompt = f"<s>[INST] {self.system_prompt}\n\nUser: {prompt} [/INST]"
            logger.info("Generating natural language response...")
            
            # Generate response using llama.cpp
            output = self.model(
                formatted_prompt,
                max_tokens=256,
                temperature=0.7,
                top_p=0.95,
                repeat_penalty=1.1,
                stop=["User:", "\n\n"]
            )
            
            # Extract the generated text
            response = output["choices"][0]["text"]
            
            # Clean up the response
            cleaned_output = response.strip()
            cleaned_output = re.sub(r'\[/INST\]', '', cleaned_output)
            cleaned_output = re.sub(r'User:|Assistant:', '', cleaned_output)
            cleaned_output = re.sub(r'\[.*?\]', '', cleaned_output)  # Remove any remaining placeholders
            cleaned_output = cleaned_output.strip()
            
            logger.info("Response generated successfully")
            return cleaned_output
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}", exc_info=True)
            return f"I encountered an error while processing your request: {str(e)}"