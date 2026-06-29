from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from app.api import upload, validate

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MAVS - Multi-Agent Validation Suite Engine",
    description="Production grade multi-agent cross-verification engine powered by Gemini 2.5 Flash",
    version="3.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(validate.router)

@app.get("/")
def health_check():
    return {
        "status": "online",
        "project": "MAVS Multi-Agent Validation Suite Engine Base Gateway",
        "documentation": "/docs"
    }