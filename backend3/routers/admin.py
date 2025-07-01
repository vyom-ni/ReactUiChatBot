import io
import os
import datetime
import logging
import json
from pathlib import Path
import pandas as pd
from fastapi import APIRouter, HTTPException, UploadFile, File
from core.config import USERS_FILE, APARTMENT_DATA, SCHEDULE_DATA
from routers.property import load_property_bot

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={404: {"description": "Not Found"}},
)

@router.get("/schedules")
def list_users():
    file_path = Path(SCHEDULE_DATA)

    if not file_path.exists():
        return {"message": "Schedule file not found.", "users": []}

    with open(file_path, "r") as file:
        data = json.load(file)

    users = []
    for user in data.values():
        users.append({
            "id": user.get("id"),
            "name": user.get("name"),
            "phone": user.get("phone"),
            "date": user.get("date"),
            "time": user.get("time"),
            "message": user.get("message"),
        })
            
    return {"users": users}

@router.put("/schedules/{appointment_id}")
def update_appointment_status(appointment_id: str, appointment_data: dict):
    if not os.path.exists(SCHEDULE_DATA):
        raise HTTPException(status_code=404, detail="No appointments found.")

    with open(SCHEDULE_DATA, 'r') as f:
        data = json.load(f)

    if appointment_id not in data:
        raise HTTPException(status_code=404, detail="Appointment not found.")

    # Update fields
    data[appointment_id].update(appointment_data)
    data[appointment_id]['updated_at'] = datetime.now().isoformat()

    with open(SCHEDULE_DATA, 'w') as f:
        json.dump(data, f, indent=4)

    return {
        "success": True,
        "message": "Appointment updated successfully.",
        "appointment": data[appointment_id]
    }
    

@router.delete("/schedules/{appointment_id}")
def delete_appointment(appointment_id: str):
    if not os.path.exists(SCHEDULE_DATA):
        raise HTTPException(status_code=404, detail="No appointments found.")

    with open(SCHEDULE_DATA, 'r') as f:
        data = json.load(f)

    if appointment_id not in data:
        raise HTTPException(status_code=404, detail="Appointment not found.")

    deleted_appointment = data.pop(appointment_id)

    with open(SCHEDULE_DATA, 'w') as f:
        json.dump(data, f, indent=4)

    return {
        "success": True,
        "message": "Appointment deleted successfully.",
        "deleted": deleted_appointment
    }

@router.post("/upload")
async def upload_data(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Only Excel files are allowed.")

        contents = await file.read()

        # Read Excel and drop fully empty rows
        df = pd.read_excel(io.BytesIO(contents))
        df.dropna(how="all", inplace=True)  # <-- Discard completely empty rows

        json_data = df.to_dict(orient="records")

        with open(APARTMENT_DATA, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2)

        load_property_bot()
        return {"message": "Excel file processed and saved successfully."}

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to process Excel file: {e}")

    