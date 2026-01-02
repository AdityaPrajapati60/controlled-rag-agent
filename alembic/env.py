# alembic/env.py

import sys, os
from dotenv import load_dotenv

# --- Load environment variables FIRST ---
CURRENT_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_FILE_DIR)
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

sys.path.insert(0, PROJECT_ROOT)

from logging.config import fileConfig
from alembic import context
from sqlalchemy import pool
from db.database import Base, engine

# Import ALL models so Alembic sees them
import models
# Alembic config
config = context.config
fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
