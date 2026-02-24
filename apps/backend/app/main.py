from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("/home/nahuel/estudios/sgdba/TP_FINAL_NMDM/backend/app.log")
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="SIMFUT God Mode API - Using v6.0 Schema"
)

# CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

from fastapi.staticfiles import StaticFiles
import os

app.mount("/uploads", StaticFiles(directory="/home/nahuel/estudios/sgdba/TP_FINAL_NMDM/backend/uploads"), name="uploads")

@app.get("/")
def root():
    return {"message": "Welcome to SIMFUT God Mode API", "version": "1.0"}

from app.api.api import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_check():
    return {"status": "ok"}
