from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any

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