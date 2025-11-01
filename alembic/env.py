import os
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from alembic import context

# Interpret the config file for Python logging.
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import target metadata from our SQLAlchemy Base
from services.shared.core.models import Base  # noqa: E402

target_metadata = Base.metadata

def get_database_url() -> str:
    # Prefer env var set by CI/CD; fallback to alembic.ini sqlalchemy.url
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    return config.get_main_option("sqlalchemy.url")


def run_migrations_offline() -> None:
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    url = get_database_url()
    connectable = create_async_engine(url, poolclass=pool.NullPool)

    async def do_run() -> None:
        async with connectable.connect() as connection:
            await connection.run_sync(run_async_migrations)

    import asyncio

    asyncio.run(do_run())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
