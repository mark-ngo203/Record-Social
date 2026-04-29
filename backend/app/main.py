import sys
import logging
import signal
import uvicorn

from contextlib import asynccontextmanager
from fastapi import FastAPI
from pythonjsonlogger.json import JsonFormatter

from app.db.database import init_db

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

app = FastAPI(title="Record Social", lifespan=lifespan)

def serve():
    # Start the actual server
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    serve()
