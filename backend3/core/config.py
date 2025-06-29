from dotenv import load_dotenv
import os

load_dotenv(override=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_MAPS_API_KEY=os.getenv("GOOGLE_MAPS_API_KEY")
USERS_FILE = os.getenv("USERS_FILE")
APARTMENT_DATA = os.getenv("APARTMENT_DATA")