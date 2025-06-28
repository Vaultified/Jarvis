from mcp.server.fastmcp import FastMCP
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from .auth_service import AuthService
import time
import os

# Create an MCP server
mcp = FastMCP("Gmail Service")

def get_gmail_service():
    """Initialize and return Gmail service with OAuth2 credentials."""
    # Get the path to the credentials file
    credentials_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "credentials.json")
    token_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "token.json")
    
    # Initialize auth service
    auth_service = AuthService(credentials_path=credentials_path, token_path=token_path)
    
    # Get Gmail service
    return auth_service.get_gmail_service()

@mcp.tool()
def send_email(to: List[str], subject: str, body: str, mime_type: str = "text/plain") -> dict:
    """Send an email using Gmail API."""
    try:
        print("\n=== Starting Email Send Process ===")
        service = get_gmail_service()
        
        # Create message
        message = MIMEText(body)
        message['to'] = ", ".join(to)
        message['subject'] = subject
        
        # Get the authenticated user's email
        profile = service.users().getProfile(userId='me').execute()
        user_email = profile.get('emailAddress')
        message['from'] = user_email
        
        print(f"\nEmail Details:")
        print(f"From: {user_email}")
        print(f"To: {to}")
        print(f"Subject: {subject}")

        # Encode the message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Send the message with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    time.sleep(2)  # Wait before retry
                
                sent_message = service.users().messages().send(
                    userId='me',
                    body={'raw': raw_message}
                ).execute()
                
                return {
                    "success": True,
                    "message": "Email sent successfully",
                    "details": {
                        "to": to,
                        "subject": subject,
                        "messageId": sent_message.get('id')
                    }
                }
            except HttpError as error:
                if attempt == max_retries - 1:
                    raise error
                print(f"Attempt {attempt + 1} failed, retrying...")
                continue

    except Exception as e:
        print(f"\nError sending email: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to send email: {str(e)}",
            "details": {
                "to": to,
                "subject": subject,
                "error": str(e)
            }
        }

if __name__ == "__main__":
    mcp.run() 