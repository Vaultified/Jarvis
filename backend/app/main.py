import os
from dotenv import load_dotenv

load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import chat, tts, stt, passive_listen, plugins, auth

app = FastAPI(
    title="Jarvis AI Assistant API",
    description="""
    A comprehensive AI assistant API featuring:
    - Chat with LLaMA model
    - Text-to-Speech using macOS 'say' command
    - Speech-to-Text using Whisper
    - Passive listening with wake word detection
    - Plugin system for extensible functionality
    - Google OAuth2 authentication for Drive and Gmail
    """,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    contact={
        "name": "Jarvis AI Assistant",
        "url": "https://github.com/yourusername/jarvis",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    }
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with tags for better organization
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(tts.router, prefix="/api", tags=["Text-to-Speech"])
app.include_router(stt.router, prefix="/api", tags=["Speech-to-Text"])
app.include_router(passive_listen.router, prefix="/api", tags=["Passive Listening"])
app.include_router(plugins.router, prefix="/api", tags=["Plugins"])
app.include_router(auth.router, prefix="/api", tags=["Authentication"])

@app.get("/api/health")
async def health_check():
    """Health check endpoint to verify API status."""
    return {"status": "healthy"}
