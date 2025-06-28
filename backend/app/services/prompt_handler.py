from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
import logging
from dataclasses import dataclass
from mcp.types import TextContent, CallToolResult
import re
from pydantic import BaseModel, Field
from app.services.drive_service import list_resources, read_resource
from ..models.intent import Intent, IntentType

logger = logging.getLogger(__name__)

class IntentType(Enum):
    LIST_FOLDERS = "list_folders"
    LIST_FILES = "list_files"
    SEARCH_FILES = "search_files"
    READ_FILE = "read_file"
    SHOW_IMAGE = "show_image"
    QUERY_PDF = "query_pdf"
    SEND_EMAIL = "send_email"
    GET_WEATHER = "get_weather"
    CHAT = "chat"

@dataclass
class Intent:
    type: IntentType
    confidence: float
    entities: Dict[str, Any]
    raw_text: str

class PromptHandler:
    def __init__(self):
        # Initialize any required models or services
        self.intent_threshold = 0.7  # Minimum confidence threshold for intent classification
        
    def classify_intent(self, prompt: str) -> Intent:
        """
        Classify the user's intent using a combination of:
        1. Rule-based patterns (for simple cases)
        2. ML-based classification (for complex cases)
        3. Entity extraction
        """
        # First, try rule-based classification
        intent, confidence, entities = self._rule_based_classification(prompt)
        
        # If confidence is low, try ML-based classification
        if confidence < self.intent_threshold:
            ml_intent, ml_confidence, ml_entities = self._ml_based_classification(prompt)
            if ml_confidence > confidence:
                intent, confidence, entities = ml_intent, ml_confidence, ml_entities
        
        return Intent(
            type=intent,
            confidence=confidence,
            entities=entities,
            raw_text=prompt
        )

    def _rule_based_classification(self, prompt: str) -> Tuple[IntentType, float, Dict[str, Any]]:
        """Rule-based intent classification using patterns and keywords."""
        prompt = prompt.lower()
        entities = {}
        
        # Email operations
        if any(phrase in prompt for phrase in [
            "send an email", "send email", "email to", "send a message", "send message"
        ]):
            entities = self._extract_email_entities(prompt)
            return IntentType.SEND_EMAIL, 0.9, entities
        
        # Weather operations
        if any(phrase in prompt for phrase in [
            "weather", "temperature", "forecast", "how's the weather", "what's the weather",
            "weather in", "temperature in", "forecast for"
        ]):
            entities = self._extract_weather_entities(prompt)
            return IntentType.GET_WEATHER, 0.9, entities
        
        # File operations - more flexible image patterns
        if any(phrase in prompt for phrase in [
            "show me the image", "show me the picture", "display the image", "display the picture",
            "show the image", "show the picture", "display the photo", "show the photo",
            "show me the photo", "display image", "show image", "display picture", "show picture"
        ]):
            entities = self._extract_file_entities(prompt)
            return IntentType.SHOW_IMAGE, 0.9, entities
            
        if "read" in prompt and "pdf" in prompt:
            entities = self._extract_file_entities(prompt)
            return IntentType.READ_FILE, 0.9, entities
            
        if "what's in" in prompt and "pdf" in prompt:
            entities = self._extract_file_entities(prompt)
            return IntentType.QUERY_PDF, 0.9, entities
            
        # Drive operations
        if "list all folders" in prompt:
            return IntentType.LIST_FOLDERS, 0.95, {}
            
        if "list files" in prompt:
            entities = self._extract_folder_entities(prompt)
            return IntentType.LIST_FILES, 0.9, entities
            
        if "search" in prompt and "drive" in prompt:
            entities = self._extract_search_entities(prompt)
            return IntentType.SEARCH_FILES, 0.9, entities
            
        # Default to chat
        return IntentType.CHAT, 0.5, {}

    def _ml_based_classification(self, prompt: str) -> Tuple[IntentType, float, Dict[str, Any]]:
        """
        ML-based intent classification.
        This is a placeholder for implementing actual ML-based classification.
        You could use:
        - Fine-tuned transformer models (BERT, RoBERTa)
        - Pre-trained intent classification models
        - Custom models trained on your specific use cases
        """
        # TODO: Implement actual ML-based classification
        return IntentType.CHAT, 0.5, {}

    def _extract_file_entities(self, prompt: str) -> Dict[str, Any]:
        """Extract file-related entities from the prompt."""
        entities = {}
        
        # Extract file name - more flexible pattern for images
        file_patterns = [
            r'(?:file|document|pdf|image|picture|photo)\s+(?:named|called|titled)?\s*[\'"]([^\'"]+)[\'"]',
            r'(?:file|document|pdf|image|picture|photo)\s+(?:named|called|titled)?\s+(\S+)',
            r'(?:show me the|display the|show the)\s+(?:image|picture|photo)\s+[\'"]([^\'"]+)[\'"]',
            r'(?:show me the|display the|show the)\s+(?:image|picture|photo)\s+(\S+)',
            r'(?:display|show)\s+(?:image|picture|photo)\s+[\'"]([^\'"]+)[\'"]',
            r'(?:display|show)\s+(?:image|picture|photo)\s+(\S+)'
        ]
        
        for pattern in file_patterns:
            file_match = re.search(pattern, prompt, re.IGNORECASE)
            if file_match:
                entities["file_name"] = file_match.group(1)
                break
        
        # Extract query for PDF content
        query_pattern = r'(?:about|containing|with)\s+[\'"]([^\'"]+)[\'"]'
        query_match = re.search(query_pattern, prompt, re.IGNORECASE)
        if query_match:
            entities["query"] = query_match.group(1)
        
        return entities

    def _extract_folder_entities(self, prompt: str) -> Dict[str, Any]:
        """Extract folder-related entities from the prompt."""
        entities = {}
        
        # Extract folder name
        folder_pattern = r'(?:in|from|under|inside)\s+[\'"]([^\'"]+)[\'"]'
        folder_match = re.search(folder_pattern, prompt, re.IGNORECASE)
        if folder_match:
            entities["folder_name"] = folder_match.group(1)
        
        return entities

    def _extract_search_entities(self, prompt: str) -> Dict[str, Any]:
        """Extract search-related entities from the prompt."""
        entities = {}
        
        # Extract search query
        query_pattern = r'(?:for|containing|with)\s+[\'"]([^\'"]+)[\'"]'
        query_match = re.search(query_pattern, prompt, re.IGNORECASE)
        if query_match:
            entities["query"] = query_match.group(1)
        
        # Extract folder name if specified
        folder_pattern = r'(?:in|from|under)\s+[\'"]([^\'"]+)[\'"]'
        folder_match = re.search(folder_pattern, prompt, re.IGNORECASE)
        if folder_match:
            entities["folder_name"] = folder_match.group(1)
        
        return entities

    def _extract_weather_entities(self, prompt: str) -> Dict[str, Any]:
        """Extract weather-related entities from the prompt."""
        entities = {}
        
        # Extract location - multiple patterns for flexibility
        location_patterns = [
            r'(?:weather|temperature|forecast)\s+(?:in|at|for)\s+[\'"]([^\'"]+)[\'"]',
            r'(?:weather|temperature|forecast)\s+(?:in|at|for)\s+(\S+)',
            r'(?:in|at|for)\s+[\'"]([^\'"]+)[\'"]',
            r'(?:in|at|for)\s+(\S+)'
        ]
        
        for pattern in location_patterns:
            location_match = re.search(pattern, prompt, re.IGNORECASE)
            if location_match:
                entities["location"] = location_match.group(1)
                break
        
        return entities

    def _extract_email_entities(self, prompt: str) -> Dict[str, Any]:
        """Extract email-related entities from the prompt."""
        entities = {}
        
        # More comprehensive pattern to match the full email format
        # Matches: "send an email to [email] about [subject] saying [body]"
        full_pattern = r'send\s+(?:an\s+)?email\s+to\s+([^\s]+@[^\s]+)\s+about\s+[\'"]([^\'"]+)[\'"]\s+saying\s+[\'"]([^\'"]+)[\'"]'
        full_match = re.search(full_pattern, prompt, re.IGNORECASE)
        
        if full_match:
            entities["to"] = full_match.group(1)
            entities["subject"] = full_match.group(2)
            entities["body"] = full_match.group(3)
            return entities
        
        # Fallback patterns for individual components
        # Extract recipient email
        email_patterns = [
            r'send\s+(?:an\s+)?email\s+to\s+([^\s]+@[^\s]+)',
            r'email\s+to\s+([^\s]+@[^\s]+)',
            r'to\s+([^\s]+@[^\s]+)'
        ]
        
        for pattern in email_patterns:
            email_match = re.search(pattern, prompt, re.IGNORECASE)
            if email_match:
                entities["to"] = email_match.group(1)
                break
        
        # Extract subject
        subject_patterns = [
            r'about\s+[\'"]([^\'"]+)[\'"]',
            r'subject\s+[\'"]([^\'"]+)[\'"]',
            r'titled\s+[\'"]([^\'"]+)[\'"]'
        ]
        
        for pattern in subject_patterns:
            subject_match = re.search(pattern, prompt, re.IGNORECASE)
            if subject_match:
                entities["subject"] = subject_match.group(1)
                break
        
        # Extract message body
        body_patterns = [
            r'saying\s+[\'"]([^\'"]+)[\'"]',
            r'message\s+[\'"]([^\'"]+)[\'"]',
            r'body\s+[\'"]([^\'"]+)[\'"]',
            r'content\s+[\'"]([^\'"]+)[\'"]'
        ]
        
        for pattern in body_patterns:
            body_match = re.search(pattern, prompt, re.IGNORECASE)
            if body_match:
                entities["body"] = body_match.group(1)
                break
        
        return entities

    def handle_prompt(self, prompt: str) -> CallToolResult:
        """
        Main method to handle user prompts.
        This orchestrates the entire process:
        1. Intent classification
        2. Entity extraction
        3. Action execution
        4. Response generation
        """
        try:
            # Classify the intent
            intent = self.classify_intent(prompt)
            
            # Handle based on intent type
            if intent.type == IntentType.LIST_FOLDERS:
                return self._handle_list_folders(intent)
            elif intent.type == IntentType.LIST_FILES:
                return self._handle_list_files(intent)
            elif intent.type == IntentType.SEARCH_FILES:
                return self._handle_search_files(intent)
            elif intent.type == IntentType.SHOW_IMAGE:
                return self._handle_show_image(intent)
            elif intent.type == IntentType.READ_FILE:
                return self._handle_read_file(intent)
            elif intent.type == IntentType.QUERY_PDF:
                return self._handle_query_pdf(intent)
            elif intent.type == IntentType.SEND_EMAIL:
                return self._handle_send_email(intent)
            elif intent.type == IntentType.GET_WEATHER:
                return self._handle_get_weather(intent)
            
            # Default to chat
            return self._handle_chat(intent)
            
        except Exception as e:
            logger.error(f"Error handling prompt: {str(e)}", exc_info=True)
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Sorry, I encountered an error: {str(e)}",
                    uri=None,
                    mimeType=None
                )],
                isError=True
            )

    def _handle_list_folders(self, intent: Intent) -> CallToolResult:
        """Handle requests to list folders."""
        try:
            from app.services.drive_service import list_resources
            result = list_resources()
            if not result:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text="No folders found in your Drive.",
                        uri=None,
                        mimeType=None
                    )],
                    isError=False
                )
            
            folders = [f for f in result if f.mimeType == "application/vnd.google-apps.folder"]
            if not folders:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text="No folders found in your Drive.",
                        uri=None,
                        mimeType=None
                    )],
                    isError=False
                )
            
            folder_list = "\n".join([f"- {folder.name}" for folder in folders])
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Found folders in your Drive:\n{folder_list}",
                    uri=None,
                    mimeType=None
                )],
                isError=False
            )
        except Exception as e:
            logger.error(f"Error listing folders: {str(e)}")
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error listing folders: {str(e)}",
                    uri=None,
                    mimeType=None
                )],
                isError=True
            )

    def _handle_list_files(self, intent: Intent) -> CallToolResult:
        """Handle requests to list files in a folder."""
        try:
            from app.services.drive_service import list_resources
            folder_name = intent.entities.get("folder_name")
            if not folder_name:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text="Please specify a folder name.",
                        uri=None,
                        mimeType=None
                    )],
                    isError=True
                )
            
            result = list_resources()
            if not result:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"No files found in folder '{folder_name}'.",
                        uri=None,
                        mimeType=None
                    )],
                    isError=False
                )
            
            files = [f for f in result if f.mimeType != "application/vnd.google-apps.folder"]
            if not files:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"No files found in folder '{folder_name}'.",
                        uri=None,
                        mimeType=None
                    )],
                    isError=False
                )
            
            file_list = "\n".join([f"- {file.name}" for file in files])
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Files in folder '{folder_name}':\n{file_list}",
                    uri=None,
                    mimeType=None
                )],
                isError=False
            )
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error listing files: {str(e)}",
                    uri=None,
                    mimeType=None
                )],
                isError=True
            )

    def _handle_search_files(self, intent: Intent) -> CallToolResult:
        """Handle requests to search for files."""
        try:
            from app.services.drive_service import search
            query = intent.entities.get("query")
            if not query:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text="Please specify a search query.",
                        uri=None,
                        mimeType=None
                    )],
                    isError=True
                )
            
            result = search(query=query)
            if not result or result.isError:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"No files found matching '{query}'.",
                        uri=None,
                        mimeType=None
                    )],
                    isError=False
                )
            
            return result
        except Exception as e:
            logger.error(f"Error searching files: {str(e)}")
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error searching files: {str(e)}",
                    uri=None,
                    mimeType=None
                )],
                isError=True
            )

    def _handle_show_image(self, intent: Intent) -> Optional[CallToolResult]:
        """Handle show image command."""
        # Get filename from extracted entities
        filename = intent.entities.get("file_name")
        if not filename:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="Please specify an image filename, e.g., 'display the photo ai.jpeg'",
                        mimeType="text/plain",
                        uri=None
                    )
                ]
            )
            
        logger.info(f"Looking for image: {filename}")
        
        try:
            # Get all resources in Drive (multiple pages if needed)
            all_resources = []
            cursor = None
            
            # Get multiple pages of results
            for _ in range(3):  # Get up to 3 pages (150 files total)
                resources = list_resources(cursor)
                if not resources:
                    break
                all_resources.extend(resources)
                cursor = getattr(resources[-1], 'nextPageToken', None) if resources else None
                if not cursor:
                    break
            
            target_file = None
            
            # Search for the file case-insensitively with multiple strategies
            filename_lower = filename.lower()
            
            # First try exact match
            for resource in all_resources:
                if resource.name.lower() == filename_lower:
                    target_file = resource
                    break
            
            # If no exact match, try partial match
            if not target_file:
                for resource in all_resources:
                    if filename_lower in resource.name.lower() and resource.mimeType.startswith('image/'):
                        target_file = resource
                        break
            
            if not target_file:
                # Return a helpful message with some available image files
                image_files = [r.name for r in all_resources if r.mimeType.startswith('image/')]
                if image_files:
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=f"Could not find image '{filename}' in your Drive. Available images: {', '.join(image_files[:5])}",
                                mimeType="text/plain",
                                uri=None
                            )
                        ]
                    )
                else:
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=f"Could not find image '{filename}' in your Drive. No image files found.",
                                mimeType="text/plain",
                                uri=None
                            )
                        ]
                    )
            
            # Get the file ID from the URI
            file_id = str(target_file.uri).split("/")[-1]
            
            # Read the resource using the file ID
            result = read_resource(f"gdrive:///{file_id}")
            
            if not result:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Could not read image '{filename}' from Drive.",
                            mimeType="text/plain",
                            uri=None
                        )
                    ]
                )
            
            # The result should be a list with one TextContent object containing the base64 image
            if result and len(result) > 0 and result[0].mimeType and result[0].mimeType.startswith('image/'):
                # Return the image data directly
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=result[0].text,  # This is the base64 image data
                            mimeType=result[0].mimeType,
                            uri=result[0].uri
                        )
                    ]
                )
            else:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Error: The file '{filename}' is not an image.",
                            mimeType="text/plain",
                            uri=None
                        )
                    ]
                )
            
        except Exception as e:
            logger.error(f"Error handling show image: {str(e)}")
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Error showing image: {str(e)}",
                        mimeType="text/plain",
                        uri=None
                    )
                ]
            )

    def _handle_read_file(self, intent: Intent) -> CallToolResult:
        """Handle requests to read files."""
        try:
            from app.services.drive_service import read_resource
            file_name = intent.entities.get("file_name")
            if not file_name:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text="Please specify a file name.",
                        uri=None,
                        mimeType=None
                    )],
                    isError=True
                )
            
            result = read_resource(f"gdrive:///{file_name}")
            if not result or result.isError:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Could not find or read file '{file_name}'.",
                        uri=None,
                        mimeType=None
                    )],
                    isError=True
                )
            
            return result
        except Exception as e:
            logger.error(f"Error reading file: {str(e)}")
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error reading file: {str(e)}",
                    uri=None,
                    mimeType=None
                )],
                isError=True
            )

    def _handle_query_pdf(self, intent: Intent) -> CallToolResult:
        """Handle queries about PDF content."""
        try:
            from app.services.drive_service import read_resource
            file_name = intent.entities.get("file_name")
            query = intent.entities.get("query")
            
            if not file_name:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text="Please specify a PDF file name.",
                        uri=None,
                        mimeType=None
                    )],
                    isError=True
                )
            
            result = read_resource(f"gdrive:///{file_name}")
            if not result or result.isError:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Could not find or read PDF '{file_name}'.",
                        uri=None,
                        mimeType=None
                    )],
                    isError=True
                )
            
            # TODO: Implement PDF content querying logic
            return result
        except Exception as e:
            logger.error(f"Error querying PDF: {str(e)}")
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error querying PDF: {str(e)}",
                    uri=None,
                    mimeType=None
                )],
                isError=True
            )

    def _handle_send_email(self, intent: Intent) -> CallToolResult:
        """Handle email sending requests."""
        try:
            from app.services.gmail_service import send_email
            to = intent.entities.get("to")
            subject = intent.entities.get("subject")
            body = intent.entities.get("body")
            
            if not all([to, subject, body]):
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text="Please provide recipient, subject, and message body.",
                        uri=None,
                        mimeType=None
                    )],
                    isError=True
                )
            
            result = send_email(to=[to], subject=subject, body=body)
            if isinstance(result, dict) and result.get("success"):
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text="Email sent successfully!",
                        uri=None,
                        mimeType=None
                    )],
                    isError=False
                )
            else:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Failed to send email: {result.get('message', 'Unknown error')}",
                        uri=None,
                        mimeType=None
                    )],
                    isError=True
                )
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error sending email: {str(e)}",
                    uri=None,
                    mimeType=None
                )],
                isError=True
            )

    def _handle_get_weather(self, intent: Intent) -> CallToolResult:
        """Handle weather information requests."""
        try:
            from app.services.weather_service import get_weather_info
            location = intent.entities.get("location")
            if not location:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text="Please specify a location.",
                        uri=None,
                        mimeType=None
                    )],
                    isError=True
                )
            
            return get_weather_info(location)
        except Exception as e:
            logger.error(f"Error getting weather: {str(e)}")
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error getting weather: {str(e)}",
                    uri=None,
                    mimeType=None
                )],
                isError=True
            )

    def _handle_chat(self, intent: Intent) -> CallToolResult:
        """Handle general chat interactions."""
        try:
            # Return None to indicate that the LLM should handle this
            return None
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error in chat: {str(e)}",
                    uri=None,
                    mimeType=None
                )],
                isError=True
            ) 