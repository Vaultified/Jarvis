from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List
from ..services.gmail_service import send_email

router = APIRouter()

class EmailRequest(BaseModel):
    to: List[EmailStr]
    subject: str
    body: str

@router.post("/send")
async def send_gmail(request: EmailRequest):
    """Send an email using Gmail API."""
    try:
        result = send_email(
            to=request.to,
            subject=request.subject,
            body=request.body
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": "Email sent successfully",
                "details": result["details"]
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result["message"]
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send email: {str(e)}"
        ) 