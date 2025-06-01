from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from ..services.drive_service import search_files, read_file_content

router = APIRouter()

# Pydantic models for request/response data
class FileSearchRequest(BaseModel):
    query: str

class FileInfo(BaseModel):
    id: str
    name: str
    mimeType: str
    modifiedTime: str
    size: Optional[str] = None # Size might not be available for all items

class FileSearchResponse(BaseModel):
    files: List[FileInfo]
    message: str

class FileReadRequest(BaseModel):
    file_id: str

class FileContentResponse(BaseModel):
    id: str
    name: str
    mimeType: str
    modifiedTime: str
    size: Optional[str] = None
    content: Optional[str] = None
    error: Optional[str] = None

@router.post("/search", response_model=FileSearchResponse)
async def search_drive_files(request: FileSearchRequest):
    """Search for files in Google Drive."""
    try:
        files_list = search_files(query=request.query)
        return FileSearchResponse(files=files_list, message="Search completed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search files: {e}")

@router.post("/read", response_model=FileContentResponse)
async def read_drive_file(request: FileReadRequest):
    """Read the content of a Google Drive file."""
    try:
        file_info = read_file_content(file_id=request.file_id)
        # Ensure the response matches the schema even if content extraction failed
        return FileContentResponse(**file_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file content: {e}") 