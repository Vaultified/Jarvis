from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Optional, List
from ..services.auth_service import AuthService

router = APIRouter()
auth_service = AuthService()

class AuthResponse(BaseModel):
    auth_url: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_uri: str
    client_id: str
    client_secret: str
    scopes: list

@router.get("/auth/start", response_model=AuthResponse)
async def start_auth():
    """Start the Google OAuth2 authentication flow."""
    try:
        auth_url = auth_service.get_auth_url()
        return AuthResponse(auth_url=auth_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/auth/callback")
async def auth_callback(code: str):
    """Handle the OAuth2 callback from Google."""
    try:
        token_info = auth_service.handle_callback(code)
        return TokenResponse(**token_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/auth/status")
async def auth_status():
    """Check the current authentication status."""
    return {
        "authenticated": auth_service.is_authenticated()
    }

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
            drive_service = auth_service.get_drive_service()
            # List the first 5 files
            files = drive_service.files().list(pageSize=5).execute()
            results['drive'] = {
                'status': 'success',
                'files_count': len(files.get('files', [])),
                'message': 'Successfully accessed Google Drive'
            }
        except Exception as e:
            results['drive'] = {
                'status': 'error',
                'message': f'Drive access error: {str(e)}'
            }

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 