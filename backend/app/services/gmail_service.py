from mcp.server.fastmcp import FastMCP
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request as GoogleRequest
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import json
import base64
from email.mime.text import MIMEText
from typing import List
import tempfile

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose'
]

# Create an MCP server
mcp = FastMCP("Gmail Service")

def find_credentials_file():
    """Find credentials.json in either services directory or backend root."""
    # Use absolute path for backend credentials
    backend_path = '/Users/sujinsr/Documents/jarvis/backend/credentials.json'
    if os.path.exists(backend_path):
        print(f"Found credentials in backend: {backend_path}")
        return backend_path
    
    # Check services directory as fallback
    services_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
    if os.path.exists(services_path):
        print(f"Found credentials in services directory: {services_path}")
        return services_path
    
    raise FileNotFoundError(f"credentials.json not found in {backend_path} or {services_path}")

def get_gmail_service():
    """Initialize and return Gmail service with OAuth2 credentials."""
    creds = None
    token_path = os.path.join(os.path.dirname(__file__), '..', '..', 'token.json')
    credentials_path = find_credentials_file()
    
    print(f"Using token path: {token_path}")
    print(f"Using credentials path: {credentials_path}")
    
    # Load credentials file
    print("\n=== OAuth Configuration ===")
    print("Loading credentials file...")
    try:
        with open(credentials_path, 'r') as f:
            content = f.read()
            print(f"Raw file content: {content}")
            creds_data = json.loads(content)
            if not creds_data:
                raise ValueError("Empty credentials.json file")
            
            # Get web credentials
            web_creds = creds_data.get('web')
            if not web_creds:
                raise ValueError("Missing 'web' section in credentials.json")
            
            print("\nCredentials file contents:")
            print(f"Client ID: {web_creds.get('client_id')}")
            print(f"Project ID: {web_creds.get('project_id')}")
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
    
    print("\nInitializing OAuth flow...")
    flow = InstalledAppFlow.from_client_secrets_file(
        credentials_path, 
        SCOPES
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

    return build('gmail', 'v1', credentials=creds, cache_discovery=False)

@mcp.tool()
def send_email(to: List[str], subject: str, body: str, mime_type: str = "text/plain") -> dict:
    """Send an email using Gmail API."""
    try:
        print("Initializing Gmail service...")
        service = get_gmail_service()
        
        # Create a simple message
        message = MIMEText(body, mime_type)
        message['to'] = ", ".join(to)
        message['subject'] = subject
        print(f"Preparing email to: {to}")

        # Encode the message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        print("Message encoded successfully")

        # Send the message
        try:
            print("Sending email...")
            # Add retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # First verify the service is working
                    profile = service.users().getProfile(userId='me').execute()
                    print(f"Connected as: {profile.get('emailAddress')}")
                    
                    sent_message = service.users().messages().send(
                        userId='me',
                        body={'raw': raw_message}
                    ).execute()
                    print(f"Email sent successfully. Message ID: {sent_message.get('id')}")
                    
                    return {
                        "success": True,
                        "message": "Email sent successfully",
                        "details": {
                            "to": to,
                            "subject": subject,
                            "mimeType": mime_type,
                            "messageId": sent_message.get('id')
                        }
                    }
                except HttpError as error:
                    print(f"Attempt {attempt + 1} failed with error: {error}")
                    if attempt < max_retries - 1:
                        print(f"Retrying... (Attempt {attempt + 2} of {max_retries})")
                        continue
                    raise error

        except HttpError as error:
            print(f"HTTP Error occurred: {error}")
            error_details = error.error_details if hasattr(error, 'error_details') else str(error)
            print(f"Error details: {error_details}")
            return {
                "success": False,
                "message": f"Failed to send email: {error_details}",
                "details": {
                    "to": to,
                    "subject": subject,
                    "mimeType": mime_type,
                    "error": str(error)
                }
            }
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to send email: {str(e)}",
            "details": {
                "to": to,
                "subject": subject,
                "mimeType": mime_type
            }
        }

if __name__ == "__main__":
    mcp.run() 