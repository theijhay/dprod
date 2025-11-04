"""Authentication service with business logic for user authentication."""

import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.shared.core.models import User, UserStatus
from services.shared.core.exceptions import AuthenticationError
from ...v1.auth.jwt_handler import create_access_token
from ...v1.auth.password_handler import hash_password, verify_password
from ...utils.config import settings


class AuthService:
    """Service for handling authentication operations with optimal performance."""

    @staticmethod
    async def register_user(
        email: str,
        password: str,
        db: AsyncSession
    ) -> Tuple[User, str, str]:
        """
        Register a new user with email and password.
        
        Args:
            email: User email address
            password: User password (plain text)
            db: Database session
            
        Returns:
            Tuple of (User, access_token, api_key)
            
        Raises:
            AuthenticationError: If user already exists
        """
        # Check if user exists (with index on email for O(log n) lookup)
        result = await db.execute(
            select(User).where(User.email == email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise AuthenticationError("User with this email already exists")
        
        # Generate secure API key
        api_key = secrets.token_urlsafe(32)
        
        # Hash password (bcrypt with 12 rounds by default - secure but fast)
        hashed_password = hash_password(password)
        
        # Create user
        new_user = User(
            email=email,
            password_hash=hashed_password,
            api_key=api_key,
            status=UserStatus.ACTIVE.value
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        # Create access token
        access_token = create_access_token(
            data={"sub": new_user.email, "user_id": str(new_user.id)},
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
        )
        
        return new_user, access_token, api_key

    @staticmethod
    async def authenticate_user(
        email: str,
        password: str,
        db: AsyncSession
    ) -> Tuple[User, str]:
        """
        Authenticate user with email and password.
        
        Args:
            email: User email address
            password: User password (plain text)
            db: Database session
            
        Returns:
            Tuple of (User, access_token)
            
        Raises:
            AuthenticationError: If credentials are invalid
        """
        # Fetch user by email (indexed lookup)
        result = await db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise AuthenticationError("Invalid credentials")
        
        # Verify password (constant-time comparison)
        if not verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid credentials")
        
        # Check user status
        if user.status != UserStatus.ACTIVE.value:
            raise AuthenticationError(f"User account is {user.status}")
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user.email, "user_id": str(user.id)},
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
        )
        
        return user, access_token

    @staticmethod
    async def authenticate_with_token(
        token: str,
        db: AsyncSession
    ) -> Tuple[User, str]:
        """
        Authenticate user with API key/token (for CLI usage).
        
        Args:
            token: API key token
            db: Database session
            
        Returns:
            Tuple of (User, access_token)
            
        Raises:
            AuthenticationError: If token is invalid
        """
        # Fetch user by API key (indexed lookup)
        result = await db.execute(
            select(User).where(User.api_key == token)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise AuthenticationError("Invalid token")
        
        # Check user status
        if user.status != UserStatus.ACTIVE.value:
            raise AuthenticationError(f"User account is {user.status}")
        
        # Create access token for session
        access_token = create_access_token(
            data={"sub": user.email, "user_id": str(user.id)},
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
        )
        
        return user, access_token

    @staticmethod
    async def get_user_by_id(
        user_id: UUID,
        db: AsyncSession
    ) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User UUID
            db: Database session
            
        Returns:
            User or None if not found
        """
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_email(
        email: str,
        db: AsyncSession
    ) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: User email
            db: Database session
            
        Returns:
            User or None if not found
        """
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_api_key(
        api_key: str,
        db: AsyncSession
    ) -> Optional[User]:
        """
        Get user by API key.
        
        Args:
            api_key: User API key
            db: Database session
            
        Returns:
            User or None if not found
        """
        result = await db.execute(
            select(User).where(User.api_key == api_key)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def change_password(
        user_id: UUID,
        current_password: str,
        new_password: str,
        db: AsyncSession
    ) -> User:
        """
        Change user password.
        
        Args:
            user_id: User UUID
            current_password: Current password
            new_password: New password
            db: Database session
            
        Returns:
            Updated User
            
        Raises:
            AuthenticationError: If current password is invalid
        """
        user = await AuthService.get_user_by_id(user_id, db)
        
        if not user:
            raise AuthenticationError("User not found")
        
        # Verify current password
        if not verify_password(current_password, user.password_hash):
            raise AuthenticationError("Invalid current password")
        
        # Update password
        user.password_hash = hash_password(new_password)
        user.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(user)
        
        return user

    @staticmethod
    async def regenerate_api_key(
        user_id: UUID,
        db: AsyncSession
    ) -> Tuple[User, str]:
        """
        Regenerate API key for a user.
        
        Args:
            user_id: User UUID
            db: Database session
            
        Returns:
            Tuple of (User, new_api_key)
            
        Raises:
            AuthenticationError: If user not found
        """
        user = await AuthService.get_user_by_id(user_id, db)
        
        if not user:
            raise AuthenticationError("User not found")
        
        # Generate new API key
        new_api_key = secrets.token_urlsafe(32)
        user.api_key = new_api_key
        user.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(user)
        
        return user, new_api_key
