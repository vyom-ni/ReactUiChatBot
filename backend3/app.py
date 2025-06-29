from fastapi import FastAPI
from dotenv import load_dotenv
import logging
from fastapi.middleware.cors import CORSMiddleware

from routers import chat, property, health, auth, admin, schedule

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(
    title="Property Assistant API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(property.router)
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(schedule.router)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to AI Property Assistant API",
        "version": "1.0.0",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
    )