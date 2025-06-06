from mcp.server.fastmcp import FastMCP
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict
from .auth_service import get_google_credentials
import time
# Import necessary modules for handling file content
import io
import googleapiclient.http
import PyPDF2 # Import PyPDF2

# Create an MCP server for the Drive Service
mcp = FastMCP("Google Drive Service")

def get_drive_service():
    """Initialize and return Google Drive service with OAuth2 credentials."""
    creds = get_google_credentials()
    if not creds:
        # In a real application, handle this more gracefully (e.g., raise HTTPException)
        print("Authentication required for Google Drive.")
        # Trigger the auth flow if necessary
        get_google_credentials() 
        creds = get_google_credentials() # Try getting creds again after triggering flow
        if not creds:
             raise ValueError("Failed to get valid credentials for Google Drive")
    try:
        service = build('drive', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f"Error building Drive service: {e}")
        raise ValueError(f"Failed to initialize Google Drive service: {e}")

@mcp.tool()
def search_files(query: str) -> List[Dict]:
    """Search for files in Google Drive by name or content.

    Args:
        query: The search query string.

    Returns:
        A list of dictionaries, each representing a matching file.
    """
    try:
        service = get_drive_service()
        # Search using the Drive API query syntax
        # Example: name contains 'query' or fullText contains 'query'
        # For more complex queries, refer to Google Drive API documentation
        results = service.files().list(
            q=f"name contains '{query}' or fullText contains '{query}'",
            pageSize=10, # Limit results
            fields="nextPageToken, files(id, name, mimeType, modifiedTime)"
        ).execute()
        items = results.get('files', [])
        
        if not items:
            print('No files found.')
            return []
        
        file_list = []
        for item in items:
            file_list.append({
                'id': item['id'],
                'name': item['name'],
                'mimeType': item['mimeType'],
                'modifiedTime': item['modifiedTime']
            })
            
        return file_list
    except HttpError as error:
        print(f'An API error occurred: {error}')
        # Handle authentication errors specifically if needed
        if error.resp.status == 401:
             print("Authentication failed. Please re-authenticate.")
             # In a real API context, you'd trigger a re-auth flow to the user
        return []
    except Exception as e:
        print(f'An error occurred: {e}')
        return []

@mcp.tool()
def read_file_content(file_id: str) -> Dict:
    """Read the content of a specific file from Google Drive.

    Args:
        file_id: The ID of the file to read.

    Returns:
        A dictionary containing file information and content.
    """
    try:
        service = get_drive_service()
        
        # Get file metadata first
        file_metadata = service.files().get(fileId=file_id, fields="id, name, mimeType, modifiedTime, size").execute()
        mime_type = file_metadata.get('mimeType')
        file_name = file_metadata.get('name')
        
        content = None
        
        # Basic handling for text-like files
        if mime_type and (mime_type.startswith('text/') or mime_type == 'application/json'):
             request = service.files().get_media(fileId=file_id)
             file_content_io = io.BytesIO()
             downloader = googleapiclient.http.MediaIoBaseDownload(file_content_io, request)
             done = False
             while done is False:
                 status, done = downloader.next_chunk()
             file_content_io.seek(0)
             content = file_content_io.read().decode('utf-8')
             
        # Handling for PDF files
        elif mime_type == 'application/pdf':
            request = service.files().get_media(fileId=file_id)
            file_content_io = io.BytesIO()
            downloader = googleapiclient.http.MediaIoBaseDownload(file_content_io, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            file_content_io.seek(0)
            
            # Use PyPDF2 to read text from the PDF
            try:
                pdf_reader = PyPDF2.PdfReader(file_content_io)
                text = ""
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() or ""
                content = text
            except Exception as pdf_error:
                print(f"Error reading PDF content: {pdf_error}")
                content = f"Error extracting text from PDF: {pdf_error}"

        # For now, we won't read content of other file types to avoid issues

        return {
            'id': file_metadata.get('id'),
            'name': file_name,
            'mimeType': mime_type,
            'modifiedTime': file_metadata.get('modifiedTime'),
            'size': file_metadata.get('size'),
            'content': content
        }

    except HttpError as error:
        print(f'An API error occurred: {error}')
        if error.resp.status == 401:
             print("Authentication failed. Please re-authenticate.")
        elif error.resp.status == 404:
             print(f"File not found with ID: {file_id}")
        return {'error': f'Failed to read file content: {error}'}
    except Exception as e:
        print(f'An error occurred: {e}')
        return {'error': f'Failed to read file content: {e}'}

if __name__ == "__main__":
    # This block allows you to run the MCP server directly for testing
    # You might need to manually trigger authentication before running this
    print("Running Google Drive MCP Server...")
    mcp.run() 