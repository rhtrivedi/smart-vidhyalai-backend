import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Add the root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.database import Base, SQLALCHEMY_DATABASE_URL
from app.models import *

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# --- THE BULLETPROOF URL OVERRIDE ---
# 1. Grab the Render URL, but if it doesn't exist, fall back to the local one
db_url = os.environ.get("DATABASE_URL", SQLALCHEMY_DATABASE_URL)

# 2. Fix Render's 'postgres://' quirk
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# 3. Set the URL securely into the Alembic config exactly ONCE
config.set_main_option("sqlalchemy.url", db_url)
# ------------------------------------


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Ensure the configuration dictionary strictly uses our overridden URL
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = config.get_main_option("sqlalchemy.url")

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
