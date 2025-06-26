from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import requests
import math
import logging
from models.property import PropertyDetailsRequest, PropertyDetailsResponse, PropertyDeitail
from services.chatbot import EnhancedPropertyChatbot

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/properties",
    tags=["properties"],
    responses={404: {"description": "Not found"}},
)

chatbot = None
def load_property_bot():
    global chatbot
    chatbot = EnhancedPropertyChatbot()

load_property_bot()

@router.post("/details", response_model=PropertyDetailsResponse)
async def get_property_details(request: PropertyDetailsRequest):
    try:
        details = chatbot.get_property_details(request.property_name)
        return PropertyDetailsResponse(details=details)
        
    except Exception as e:
        logger.error(f"Error getting property details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Property details error: {str(e)}")

@router.get("/list_properties")
async def get_properties():
    """Get all properties with coordinates for map display"""

    properties_with_coords = []
    clean_properties = []

    for prop in chatbot.properties_data:
        # Sanitize individual property
        sanitized_prop = {
            k: (None if isinstance(v, float) and (math.isnan(v) or math.isinf(v)) else v)
            for k, v in prop.items()
        }
        clean_properties.append(sanitized_prop)

        if sanitized_prop.get('Latitude') and sanitized_prop.get('Longitude'):
            properties_with_coords.append({
                'id': len(properties_with_coords) + 1,
                'name': sanitized_prop.get('Building Name'),
                'location': sanitized_prop.get('Location'),
                'lat': sanitized_prop.get('Latitude'),
                'lng': sanitized_prop.get('Longitude'),
                'price': sanitized_prop.get('Price Range (Lakhs)'),
                'types': sanitized_prop.get('Apartment Types'),
                'amenities': sanitized_prop.get('Amenities'),
                'contact': sanitized_prop.get('Builder Contact'),
                'builder': sanitized_prop.get('Builder Name'),
                'status': sanitized_prop.get('Availability Status')
            })

    return {
        "properties": clean_properties,
        "map_properties": properties_with_coords,
        "count": len(properties_with_coords)
    }

@router.post('/nearby')
async def find_nearby(request: PropertyDeitail):
    """Find nearby places for a property"""
    try:
        property_name = request.property_name
        place_type = request.place_type

        # Find the property
        target_property = None
        for prop in chatbot.properties_data:
            if property_name.lower() in prop.get('Building Name', '').lower():
                target_property = prop
                break
        
        if not target_property:
            raise HTTPException(
                status_code=404, 
                detail=f"Property '{property_name}' not found"
            )
        
        lat = target_property.get('Latitude')
        lng = target_property.get('Longitude')
        
        if not lat or not lng:
            raise HTTPException(
                status_code=400, 
                detail="Property coordinates not available"
            )
        
        # Find nearby places
        nearby_result = chatbot.find_nearby_places(lat, lng, place_type)
        
        logger.info(f"Found {len(nearby_result)} nearby places for {property_name} ({place_type})")
        return {
            "property": {
                "name": target_property.get('Building Name'),
                "location": target_property.get('Location'),
                "coordinates": {"lat": lat, "lng": lng}
            },
            "place_type": place_type,
            "nearby": nearby_result
        }
        
    except Exception as e:
        print(f"❌ Error finding nearby places: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error finding nearby places: {str(e)}"
        )