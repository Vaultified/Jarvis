from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from ..services.drive_service import search_files, read_file_content
import logging
from ..services.auth_service import get_google_credentials

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

class DriveSearchRequest(BaseModel):
    query: Optional[str] = None
    folder: Optional[str] = None

@router.post("/search")
async def search_drive(request: DriveSearchRequest):
    try:
        # Get credentials
        credentials = get_google_credentials()
        if not credentials:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Build Drive service
        from googleapiclient.discovery import build
        service = build('drive', 'v3', credentials=credentials)
        
        logger.info("\n=== Starting Drive Search ===")
        
        # Prepare the query
        query_parts = []
        
        # If folder is specified, search in that folder
        if request.folder:
            logger.info(f"Searching in folder: {request.folder}")
            # First, find the folder ID
            folder_query = f"name = '{request.folder}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
            folder_results = service.files().list(
                q=folder_query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            folders = folder_results.get('files', [])
            if not folders:
                return {
                    "success": False,
                    "message": f"Folder '{request.folder}' not found"
                }
            
            folder_id = folders[0]['id']
            query_parts.append(f"'{folder_id}' in parents")
        
        # If search query is specified, add it to the query
        if request.query:
            logger.info(f"Searching for: {request.query}")
            query_parts.append(f"fullText contains '{request.query}'")
        
        # Add common query parts
        query_parts.append("trashed = false")
        
        # Combine all query parts
        final_query = " and ".join(query_parts)
        logger.info(f"Final query: {final_query}")
        
        # Execute the search
        results = service.files().list(
            q=final_query,
            spaces='drive',
            fields='files(id, name, mimeType, size, modifiedTime)',
            pageSize=100
        ).execute()
        
        files = results.get('files', [])
        
        if not files:
            return {
                "success": True,
                "message": "No files found matching your search criteria."
            }
        
        # Format the results
        file_list = []
        for file in files:
            file_info = {
                "name": file.get('name'),
                "type": file.get('mimeType', 'Unknown'),
                "size": file.get('size', 'Unknown'),
                "modified": file.get('modifiedTime', 'Unknown')
            }
            file_list.append(file_info)
        
        # Create a summary message
        total_files = len(file_list)
        file_types = {}
        for file in file_list:
            file_type = file['type'].split('.')[-1] if '.' in file['type'] else file['type']
            file_types[file_type] = file_types.get(file_type, 0) + 1
        
        summary = f"Found {total_files} files in {request.folder if request.folder else 'your Drive'}:\n"
        for file_type, count in file_types.items():
            summary += f"- {count} {file_type} files\n"
        
        return {
            "success": True,
            "message": summary,
            "files": file_list
        }
        
    except Exception as e:
        logger.error(f"Error in search_drive: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/read", response_model=FileContentResponse)
async def read_drive_file(request: FileReadRequest):
    """Read the content of a Google Drive file."""
    try:
        file_info = read_file_content(file_id=request.file_id)
        # Ensure the response matches the schema even if content extraction failed
        return FileContentResponse(**file_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file content: {e}") 