from fastapi import APIRouter, HTTPException
from datetime import datetime
import logging
from models.chat import ChatRequest, ChatResponse
from services.chatbot import EnhancedPropertyChatbot

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    responses={404: {"description": "Not found"}},
)
sessions = {}

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint for property assistance"""
    try:
        session_id = request.session_id 
        
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Invalid session ID")
        
        session_chatbot = sessions[session_id]
        response, suggestions = session_chatbot.get_ai_response(request.query)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return ChatResponse(
            response=response,
            suggestions=suggestions,
            session_id=session_id,
            timestamp=timestamp
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")
    
@router.get("/create_session")
async def create_session():
    """Create a new chat session"""
    try:
        session_id = f"session_{datetime.now().timestamp()}"
        sessions[session_id] = EnhancedPropertyChatbot()
        return {"session_id": session_id, "message": "Session created successfully"}
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Session creation error: {str(e)}")

@router.delete("/session/{session_id}")
async def clear_session(session_id: str):

    try:
        if session_id in sessions:
            del sessions[session_id]
            return {"message": f"Session {session_id} cleared successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        logger.error(f"Error clearing session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Session clear error: {str(e)}")

@router.get("/sessions")
async def get_active_sessions():
    try:
        active_sessions = list(sessions.keys())
        return {
            "active_sessions": active_sessions,
            "total_sessions": len(active_sessions)
        }
    except Exception as e:
        logger.error(f"Error getting sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sessions error: {str(e)}")

