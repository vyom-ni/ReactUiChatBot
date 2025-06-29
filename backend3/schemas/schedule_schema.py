from pydantic import BaseModel
from typing import Optional


class AppointmentDetails(BaseModel):
    id: str
    name: str
    date: str
    time: str
    status: str

class ScheduleSchema(BaseModel):
    fullName: str
    phone: Optional[str]
    date: str
    time: str
    message: str

class ScheduleResponseSchema(BaseModel):
    success: bool
    message: str
    appointment_id: str
    appointment: AppointmentDetails

