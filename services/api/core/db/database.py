"""Database configuration and session management with async support."""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    AsyncEngine
)

from ..utils.config import settings
from services.shared.core.models import Base


def get_db_engine(test_mode: bool = False) -> AsyncEngine:
    """
    Create and return an async database engine.
    
    Supports:
    - PostgreSQL with asyncpg driver (production)
    - SQLite with aiosqlite driver (testing)
    
    Args:
        test_mode: If True, use SQLite for testing
        
    Returns:
        AsyncEngine instance
    """
    database_url = settings.database_url
    
    # Parse database URL to determine type
    if test_mode or database_url.startswith("sqlite"):
        # SQLite for testing
        sqlite_path = "test.db" if test_mode else "dprod.db"
        database_url = f"sqlite+aiosqlite:///./{sqlite_path}"
        connect_args = {"check_same_thread": False}
    else:
        # PostgreSQL with asyncpg
        connect_args = {}
    
    return create_async_engine(
        database_url,
        echo=settings.debug,
        future=True,
        connect_args=connect_args,
        pool_pre_ping=True,  # Test connections before using them
        pool_size=5,         # Smaller pool for serverless databases
        max_overflow=10,     # Allow temporary connections
        pool_recycle=300,    # Recycle connections after 5 minutes
    )


# Create async engine
engine = get_db_engine()

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get database session.
    
    Usage in FastAPI routes:
        async def my_route(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
    
    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# For backward compatibility
__all__ = [
    "engine",
    "AsyncSessionLocal",
    "get_db",
    "Base",
]
