# db/database.py 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os 

# --- NEW: Get URL from Environment ---
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    # This prevents the app from crashing silently if the .env file isn't loaded
    raise Exception("DATABASE_URL environment variable is not set. Check your .env file and main.py setup.")


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()