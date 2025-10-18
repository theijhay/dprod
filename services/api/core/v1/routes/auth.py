"""Authentication endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ...db.database import get_db
from ...v1.auth.jwt_handler import create_access_token, verify_token
from ...v1.auth.password_handler import hash_password, verify_password
from services.shared.core.models import User, UserCreate, UserResponse
from services.shared.core.exceptions import AuthenticationError

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user."""
    # Check if user already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create new user
    import secrets
    api_key = secrets.token_urlsafe(32)
    
    new_user = User(
        email=user_data.email,
        api_key=api_key,
        status=user_data.status
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return UserResponse.from_orm(new_user)


@router.post("/login")
async def login_user(
    email: str,
    password: str = None,  # For future password-based auth
    db: AsyncSession = Depends(get_db)
):
    """Login user and return API key."""
    # For now, just return the API key for the user
    result = await db.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    return {
        "api_key": user.api_key,
        "user": UserResponse.from_orm(user)
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Get current user information."""
    api_key = credentials.credentials
    
    result = await db.execute(
        select(User).where(User.api_key == api_key)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return UserResponse.from_orm(user)
