"""Alembic's entry point: tells Alembic which database to use and which tables should exist."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlmodel import SQLModel, create_engine

import app.models  # noqa: F401  (importing it registers every table on SQLModel.metadata)
from app.core.config import settings

# The Alembic Config object, which gives access to the values in alembic.ini.
config = context.config

# Set up Python logging from the [loggers] sections of alembic.ini.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# The tables the models define. Autogenerate compares them with the real database.
target_metadata = SQLModel.metadata

# NullPool: Alembic runs once and exits, so it doesn't need a pool of open connections.
engine = create_engine(settings.DATABASE_URL, poolclass=pool.NullPool)

# Connect, then run the migrations that haven't run yet, all in one transaction.
with engine.connect() as connection:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()