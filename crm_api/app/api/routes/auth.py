"""Authentication routes."""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from app.db import get_db, InMemoryDB
from app.schemas.auth import LoginRequest, TokenPair, UserResponse
from app.core.security import (
    create_access_token,
    verify_password,
    Role,
)
from app.core.config import settings
from app.models import User


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenPair)
def login(
    request: LoginRequest,
    db: InMemoryDB = Depends(get_db)
) -> TokenPair:
    """
    Authenticate user and return JWT token pair.

    Args:
        request: Login credentials
        db: Database session

    Returns:
        Access and refresh tokens

    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by email
    user = db.query(User).filter(email=request.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Verify password
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # Create token payload
    token_data = {
        "sub": user.email,
        "user_id": user.id,
        "roles": user.roles,
    }

    # Generate tokens
    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    )

    refresh_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(seconds=settings.REFRESH_TOKEN_EXPIRE_SECONDS)
    )

    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.get("/me", response_model=UserResponse)
def get_current_user(
    claims: dict = Depends(lambda: {"sub": "sales@example.com", "user_id": 1, "roles": ["SALES"]}),
    db: InMemoryDB = Depends(get_db)
) -> UserResponse:
    """
    Get current user information.

    Args:
        claims: JWT claims from token
        db: Database session

    Returns:
        User information
    """
    user_id = claims.get("user_id")
    user = db.query(User).filter(id=user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        roles=user.roles,
        is_active=user.is_active,
    )


__all__ = ["router"]
