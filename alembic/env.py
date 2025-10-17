import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from api.db.database import Base
from api.v1.models import *
from dotenv import load_dotenv


load_dotenv()

config = context.config

if config.config_file_name:
    fileConfig(config.config_file_name)

db_url = os.getenv("DB_URL") or os.getenv("DATABASE_URL")
if not db_url:
    raise RuntimeError("DB_URL not found in environment.")

config.set_main_option("sqlalchemy.url", db_url)

target_metadata = Base.metadata

def include_object(object, name, type_, reflected, compare_to):
    return not (type_ == "table" and name in ("celery_taskmeta", "celery_tasksetmeta"))

def run_migrations_offline():
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        include_object=include_object,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            include_object=include_object,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
