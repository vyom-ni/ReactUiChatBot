from dotenv import load_dotenv
import os

load_dotenv(override=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")