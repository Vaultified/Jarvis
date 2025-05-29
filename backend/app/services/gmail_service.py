from mcp.server.fastmcp import FastMCP
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from .auth_service import get_google_credentials
import time
import json

# Create an MCP server
mcp = FastMCP("Gmail Service")

def get_gmail_service():
    """Initialize and return Gmail service with OAuth2 credentials."""
    creds = get_google_credentials()
    print("\n=== Gmail Service Initialization ===")
    print("Credentials valid:", creds.valid)
    print("Credentials expired:", creds.expired)
    print("Has refresh token:", bool(creds.refresh_token))
    print("Scopes:", creds.scopes)
    return build('gmail', 'v1', credentials=creds, cache_discovery=False)

@mcp.tool()
def send_email(to: List[str], subject: str, body: str, mime_type: str = "text/plain") -> dict:
    """Send an email using Gmail API."""
    try:
        print("\n=== Starting Email Send Process ===")
        print("Initializing Gmail service...")
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
        print("\nMessage encoded successfully")

        # Send the message
        try:
            print("\nAttempting to send email...")
            # Add retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Add a small delay between retries
                    if attempt > 0:
                        print(f"Waiting 2 seconds before retry {attempt + 1}...")
                        time.sleep(2)
                    
                    print(f"\nSending attempt {attempt + 1}...")
                    sent_message = service.users().messages().send(
                        userId='me',
                        body={'raw': raw_message}
                    ).execute()
                    
                    print(f"Email sent successfully!")
                    print(f"Message ID: {sent_message.get('id')}")
                    
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
                    print(f"\nAttempt {attempt + 1} failed with error:")
                    print(f"Error details: {error.error_details if hasattr(error, 'error_details') else str(error)}")
                    
                    if attempt < max_retries - 1:
                        print(f"\nRetrying... (Attempt {attempt + 2} of {max_retries})")
                        continue
                    raise error

        except HttpError as error:
            print("\n=== Final Error Details ===")
            print(f"HTTP Error: {error}")
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
        print("\n=== Unexpected Error ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to send email: {str(e)}",
            "details": {
                "to": to,
                "subject": subject,
                "mimeType": mime_type,
                "error": str(e)
            }
        }

if __name__ == "__main__":
    mcp.run() 