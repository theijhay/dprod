from datetime import timedelta
from typing import Union

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.database import get_db
from ...utils.config import settings
from ...v1.auth.jwt_handler import verify_token
from ...v1.schemas.auth_schema import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenLoginRequest,
    RegisterResponse,
    LoginResponse,
    UserAuthResponse,
    TokenResponse,
    PasswordChangeRequest,
    APIKeyResponse,
)
from ...v1.services.auth_service import AuthService
from services.shared.core.exceptions import AuthenticationError

router = APIRouter(tags=["Authentication"])
security = HTTPBearer()


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Register a new user with email and password. Returns JWT token and API key for CLI usage."
)
async def register_user(
    user_data: UserRegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user account.
    
    - **email**: Valid email address (unique)
    - **password**: Minimum 8 characters with uppercase, lowercase, and digit
    
    Returns user info, JWT access token, and API key for CLI usage.
    """
    try:
        user, access_token, api_key = await AuthService.register_user(
            email=user_data.email,
            password=user_data.password,
            db=db
        )
        
        return RegisterResponse(
            user=UserAuthResponse.model_validate(user),
            token=TokenResponse(
                access_token=access_token,
                token_type="bearer",
                expires_in=settings.access_token_expire_minutes * 60,
                api_key=api_key
            )
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login with email and password",
    description="Authenticate user with email and password. Returns JWT token and API key."
)
async def login_with_password(
    login_data: UserLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with email and password.
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns JWT access token and user information.
    """
    try:
        user, access_token = await AuthService.authenticate_user(
            email=login_data.email,
            password=login_data.password,
            db=db
        )
        
        return LoginResponse(
            user=UserAuthResponse.model_validate(user),
            token=TokenResponse(
                access_token=access_token,
                token_type="bearer",
                expires_in=settings.access_token_expire_minutes * 60,
                api_key=user.api_key
            )
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post(
    "/login/token",
    response_model=LoginResponse,
    summary="Login with API token",
    description="Authenticate using API key/token (for CLI usage). Returns JWT token."
)
async def login_with_token(
    token_data: TokenLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with API token (for CLI usage).
    
    - **token**: API key obtained during registration
    
    Returns JWT access token and user information.
    """
    try:
        user, access_token = await AuthService.authenticate_with_token(
            token=token_data.token,
            db=db
        )
        
        return LoginResponse(
            user=UserAuthResponse.model_validate(user),
            token=TokenResponse(
                access_token=access_token,
                token_type="bearer",
                expires_in=settings.access_token_expire_minutes * 60,
                api_key=user.api_key
            )
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Dependency to get current authenticated user.
    
    Supports both JWT tokens and API keys.
    """
    token = credentials.credentials
    
    # Try to verify as JWT token first
    try:
        email = verify_token(
            token,
            HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        )
        user = await AuthService.get_user_by_email(email, db)
    except:
        # If not a valid JWT, try as API key
        user = await AuthService.get_user_by_api_key(token, db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user


@router.get(
    "/me",
    response_model=UserAuthResponse,
    summary="Get current user",
    description="Get information about the currently authenticated user."
)
async def get_user_profile(
    current_user = Depends(get_current_user)
):
    """
    Get current authenticated user's profile.
    
    Requires valid JWT token or API key in Authorization header.
    """
    return UserAuthResponse.model_validate(current_user)


@router.post(
    "/password/change",
    response_model=UserAuthResponse,
    summary="Change password",
    description="Change the current user's password."
)
async def change_password(
    password_data: PasswordChangeRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change user password.
    
    - **current_password**: Current password
    - **new_password**: New password (min 8 chars with uppercase, lowercase, digit)
    
    Requires authentication.
    """
    try:
        updated_user = await AuthService.change_password(
            user_id=current_user.id,
            current_password=password_data.current_password,
            new_password=password_data.new_password,
            db=db
        )
        
        return UserAuthResponse.model_validate(updated_user)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/api-key/regenerate",
    response_model=APIKeyResponse,
    summary="Regenerate API key",
    description="Generate a new API key for the current user (invalidates old key)."
)
async def regenerate_api_key(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Regenerate API key for current user.
    
    WARNING: This will invalidate the old API key.
    Update your CLI configuration with the new key.
    
    Requires authentication.
    """
    try:
        updated_user, new_api_key = await AuthService.regenerate_api_key(
            user_id=current_user.id,
            db=db
        )
        
        return APIKeyResponse(
            api_key=new_api_key,
            created_at=updated_user.updated_at
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
