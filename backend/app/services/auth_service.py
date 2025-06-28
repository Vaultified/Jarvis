import os
import json
from pathlib import Path
from typing import Dict, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request as GoogleRequest
from googleapiclient.discovery import build
import logging
from fastapi import HTTPException

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthService:
    """Service for handling Google OAuth2 authentication."""
    
    # Define the scopes needed for Gmail and Drive access
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.compose',
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/gmail.send'
    ]
    
    def __init__(self, credentials_path: str, token_path: str):
        """Initialize the auth service with paths to credentials and token files."""
        self.credentials_path = credentials_path
        self.token_path = token_path

    def get_credentials(self):
        """Get Google credentials from token file."""
        try:
            if not os.path.exists(self.token_path):
                logger.error(f"Token file not found at {self.token_path}")
                return None

            with open(self.token_path, 'r') as token:
                creds_dict = json.load(token)
                logger.info(f"Loaded credentials with scopes: {creds_dict.get('scopes', [])}")
                
            # Create credentials from the token data
            credentials = Credentials.from_authorized_user_info(creds_dict)
            
            # Check if credentials exist and have a token
            if not credentials:
                logger.error("Failed to create credentials from token data")
                return None
                
            if not credentials.token:
                logger.error("No access token found in credentials")
                return None
                
            # Don't check credentials.valid as it might be false even with a valid token
            # Just ensure we have the token and scopes
            if not credentials.scopes:
                logger.error("No scopes found in credentials")
                return None
                
            logger.info("Successfully loaded valid credentials")
            return credentials
            
        except Exception as e:
            logger.error(f"Error loading credentials: {str(e)}")
            return None

    def get_authorization_url(self) -> str:
        """Get the authorization URL for Google OAuth2."""
        try:
            if not os.path.exists(self.credentials_path):
                raise FileNotFoundError(f"Credentials file not found at {self.credentials_path}")

            # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_path,
                scopes=self.SCOPES
            )

            # Set the redirect URI to match the Google Console configuration
            flow.redirect_uri = "http://localhost:8000/api/auth/callback"

            # Generate URL for request to Google's OAuth 2.0 server
            auth_url, _ = flow.authorization_url(
                access_type='offline',  # Request offline access to get refresh token
                include_granted_scopes='true',
                prompt='consent'  # Force consent screen to ensure we get refresh token
            )
            
            return auth_url
        except Exception as e:
            logger.error(f"Error getting authorization URL: {str(e)}")
            raise

    def handle_callback(self, code: str) -> bool:
        """Handle the OAuth2 callback from Google."""
        try:
            if not os.path.exists(self.credentials_path):
                raise FileNotFoundError(f"Credentials file not found at {self.credentials_path}")

            # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_path,
                scopes=self.SCOPES
            )

            # Set the redirect URI to match the Google Console configuration
            flow.redirect_uri = "http://localhost:8000/api/auth/callback"

            # Exchange authorization code for credentials
            flow.fetch_token(code=code)

            # Get the credentials from the flow
            credentials = flow.credentials

            # Save the credentials
            self._save_credentials(credentials)

            return True
        except Exception as e:
            logger.error(f"Error in auth callback: {str(e)}")
            raise

    def _save_credentials(self, credentials):
        """Save credentials to token file."""
        try:
            # Create a dictionary with all required fields
            creds_dict = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes,
                'universe_domain': 'googleapis.com'
            }

            # Ensure the directory exists
            os.makedirs(os.path.dirname(self.token_path), exist_ok=True)

            # Save to token file
            with open(self.token_path, 'w') as token:
                json.dump(creds_dict, token)
            logger.info(f"Credentials saved to {self.token_path}")
        except Exception as e:
            logger.error(f"Error saving credentials: {str(e)}")
            raise

    def is_authenticated(self) -> bool:
        """Check if we have valid credentials."""
        return os.path.exists(self.token_path)

    def get_gmail_service(self):
        """Get an authenticated Gmail service."""
        try:
            credentials = self.get_credentials()
            if not credentials:
                raise ValueError("Not authenticated")
            
            # Try to refresh credentials if they're expired
            if credentials.expired and credentials.refresh_token:
                try:
                    credentials.refresh(GoogleRequest())
                    self._save_credentials(credentials)
                    logger.info("Credentials refreshed successfully")
                except Exception as e:
                    logger.error(f"Failed to refresh credentials: {str(e)}")
                    raise ValueError("Authentication expired. Please re-authenticate.")
            
            return build('gmail', 'v1', credentials=credentials)
        except Exception as e:
            logger.error(f"Error getting Gmail service: {str(e)}")
            raise

    def get_drive_service(self):
        """Get a Google Drive service instance."""
        try:
            credentials = self.get_credentials()
            if not credentials:
                raise ValueError("Not authenticated")
            
            # Try to refresh credentials if they're expired
            if credentials.expired and credentials.refresh_token:
                try:
                    credentials.refresh(GoogleRequest())
                    self._save_credentials(credentials)
                    logger.info("Credentials refreshed successfully")
                except Exception as e:
                    logger.error(f"Failed to refresh credentials: {str(e)}")
                    raise ValueError("Authentication expired. Please re-authenticate.")
            
            # Disable cache to avoid the warning
            import googleapiclient.discovery_cache
            googleapiclient.discovery_cache.DISCOVERY_CACHE = {}
            
            return build('drive', 'v3', credentials=credentials)
        except Exception as e:
            logger.error(f"Error getting Drive service: {str(e)}")
            raise

def get_google_credentials():
    """Get Google credentials for API access."""
    try:
        # Get the path to the credentials file
        credentials_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "credentials.json")
        token_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "token.json")
        
        # Initialize auth service
        auth_service = AuthService(credentials_path=credentials_path, token_path=token_path)
        
        # Get credentials
        credentials = auth_service.get_credentials()
        if not credentials:
            logger.error("No valid credentials found")
            return None
            
        return credentials
    except Exception as e:
        logger.error(f"Error getting Google credentials: {str(e)}")
        return None 