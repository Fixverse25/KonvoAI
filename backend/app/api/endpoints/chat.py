"""
Chat API Endpoints
Handles text-based chat interactions with Claude
"""

import asyncio
import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import get_settings
from app.core.logging import get_logger
from app.services.claude_service import claude_service
from app.services.redis_service import redis_service

router = APIRouter()
logger = get_logger(__name__)
settings = get_settings()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: str = None


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str
    session_id: str = None
    stream: bool = False
    history: List[Dict[str, str]] = []


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    session_id: str
    message_id: str


@router.post("/", response_model=ChatResponse)
# @limiter.limit(f"{settings.rate_limit_requests_per_minute}/minute")  # Temporarily disabled for debugging
async def chat(
    request: Request,
    chat_request: ChatRequest
) -> ChatResponse:
    """
    Send a chat message and get a response from Claude
    """
    logger.info(f"Chat endpoint called with message: {chat_request.message[:50]}...")
    try:
        # Get Redis service from app state
        redis_svc = request.app.state.redis

        # Generate session ID if not provided
        session_id = chat_request.session_id or str(uuid.uuid4())
        message_id = str(uuid.uuid4())

        # Get conversation history from Redis
        conversation_key = f"conversation:{session_id}"
        conversation_history = await redis_svc.get(conversation_key) or []
        
        # Add user message to history
        user_message = {
            "role": "user",
            "content": chat_request.message,
            "timestamp": str(uuid.uuid4()),
            "message_id": str(uuid.uuid4())
        }
        conversation_history.append(user_message)
        
        # Format messages for Claude
        claude_messages = claude_service.format_conversation_history(conversation_history)
        
        # Get response from Claude
        response_text = await claude_service.chat_completion(claude_messages)
        
        if not response_text:
            raise HTTPException(status_code=500, detail="Failed to get response from AI")
        
        # Add assistant response to history
        assistant_message = {
            "role": "assistant",
            "content": response_text,
            "timestamp": str(uuid.uuid4()),
            "message_id": message_id
        }
        conversation_history.append(assistant_message)
        
        # Save updated conversation to Redis (expire after 1 hour)
        logger.info(f"Saving conversation to Redis for session {session_id}")
        try:
            await asyncio.wait_for(
                redis_svc.set(conversation_key, conversation_history, expire=3600),
                timeout=5.0
            )
            logger.info(f"Conversation saved to Redis for session {session_id}")
        except asyncio.TimeoutError:
            logger.warning(f"Redis save timeout for session {session_id}")
        except Exception as e:
            logger.error(f"Redis save error for session {session_id}: {e}")

        logger.info(f"Chat response generated for session {session_id}")

        # Return simple dict instead of Pydantic model for debugging
        response_data = {
            "response": response_text,
            "session_id": session_id,
            "message_id": message_id
        }
        logger.info(f"Returning response data: {len(str(response_data))} chars")

        # Try explicit JSONResponse with CORS headers
        return JSONResponse(
            content=response_data,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/test")
async def test_endpoint():
    """Simple test endpoint to debug response issues"""
    logger.info("Test endpoint called")
    return {"status": "ok", "message": "Test endpoint working"}


@router.post("/test-post")
def test_post_endpoint_sync(data: dict):
    """Simple SYNC POST test endpoint"""
    logger.info(f"Test SYNC POST endpoint called with: {data}")
    return JSONResponse(
        content={"status": "ok", "received": data, "sync": True},
        headers={"Access-Control-Allow-Origin": "*"}
    )


@router.post("/test-post-async")
async def test_post_endpoint_async(data: dict):
    """Simple ASYNC POST test endpoint"""
    logger.info(f"Test ASYNC POST endpoint called with: {data}")
    return JSONResponse(
        content={"status": "ok", "received": data, "async": True},
        headers={"Access-Control-Allow-Origin": "*"}
    )


@router.post("/stream")
@limiter.limit(f"{settings.rate_limit_requests_per_minute}/minute")
async def chat_stream(
    request: Request,
    chat_request: ChatRequest
):
    """
    Send a chat message and get a streaming response from Claude
    """
    try:
        # Generate session ID if not provided
        session_id = chat_request.session_id or str(uuid.uuid4())
        
        # Get conversation history from Redis
        conversation_key = f"conversation:{session_id}"
        conversation_history = await redis_service.get(conversation_key) or []
        
        # Add user message to history
        user_message = {
            "role": "user",
            "content": chat_request.message,
            "timestamp": str(uuid.uuid4()),
            "message_id": str(uuid.uuid4())
        }
        conversation_history.append(user_message)
        
        # Format messages for Claude
        claude_messages = claude_service.format_conversation_history(conversation_history)
        
        async def generate_response():
            """Generate streaming response"""
            full_response = ""
            
            try:
                async for chunk in claude_service.stream_completion(claude_messages):
                    full_response += chunk
                    yield f"data: {chunk}\n\n"
                
                # Add assistant response to history
                assistant_message = {
                    "role": "assistant",
                    "content": full_response,
                    "timestamp": str(uuid.uuid4()),
                    "message_id": str(uuid.uuid4())
                }
                conversation_history.append(assistant_message)
                
                # Save updated conversation to Redis
                await redis_service.set(conversation_key, conversation_history, expire=3600)
                
                # Send end marker
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                yield f"data: Error: {str(e)}\n\n"
        
        return StreamingResponse(
            generate_response(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Session-ID": session_id
            }
        )
        
    except Exception as e:
        logger.error(f"Chat stream endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/history/{session_id}")
@limiter.limit(f"{settings.rate_limit_requests_per_minute}/minute")
async def get_chat_history(
    request: Request,
    session_id: str
) -> List[Dict[str, Any]]:
    """
    Get chat history for a session
    """
    try:
        conversation_key = f"conversation:{session_id}"
        conversation_history = await redis_service.get(conversation_key) or []
        
        logger.info(f"Retrieved chat history for session {session_id}")
        return conversation_history
        
    except Exception as e:
        logger.error(f"Get chat history error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/history/{session_id}")
@limiter.limit(f"{settings.rate_limit_requests_per_minute}/minute")
async def clear_chat_history(
    request: Request,
    session_id: str
) -> Dict[str, str]:
    """
    Clear chat history for a session
    """
    try:
        conversation_key = f"conversation:{session_id}"
        await redis_service.delete(conversation_key)
        
        logger.info(f"Cleared chat history for session {session_id}")
        return {"message": "Chat history cleared successfully"}
        
    except Exception as e:
        logger.error(f"Clear chat history error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/log-message")
@limiter.limit(f"{settings.rate_limit_requests_per_minute}/minute")
async def log_message(
    request: Request,
    message_data: Dict[str, str]
) -> Dict[str, str]:
    """
    Log a user message for analytics/monitoring
    """
    try:
        message = message_data.get("message", "")
        if message:
            logger.info(f"User message logged: {message[:100]}...")

        return {"status": "logged"}

    except Exception as e:
        logger.error(f"Log message error: {e}")
        return {"status": "error"}
