from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from ..services.llm_service import LLMService

router = APIRouter()
llm_service = LLMService()

class ChatRequest(BaseModel):
    prompt: str = Field(
        ...,
        description="The text prompt to send to the LLaMA model",
        example="What is the capital of France?"
    )

class ChatResponse(BaseModel):
    response: str = Field(
        ...,
        description="The AI's response to the prompt",
        example="The capital of France is Paris."
    )

@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Chat with LLaMA",
    description="""
    Send a prompt to the LLaMA model and receive its response.
    
    This endpoint processes natural language input and returns an AI-generated response
    using the LLaMA language model.
    """,
    responses={
        200: {
            "description": "Successful response from LLaMA",
            "content": {
                "application/json": {
                    "example": {
                        "response": "The capital of France is Paris."
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Error generating response from LLaMA"
                    }
                }
            }
        }
    }
)
async def chat(request: ChatRequest):
    """
    Process a chat request with LLaMA.
    
    Args:
        request (ChatRequest): The chat request containing the prompt
        
    Returns:
        ChatResponse: The AI's response to the prompt
        
    Raises:
        HTTPException: If there's an error processing the request
    """
    try:
        response = llm_service.generate_response(request.prompt)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 