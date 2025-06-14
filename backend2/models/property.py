from pydantic import BaseModel

class PropertyDetailsRequest(BaseModel):
    property_name: str

class PropertyDetailsResponse(BaseModel):
    details: str