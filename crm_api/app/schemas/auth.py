"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""Authentication schemas."""

from typing import List
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Login request payload."""

    email: EmailStr
    password: str


class TokenPair(BaseModel):
    """JWT token pair response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """JWT token payload."""

    sub: str  # Subject (user ID or email)
    roles: List[str]
    exp: int  # Expiration timestamp


class UserResponse(BaseModel):
    """User information response."""

    id: int
    email: str
    full_name: str
    roles: List[str]
    is_active: bool


__all__ = [
    "LoginRequest",
    "TokenPair",
    "TokenPayload",
    "UserResponse",
]
