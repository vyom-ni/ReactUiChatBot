import io
import logging
import json
from pathlib import Path
import pandas as pd
from fastapi import APIRouter, HTTPException, UploadFile, File
from config import USERS_FILE, APARTMENT_DATA

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={404: {"description": "Not Found"}},
)

@router.get("/list-users")
def list_users():
    file_path = Path(USERS_FILE)

    if not file_path.exists():
        return {"message": "User registration file not found.", "users": []}

    with open(file_path, "r") as file:
        data = json.load(file)

    users = []
    for user in data.values():
        if user.get("name", "").lower() != "admin":
            users.append({
                "name": user.get("name"),
                "phone": user.get("phone"),
                "email": user.get("email")
            })

    return {"users": users}

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

        return {"message": "Excel file processed and saved successfully."}

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to process Excel file: {e}")

    