"""Authentication schemas for request/response validation."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRegisterRequest(BaseModel):
    """Schema for user registration request."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User password (minimum 8 characters)"
    )

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLoginRequest(BaseModel):
    """Schema for user login request."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class TokenLoginRequest(BaseModel):
    """Schema for token-based login request."""
    token: str = Field(..., description="Authentication token (API key)")


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    api_key: str = Field(..., description="API key for CLI usage")


class UserAuthResponse(BaseModel):
    """Schema for authenticated user response."""
    id: UUID
    email: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """Schema for login response."""
    user: UserAuthResponse
    token: TokenResponse


class RegisterResponse(BaseModel):
    """Schema for registration response."""
    user: UserAuthResponse
    token: TokenResponse
    message: str = Field(
        default="Registration successful. Please save your API key for CLI usage.",
        description="Success message"
    )


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh request."""
    refresh_token: Optional[str] = Field(None, description="Refresh token (future use)")


class PasswordChangeRequest(BaseModel):
    """Schema for password change request."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="New password"
    )

    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class APIKeyResponse(BaseModel):
    """Schema for API key response."""
    api_key: str = Field(..., description="API key")
    created_at: datetime = Field(..., description="Creation timestamp")
    message: str = Field(
        default="Please save this API key securely. It won't be shown again.",
        description="Important message"
    )
