"""Schemas package for API v1."""

from .auth_schema import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenLoginRequest,
    RegisterResponse,
    LoginResponse,
    TokenResponse,
    UserAuthResponse,
    PasswordChangeRequest,
    APIKeyResponse,
)

__all__ = [
    "UserRegisterRequest",
    "UserLoginRequest",
    "TokenLoginRequest",
    "RegisterResponse",
    "LoginResponse",
    "TokenResponse",
    "UserAuthResponse",
    "PasswordChangeRequest",
    "APIKeyResponse",
]
