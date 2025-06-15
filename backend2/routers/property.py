from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import logging
from models.property import PropertyDetailsRequest, PropertyDetailsResponse, PropertyDeitail
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

@router.get("/list_properties")
async def get_properties():
    """Get all properties with coordinates for map display"""

    properties_with_coords = []
    for prop in chatbot.properties_data:
        if prop.get('Latitude') and prop.get('Longitude'):
            properties_with_coords.append({
                'id': len(properties_with_coords) + 1,
                'name': prop.get('Building Name'),
                'location': prop.get('Location'),
                'lat': prop.get('Latitude'),
                'lng': prop.get('Longitude'),
                'price': prop.get('Price Range (Lakhs)'),
                'types': prop.get('Apartment Types'),
                'amenities': prop.get('Amenities'),
                'contact': prop.get('Builder Contact'),
                'builder': prop.get('Builder Name'),
                'status': prop.get('Availability Status')
            })
    return {
        "properties": chatbot.properties_data,
        "map_properties": properties_with_coords,
        "count": len(properties_with_coords)
    }

@router.get('/nearby')
async def find_nearby(request: PropertyDeitail):
    """Find nearby places for a property"""
    try:
        data = request.get_json()
        property_name = data.get('property_name', '')
        place_type = data.get('place_type', 'school')
        
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