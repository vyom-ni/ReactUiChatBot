from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
from schemas.schedule_schema import ScheduleSchema
from schemas.schedule_schema import ScheduleResponseSchema
import logging, uuid, os, json
from datetime import datetime
from core.config import SCHEDULE_DATA

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/schedule", tags=["schedule"])

SCHEDULE_FILE = SCHEDULE_DATA

def generate_appointment_id():
    return str(uuid.uuid4())

def save_appointment_to_file(appointment):
    if os.path.exists(SCHEDULE_FILE):
        with open(SCHEDULE_FILE, 'r') as f:
            data = json.load(f)
    else:
        data = {}

    # Save appointment using its ID as key
    data[appointment['id']] = appointment

    with open(SCHEDULE_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@router.post('/', response_model=ScheduleResponseSchema)
async def schedule_appointment(request_model: ScheduleSchema = Body(...)):
    try:
        appointment = {
            'id': generate_appointment_id(),
            'name': request_model.fullName,
            'phone': request_model.phone,
            'date': request_model.date,
            'time': request_model.time,
            'message': request_model.message,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        save_appointment_to_file(appointment)

        logger.info(f"New appointment scheduled: {appointment['id']} for {appointment['name']}")

        return {
            'success': True,
            'message': 'Appointment scheduled successfully!',
            'appointment_id': appointment['id'],
            'appointment': {
                'id': appointment['id'],
                'name': appointment['name'],
                'date': appointment['date'],
                'time': appointment['time'],
                'status': appointment['status']
            }
        }

    except Exception as e:
        logger.error(f"Error scheduling appointment: {e}")
        return JSONResponse(content={
            'success': False,
            'error': 'Internal server error. Please try again later.'
        }, status_code=500)