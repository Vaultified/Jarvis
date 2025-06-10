from pathlib import Path
import os
import re
from typing import Dict, Any, Optional, Tuple
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

For Drive commands:
- To list all folders: list all folders in my Drive
- To search in a folder: list files in my Drive in "[folder_name]"
- To search for files: search my Drive for "[query]"

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

    def _extract_drive_info(self, text: str) -> Tuple[str, str, str]:
        """Extract Drive command, folder name, and search query from text."""
        # Pattern for listing all folders
        list_folders_pattern = r'list\s+all\s+folders\s+(?:in\s+)?(?:my\s+)?(?:Drive|Google\s+Drive)'
        
        # Pattern for searching files in a specific folder
        search_pattern = r'search\s+(?:for\s+)?(?:files\s+)?(?:in\s+)?(?:my\s+)?(?:Drive|Google\s+Drive)\s+(?:for|containing|with)\s+[\'"]([^\'"]+)[\'"]\s+(?:in|from|under)\s+[\'"]([^\'"]+)[\'"]'
        
        # Pattern for listing files in a specific folder
        list_files_pattern = r'list\s+(?:files\s+)?(?:in\s+)?(?:my\s+)?(?:Drive|Google\s+Drive)\s+(?:in|from|under)\s+[\'"]([^\'"]+)[\'"]'
        
        if re.search(list_folders_pattern, text, re.IGNORECASE):
            return "list_folders", None, None
            
        search_match = re.search(search_pattern, text, re.IGNORECASE)
        if search_match:
            return "search", search_match.group(2), search_match.group(1)
            
        list_files_match = re.search(list_files_pattern, text, re.IGNORECASE)
        if list_files_match:
            return "list_files", list_files_match.group(1), None
            
        return None, None, None

    def _send_email(self, to: str, subject: str, body: str) -> str:
        try:
            logger.info(f"Preparing to send email to {to}")
            logger.info(f"Subject: {subject}")
            logger.info(f"Body: {body}")

            # Use the MCP Gmail service instead of HTTP request
            from app.services.gmail_service import send_email  # Import MCP tool

            # Always pass a list for 'to' as required by gmail_service
            result = send_email(to=[to], subject=subject, body=body)
            logger.info(f"Gmail MCP send_email result: {result}")

            if isinstance(result, dict) and result.get("success"):
                return "Email sent successfully! Please check your inbox."
            elif isinstance(result, dict) and result.get("message"):
                return f"Email sending failed: {result.get('message', 'Unknown error')}"
            elif isinstance(result, str):
                return result
            else:
                return "The email may have been sent successfully. Please check your inbox to confirm."

        except Exception as e:
            logger.error(f"Unexpected error while sending email: {str(e)}", exc_info=True)
            return f"An unexpected error occurred while trying to send the email: {str(e)}"

    def _search_drive(self, command: str, folder_name: str = None, search_query: str = None) -> str:
        """Search Google Drive using the MCP Drive service."""
        try:
            # Import the MCP Drive service
            from app.services.drive_service import list_root_folders, search_files
            
            if command == "list_folders":
                # Use the MCP tool to list folders
                folders = list_root_folders()
                if not folders:
                    return "No folders found in your Drive."
                return "Found folders in your Drive:\n" + "\n".join([f"- {folder['name']}" for folder in folders])
            
            elif command == "list_files":
                # Use the MCP tool to search files in folder
                files = search_files(query="", folder_name=folder_name)
                if not files:
                    return f"No files found in folder '{folder_name}'."
                return f"Files in folder '{folder_name}':\n" + "\n".join([f"- {file['name']}" for file in files])
            
            elif command == "search":
                # Use the MCP tool to search files
                files = search_files(query=search_query, folder_name=folder_name)
                if not files:
                    return f"No files found matching '{search_query}' in folder '{folder_name}'."
                return f"Found files matching '{search_query}' in folder '{folder_name}':\n" + "\n".join([f"- {file['name']}" for file in files])
            
            return "Invalid Drive command."
            
        except Exception as e:
            print(f"Error in Drive search: {e}")
            return f"Error searching Drive: {str(e)}"

    def _extract_weather_info(self, text: str) -> Optional[Tuple[float, float]]:
        """Extract latitude and longitude or city name from a weather-related prompt."""
        # Pattern: 'weather in [lat],[lon]' or 'weather at [lat],[lon]'
        match = re.search(r'weather (?:in|at|for)?\s*([+-]?\d+\.\d+),\s*([+-]?\d+\.\d+)', text, re.IGNORECASE)
        if match:
            try:
                lat = float(match.group(1))
                lon = float(match.group(2))
                return lat, lon
            except Exception:
                return None
        # Pattern: 'weather in [city]' or 'weather at [city]' or 'weather update for [city]' or 'what's the weather in [city]'
        match_city = re.search(r'(?:weather|weather update|what\'?s the weather|show me the weather|tell me the weather)(?:\s*(?:in|at|for))?\s*([a-zA-Z\s]+)', text, re.IGNORECASE)
        if match_city:
            city = match_city.group(1).strip()
            return city
        return None

    def _get_weather(self, location) -> str:
        try:
            from app.services.weather_service import get_weather_info
            # location can be (lat, lon) tuple or city name string
            result = get_weather_info(location)
            if isinstance(result, str):
                return result  # error message from weather_service
            if result.get("success"):
                return result["message"]
            else:
                return f"Weather fetch failed: {result.get('message', 'Unknown error')}"
        except Exception as e:
            logger.error(f"Error fetching weather: {str(e)}", exc_info=True)
            return f"An error occurred while fetching weather: {str(e)}"

    def generate_response(self, prompt: str) -> str:
        """Generate a response using the LLaMA model."""
        try:
            # Check for Drive commands first
            command, folder_name, search_query = self._extract_drive_info(prompt)
            if command:
                return self._search_drive(command, folder_name, search_query)
            
            # Check for email command
            email_info = self._extract_email_info(prompt)
            if email_info:
                logger.info(f"Detected email command: {email_info}")
                return self._send_email(
                    email_info["to"],
                    email_info["subject"],
                    email_info["body"]
                )
            
            # Check for weather command
            weather_info = self._extract_weather_info(prompt)
            if weather_info:
                return self._get_weather(weather_info)
            
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
            return f"An error occurred: {str(e)}"