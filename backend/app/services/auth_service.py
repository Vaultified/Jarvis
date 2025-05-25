import os
import json
from pathlib import Path
from typing import Dict, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

class AuthService:
    """Service to handle Google OAuth2 authentication."""
    
    SCOPES = [
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.readonly'
    ]
    
    def __init__(self):
        self.credentials_path = Path('credentials.json')
        self.token_path = Path('token.json')
        self.credentials: Optional[Credentials] = None
        self._load_credentials()
    
    def _load_credentials(self) -> None:
        """Load credentials from token file if it exists."""
        if self.token_path.exists():
            with open(self.token_path, 'r') as token:
                self.credentials = Credentials.from_authorized_user_info(
                    json.load(token), self.SCOPES
                )
    
    def _save_credentials(self) -> None:
        """Save credentials to token file."""
        if self.credentials:
            with open(self.token_path, 'w') as token:
                token.write(self.credentials.to_json())
    
    def get_auth_url(self) -> str:
        """Get the authorization URL for Google OAuth2."""
        flow = InstalledAppFlow.from_client_secrets_file(
            self.credentials_path,
            self.SCOPES,
            redirect_uri="http://localhost:8000/api/auth/callback"
        )
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        return auth_url
    
    def handle_callback(self, code: str) -> Dict:
        """Handle the OAuth2 callback and exchange code for tokens."""
        flow = InstalledAppFlow.from_client_secrets_file(
            self.credentials_path,
            self.SCOPES,
            redirect_uri="http://localhost:8000/api/auth/callback"
        )
        flow.fetch_token(code=code)
        self.credentials = flow.credentials
        self._save_credentials()
        
        return {
            "access_token": self.credentials.token,
            "refresh_token": self.credentials.refresh_token,
            "token_uri": self.credentials.token_uri,
            "client_id": self.credentials.client_id,
            "client_secret": self.credentials.client_secret,
            "scopes": self.credentials.scopes
        }
    
    def get_credentials(self) -> Optional[Credentials]:
        """Get the current credentials, refreshing if necessary."""
        if not self.credentials:
            return None
        
        if self.credentials.expired and self.credentials.refresh_token:
            self.credentials.refresh(Request())
            self._save_credentials()
        
        return self.credentials
    
    def is_authenticated(self) -> bool:
        """Check if the user is authenticated."""
        return self.credentials is not None and not self.credentials.expired
    
    def get_drive_service(self):
        """Get an authenticated Google Drive service."""
        if not self.is_authenticated():
            raise ValueError("Not authenticated")
        return build('drive', 'v3', credentials=self.credentials)
    
    def get_gmail_service(self):
        """Get an authenticated Gmail service."""
        if not self.is_authenticated():
            raise ValueError("Not authenticated")
        return build('gmail', 'v1', credentials=self.credentials) 