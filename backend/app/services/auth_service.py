import os
import json
from pathlib import Path
from typing import Dict, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request as GoogleRequest
from googleapiclient.discovery import build

class AuthService:
    """Service to handle Google OAuth2 authentication."""
    
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/gmail.compose',
        'https://www.googleapis.com/auth/drive.file'
    ]
    
    def __init__(self):
        # Get the backend directory path
        backend_dir = Path(__file__).parent.parent.parent
        self.credentials_path = backend_dir / 'credentials.json'
        self.token_path = backend_dir / 'token.json'
        self.credentials: Optional[Credentials] = None
        self._load_credentials()
    
    def _load_credentials(self) -> None:
        """Load credentials from token file if it exists."""
        try:
            if self.token_path.exists():
                with open(self.token_path, 'r') as token:
                    token_data = json.load(token)
                    # Create credentials from the token data
                    self.credentials = Credentials(
                        token=token_data.get('token'),
                        refresh_token=token_data.get('refresh_token'),
                        token_uri=token_data.get('token_uri'),
                        client_id=token_data.get('client_id'),
                        client_secret=token_data.get('client_secret'),
                        scopes=token_data.get('scopes', self.SCOPES)
                    )
                    
                    # Check if credentials need refresh
                    if self.credentials.expired and self.credentials.refresh_token:
                        try:
                            self.credentials.refresh(GoogleRequest())
                            self._save_credentials()
                        except Exception as e:
                            print(f"Token refresh failed: {str(e)}")
                            self._start_new_oauth_flow()
        except Exception as e:
            print(f"Error loading credentials: {str(e)}")
            self._start_new_oauth_flow()
    
    def _start_new_oauth_flow(self) -> None:
        """Start a new OAuth flow to get fresh credentials."""
        try:
            # Remove old token file if it exists
            if self.token_path.exists():
                self.token_path.unlink()
            
            # Set the redirect URI to match Google Console exactly
            redirect_uri = 'http://localhost:8000/api/auth/callback'
            
            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.credentials_path),
                self.SCOPES,
                redirect_uri=redirect_uri
            )
            
            # Get the authorization URL - the callback will be handled by the backend's API endpoint
            auth_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true'
            )
            
            print(f"\n==========================================================")
            print(f"Please visit this URL in your browser to authorize the application:")
            print(auth_url)
            print(f"\nAfter authorization, your browser will be redirected to {redirect_uri}")
            print(f"The backend must be running on port 8000 to handle this redirect and complete the authentication.")
            print(f"==========================================================")
            
            # The code will be handled by the /api/auth/callback endpoint
            
        except Exception as e:
            print(f"\n=== OAuth Flow Error ===")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            self.credentials = None
            
    def exchange_code_for_token(self, code: str) -> None:
        """Exchanges authorization code for credentials and saves them."""
        try:
            redirect_uri = 'http://localhost:8000/api/auth/callback'
            
            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.credentials_path),
                self.SCOPES,
                redirect_uri=redirect_uri
            )
            
            # Fetch the token using the provided code
            flow.fetch_token(code=code)
            self.credentials = flow.credentials
            
            # Save the new credentials
            self._save_credentials()
            
        except Exception as e:
            print(f"\n=== Token Exchange Error ===")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            raise e # Re-raise the exception after logging
    
    def _save_credentials(self) -> None:
        """Save credentials to token file."""
        if self.credentials:
            token_data = {
                'token': self.credentials.token,
                'refresh_token': self.credentials.refresh_token,
                'token_uri': self.credentials.token_uri,
                'client_id': self.credentials.client_id,
                'client_secret': self.credentials.client_secret,
                'scopes': self.credentials.scopes
            }
            with open(self.token_path, 'w') as token:
                json.dump(token_data, token, indent=2)
    
    def get_credentials(self) -> Optional[Credentials]:
        """Get the current credentials, refreshing if necessary."""
        if not self.credentials:
            self._start_new_oauth_flow()
            return self.credentials
        
        if self.credentials.expired and self.credentials.refresh_token:
            try:
                self.credentials.refresh(GoogleRequest())
                self._save_credentials()
            except Exception as e:
                print(f"Token refresh failed: {str(e)}")
                self._start_new_oauth_flow()
        
        return self.credentials
    
    def is_authenticated(self) -> bool:
        """Check if the user is authenticated."""
        return self.credentials is not None and not self.credentials.expired
    
    def get_gmail_service(self):
        """Get an authenticated Gmail service."""
        if not self.is_authenticated():
            raise ValueError("Not authenticated")
        return build('gmail', 'v1', credentials=self.credentials)

def get_google_credentials():
    """Get Google OAuth2 credentials, refreshing if necessary."""
    auth_service = AuthService()
    return auth_service.get_credentials() 