from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from ..services.auth_service import get_google_credentials

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class EmailRequest(BaseModel):
    to: List[str]
    subject: str
    body: str

@router.post("/send")
async def send_email(request: EmailRequest):
    try:
        # Get credentials
        credentials = get_google_credentials()
        if not credentials:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Build Gmail service
        from googleapiclient.discovery import build
        service = build('gmail', 'v1', credentials=credentials)
        
        # Get user's email address
        profile = service.users().getProfile(userId='me').execute()
        sender_email = profile.get('emailAddress')
        
        logger.info("\n=== Starting Email Send Process ===")
        
        # Create message
        message = MIMEMultipart()
        message['to'] = ', '.join(request.to)
        message['from'] = sender_email
        message['subject'] = request.subject
        
        # Add body
        msg = MIMEText(request.body)
        message.attach(msg)
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Log email details
        logger.info(f"\nEmail Details:")
        logger.info(f"From: {sender_email}")
        logger.info(f"To: {request.to}")
        logger.info(f"Subject: {request.subject}")
        
        # Send message
        try:
            sent_message = service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            logger.info(f"Message sent successfully! Message ID: {sent_message['id']}")
            return {"success": True, "message": "Email sent successfully", "message_id": sent_message['id']}
            
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error in send_email: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def check_email_status():
    try:
        # Get credentials
        credentials = get_google_credentials()
        if not credentials:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Build Gmail service
        from googleapiclient.discovery import build
        service = build('gmail', 'v1', credentials=credentials)
        
        # Get user's email address
        profile = service.users().getProfile(userId='me').execute()
        
        return {
            "status": "authenticated",
            "email": profile.get('emailAddress'),
            "service_available": True
        }
    except Exception as e:
        logger.error(f"Error checking email status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 