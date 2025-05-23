from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import chat
from .api import tts

app = FastAPI(title="AI Desktop Assistant API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api")
app.include_router(tts.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "AI Desktop Assistant API is running"}
