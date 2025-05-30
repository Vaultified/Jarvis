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
        'https://www.googleapis.com/auth/gmail.compose',
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
    
    def __init__(self):
        # Use absolute path for credentials
        self.credentials_path = Path('/Users/sujinsr/Documents/jarvis/backend/credentials.json')
        self.token_path = Path('/Users/sujinsr/Documents/jarvis/backend/token.json')
        self.credentials: Optional[Credentials] = None
        self._load_credentials()
    
    def _load_credentials(self) -> None:
        """Load credentials from token file if it exists."""
        try:
            if self.token_path.exists():
                with open(self.token_path, 'r') as token:
                    token_data = json.load(token)
                    # Check if we have the required fields
                    if 'refresh_token' in token_data:
                        self.credentials = Credentials.from_authorized_user_info(
                            token_data, self.SCOPES
                        )
                    else:
                        print("Existing token file is missing refresh_token, will need to re-authenticate")
                        # Optionally remove the invalid token file
                        self.token_path.unlink()
        except Exception as e:
            print(f"Error loading credentials: {str(e)}")
            # If there's any error, we'll start fresh
            self.credentials = None
    
    def _save_credentials(self) -> None:
        """Save credentials to token file."""
        if self.credentials:
            with open(self.token_path, 'w') as token:
                token.write(self.credentials.to_json())
    
    def get_auth_url(self) -> str:
        """Get the authorization URL for Google OAuth2."""
        if not self.credentials_path.exists():
            raise FileNotFoundError(f"Credentials file not found at {self.credentials_path}")
            
        flow = InstalledAppFlow.from_client_secrets_file(
            str(self.credentials_path),
            self.SCOPES,
            redirect_uri="http://localhost:8000/api/auth/callback"
        )
        auth_url, _ = flow.authorization_url(
            access_type='offline',  # Force offline access to get refresh token
            prompt='consent',       # Force consent screen to ensure refresh token
            include_granted_scopes='true'
        )
        return auth_url
    
    def handle_callback(self, code: str) -> Dict:
        """Handle the OAuth2 callback and exchange code for tokens."""
        flow = InstalledAppFlow.from_client_secrets_file(
            str(self.credentials_path),
            self.SCOPES,
            redirect_uri="http://localhost:8000/api/auth/callback"
        )
        flow.fetch_token(code=code)
        self.credentials = flow.credentials
        
        # Verify we got a refresh token
        if not self.credentials.refresh_token:
            raise ValueError("No refresh token received. Please try the authorization flow again.")
            
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
            self.credentials.refresh(GoogleRequest())
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

def find_credentials_file():
    """Find credentials.json in either services directory or backend root."""
    # Use absolute path for backend credentials
    backend_path = '/Users/sujinsr/Documents/jarvis/backend/credentials.json'
    if os.path.exists(backend_path):
        return backend_path
    
    # Check services directory as fallback
    services_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
    if os.path.exists(services_path):
        return services_path
    
    raise FileNotFoundError(f"credentials.json not found in {backend_path} or {services_path}")

def get_google_credentials():
    """Get Google OAuth2 credentials, refreshing if necessary."""
    creds = None
    token_path = os.path.join(os.path.dirname(__file__), '..', '..', 'token.json')
    credentials_path = find_credentials_file()
    
    # Load credentials file
    print("\n=== OAuth Configuration ===")
    print("Loading credentials file...")
    try:
        with open(credentials_path, 'r') as f:
            content = f.read()
            creds_data = json.loads(content)
            if not creds_data:
                raise ValueError("Empty credentials.json file")
            
            # Get web credentials
            web_creds = creds_data.get('web')
            if not web_creds:
                raise ValueError("Missing 'web' section in credentials.json")
            
            print("\nCredentials file contents:")
            print("\nRedirect URIs:")
            for uri in web_creds.get('redirect_uris', []):
                print(f"  - {uri}")
            
            if not web_creds.get('client_id'):
                raise ValueError("Missing client_id in credentials.json")
            
            if not web_creds.get('redirect_uris'):
                raise ValueError("Missing redirect_uris in credentials.json")
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {str(e)}")
        raise ValueError("Invalid JSON in credentials.json")
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        raise ValueError(f"Error loading credentials.json: {str(e)}")

    # Check if we have a valid token
    if os.path.exists(token_path):
        try:
            with open(token_path, 'r') as token:
                creds = Credentials.from_authorized_user_info(json.load(token), AuthService.SCOPES)
        except Exception as e:
            print(f"Error loading token: {str(e)}")
            creds = None

    # If no valid credentials, start OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(GoogleRequest())
            except Exception as e:
                print(f"Error refreshing token: {str(e)}")
                creds = None

        if not creds:
            print("\nInitializing OAuth flow...")
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, 
                AuthService.SCOPES
            )
            
            # Get the redirect URI from credentials
            redirect_uri = web_creds['redirect_uris'][0]
            print(f"\nUsing redirect URI: {redirect_uri}")
            
            # Extract port from redirect URI
            try:
                port = int(redirect_uri.split(':')[-1])
                print(f"Using port: {port}")
            except (IndexError, ValueError):
                raise ValueError(f"Invalid redirect URI format: {redirect_uri}")
            
            print("\nStarting local server for OAuth...")
            try:
                creds = flow.run_local_server(
                    port=port,
                    success_message='Authentication successful! You can close this window.',
                    open_browser=True
                )
                print("New token obtained")
                
                # Save the credentials as JSON
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
                    print("Token saved to file")
            except Exception as e:
                raise ValueError(f"OAuth flow failed: {str(e)}")

    return creds 