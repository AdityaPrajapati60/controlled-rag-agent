#app/main.py
import os
import sys
from dotenv import load_dotenv

from fastapi.security import OAuth2PasswordBearer

# --- DEFINITIVE FIX: Path Resolution for Copied/Reloaded Folders ---
# 1. Get the directory of the currently executing file (main.py)
CURRENT_FILE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Go up two levels to reach the project root (task_ai_manager)
PROJECT_ROOT = os.path.dirname(CURRENT_FILE_DIR)

# 3. Define the path to the .env file
DOTENV_PATH = os.path.join(PROJECT_ROOT, '.env')

# Add project root to sys.path
sys.path.insert(0, PROJECT_ROOT)

# Explicitly load the environment variables
load_dotenv(DOTENV_PATH)


from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging

# Imports MUST be AFTER load_dotenv()
from db.database import Base, engine 
import models.task  # ensure task metadata registered
import models.user  # ensure user metadata registered
from api.routes import router as tasks_router
from api.auth import router as auth_router
from api import agent
from api import documents
from api.admin import router as admin_router
import models



# Define the OAuth2 scheme (tells FastAPI where the token is obtained)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token") 

app = FastAPI(
    title="Task AI Manager",
    # CRITICAL: This block adds the security method to the OpenAPI specification (Swagger UI)
    openapi_extra={
        "securitySchemes": {
            "Bearer Auth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        },
        # You can optionally set a global security requirement here
        "security": [{"Bearer Auth": []}]
    }
)


# include routers
app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(documents.router)
app.include_router(agent.router)
app.include_router(admin_router)




# basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.exception_handler(Exception)
async def universal_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled error: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/")
def root():
    return {"message": "Task AI Manager API is running!"}

