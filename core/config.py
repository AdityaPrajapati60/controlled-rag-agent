# app/core/config.py 

import os
from datetime import timedelta
from dotenv import load_dotenv # <--- ADDED: Load environment tool
from pathlib import Path       # <--- ADDED: Path tool


# Define the path to the project root (where .env lives)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
# Load the .env file explicitly
load_dotenv(BASE_DIR / ".env")
# ------------------------------------------------------------------


# Security Configuration
# os.getenv() will now reliably pull the value from the loaded .env file
SECRET_KEY = os.getenv("SECRET_KEY", "change_this_to_a_strong_secret")
ALGORITHM = "HS256"


# Token Expiration Configuration
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
ACCESS_TOKEN_EXPIRE = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")