import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI
from pythonjsonlogger.json import JsonFormatter

from app.db.database import init_db
from app.api.v1.api import api_router

# Setup logging
logger = logging.getLogger()

# 1. Create a handler
logHandler = logging.StreamHandler()

# 2. Apply the JSON Formatter
formatter = JsonFormatter('%(asctime)s %(name)s %(levelname)s %(message)s')
logHandler.setFormatter(formatter)

# 3. Add the handler to the Root Logger
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Startup: Run before the app starts taking requests
    logger.info("Starting up: Initializing database...")
    init_db()
    yield
    # 2. Shutdown: Run right before the app stops
    logger.info("Shutting down: Cleaning up resources...")

# Create FASTAPI app that executes lifespan before the server starts
app = FastAPI(title="Record Social", lifespan=lifespan)

# Add router to api endpoints
app.include_router(api_router, prefix="/api/v1")
