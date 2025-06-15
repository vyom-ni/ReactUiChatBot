from pydantic import BaseModel

class PropertyDetailsRequest(BaseModel):
    property_name: str

class PropertyDetailsResponse(BaseModel):
    details: str

class PropertyDeitail(BaseModel):
    property_name: str
    place_type: str 