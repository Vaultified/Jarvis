from fastapi import APIRouter, HTTPException, Request
from ..services.auth_service import AuthService
import logging
import os

router = APIRouter()
logger = logging.getLogger(__name__)

# Get the path to the credentials file
credentials_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "credentials.json")
token_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "token.json")

# Initialize the auth service
auth_service = AuthService(credentials_path=credentials_path, token_path=token_path)

@router.get("/auth/start")
async def start_auth():
    """Start the OAuth2 flow."""
    try:
        auth_url = auth_service.get_authorization_url()
        return {"auth_url": auth_url}
    except Exception as e:
        logger.error(f"Error starting auth: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/auth/callback")
async def auth_callback(code: str, state: str = None):
    """Handle the OAuth2 callback."""
    try:
        success = auth_service.handle_callback(code)
        if success:
            return {"status": "success", "message": "Authentication successful"}
        else:
            raise HTTPException(status_code=400, detail="Authentication failed")
    except Exception as e:
        logger.error(f"Error in auth callback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/auth/status")
async def auth_status():
    """Check the authentication status."""
    try:
        is_authenticated = auth_service.is_authenticated()
        return {"authenticated": is_authenticated}
    except Exception as e:
        logger.error(f"Error checking auth status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/auth/test-services")
async def test_google_services():
    """Test access to Google services."""
    try:
        results = {}
        
        # Test Gmail access
        try:
            gmail_service = auth_service.get_gmail_service()
            # Get the first 5 email threads
            threads = gmail_service.users().threads().list(userId='me', maxResults=5).execute()
            results['gmail'] = {
                'status': 'success',
                'threads_count': len(threads.get('threads', [])),
                'message': 'Successfully accessed Gmail'
            }
        except Exception as e:
            results['gmail'] = {
                'status': 'error',
                'message': f'Gmail access error: {str(e)}'
            }

        # Test Drive access
        try:
            # Check if get_drive_service exists before calling
            if hasattr(auth_service, 'get_drive_service'):
                drive_service = auth_service.get_drive_service()
                # List the first 5 files
                files = drive_service.files().list(pageSize=5).execute()
                results['drive'] = {
                    'status': 'success',
                    'files_count': len(files.get('files', [])),
                    'message': 'Successfully accessed Google Drive'
                }
            else:
                 results['drive'] = {
                    'status': 'skipped',
                    'message': 'Drive service not implemented'
                }
        except Exception as e:
            results['drive'] = {
                'status': 'error',
                'message': f'Drive access error: {str(e)}'
            }

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 