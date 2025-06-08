from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
from ..services.drive_service import search_files, read_file_content
import logging
from ..services.auth_service import get_google_credentials
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import time

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
    size: Optional[str] = None

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

class DriveSearchResponse(BaseModel):
    files: List[dict]
    error: Optional[str] = None

@router.get("/root-folders")
async def list_root_folders(credentials: Credentials = Depends(get_google_credentials)):
    """List all folders in the root directory of Google Drive."""
    try:
        logger.info("Getting Google credentials...")
        if not credentials:
            raise HTTPException(status_code=401, detail="Not authenticated")
            
        logger.info("Building Drive service...")
        service = build('drive', 'v3', credentials=credentials)
        
        # List all folders in root with minimal fields
        query = "mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        logger.info(f"Listing root folders with query: {query}")
        
        try:
            logger.info("Executing Drive API request...")
            # Execute the folder query with minimal fields and smaller page size
            results = service.files().list(
                q=query,
                pageSize=50,  # Reduced page size
                fields="files(id, name)",  # Only get essential fields
                spaces='drive',
                orderBy="name"
            ).execute()
            
            folders = results.get('files', [])
            logger.info(f"Found {len(folders)} folders in root")
            
            # Create a simplified response
            response = {
                "folders": [
                    {
                        "id": folder['id'],
                        "name": folder['name']
                    } for folder in folders
                ]
            }
            
            return response
            
        except HttpError as error:
            logger.error(f"Drive API error: {str(error)}")
            if error.resp.status == 401:
                raise HTTPException(status_code=401, detail="Authentication expired. Please re-authenticate.")
            raise HTTPException(status_code=500, detail=f"Drive API error: {str(error)}")
            
    except Exception as e:
        logger.error(f"Error listing root folders: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=DriveSearchResponse)
async def search_drive(
    request: DriveSearchRequest,
    credentials: Credentials = Depends(get_google_credentials)
):
    """Search for files in Google Drive."""
    try:
        logger.info("Getting Google credentials...")
        service = build('drive', 'v3', credentials=credentials)
        
        # Build the search query
        query_parts = ["trashed = false"]
        
        if request.folder:
            logger.info(f"Searching in folder: {request.folder}")
            # First, find the folder ID
            folder_query = f"mimeType = 'application/vnd.google-apps.folder' and name = '{request.folder}' and trashed = false"
            logger.info(f"Initial folder query: {folder_query}")
            
            folder_results = service.files().list(
                q=folder_query,
                pageSize=1,
                fields="nextPageToken, files(id, name)"
            ).execute()
            
            folders = folder_results.get('files', [])
            logger.info(f"Found {len(folders)} folders")
            
            if not folders:
                logger.warning(f"Folder '{request.folder}' not found")
                return DriveSearchResponse(files=[], error=f"Folder '{request.folder}' not found")
            
            folder_id = folders[0]['id']
            logger.info(f"Found folder ID: {folder_id}")
            query_parts.append(f"'{folder_id}' in parents")
        
        if request.query:
            query_parts.append(f"name contains '{request.query}'")
        
        final_query = " and ".join(query_parts)
        logger.info(f"Final search query: {final_query}")
        
        # Execute the search
        results = service.files().list(
            q=final_query,
            pageSize=100,
            fields="nextPageToken, files(id, name, mimeType, size, modifiedTime)"
        ).execute()
        
        files = results.get('files', [])
        logger.info(f"Found {len(files)} files")
        
        return DriveSearchResponse(files=files)
        
    except Exception as e:
        logger.error(f"Error searching Drive: {str(e)}")
        return DriveSearchResponse(files=[], error=str(e))

@router.post("/read", response_model=FileContentResponse)
async def read_drive_file(request: FileReadRequest):
    """Read the content of a Google Drive file."""
    try:
        file_info = read_file_content(file_id=request.file_id)
        # Ensure the response matches the schema even if content extraction failed
        return FileContentResponse(**file_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file content: {e}") 