from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import logging
from models.property import PropertyDetailsRequest, PropertyDetailsResponse
from services.chatbot import EnhancedPropertyChatbot

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/properties",
    tags=["properties"],
    responses={404: {"description": "Not found"}},
)

chatbot = EnhancedPropertyChatbot()


@router.post("/details", response_model=PropertyDetailsResponse)
async def get_property_details(request: PropertyDetailsRequest):
    try:
        details = chatbot.get_property_details(request.property_name)
        return PropertyDetailsResponse(details=details)
        
    except Exception as e:
        logger.error(f"Error getting property details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Property details error: {str(e)}")

