import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .api import chat, auth
from .core.config import settings

load_dotenv()
app = FastAPI(
    title="Jarvis API",
    description="""
    Backend API for Jarvis, an AI-powered assistant.
    
    Features:
    - Chat with AI
    - User authentication
    - Gmail integration
    - Google Drive integration
    """,
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(auth.router, prefix="/api", tags=["Auth"])

@app.get("/")
async def root():
    """Root endpoint that returns API information."""
    return {
        "name": "Jarvis API",
        "version": "1.0.0",
        "status": "running",
        "documentation": "/docs"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint to verify API status."""
    return {"status": "healthy"}
