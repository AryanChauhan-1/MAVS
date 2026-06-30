from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from app.api import upload, validate

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="HireLens",
    description="Powered by MAVS (Multi-Agent Validation System)",
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
        "project": "HireLens API Gateway",
        "documentation": "/docs"
    }