"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
CRM API Dependencies.

Dependency injection for database sessions, authentication, and authorization.
"""

from typing import Dict, Generator, Optional
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db, InMemoryDB
from app.core.security import verify_token, Role


def get_token_from_header(authorization: str = Header(...)) -> str:
    """
    Extract JWT token from Authorization header.

    Args:
        authorization: Authorization header value

    Returns:
        JWT token string

    Raises:
        HTTPException: If header format is invalid
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )

    return authorization[7:]  # Remove "Bearer " prefix


def get_claims(token: str = Depends(get_token_from_header)) -> Dict:
    """
    Get JWT claims from token.

    Args:
        token: JWT token string

    Returns:
        Decoded JWT claims

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        claims = verify_token(token)
        return claims
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(e)}",
        )


def require_sales_claims(
    claims: Dict = Depends(get_claims)
) -> Dict:
    """
    Require SALES, SALES_MANAGER, or OWNER role.

    Args:
        claims: JWT claims

    Returns:
        Claims if authorized

    Raises:
        HTTPException: If user doesn't have required role
    """
    user_roles = claims.get("roles", [])
    required_roles = [Role.SALES, Role.SALES_MANAGER, Role.OWNER]

    has_required_role = any(
        role.value in user_roles for role in required_roles
    )

    if not has_required_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Requires SALES, SALES_MANAGER, or OWNER role.",
        )

    return claims


def require_manager_claims(
    claims: Dict = Depends(get_claims)
) -> Dict:
    """
    Require SALES_MANAGER or OWNER role.

    Args:
        claims: JWT claims

    Returns:
        Claims if authorized

    Raises:
        HTTPException: If user doesn't have required role
    """
    user_roles = claims.get("roles", [])
    required_roles = [Role.SALES_MANAGER, Role.OWNER]

    has_required_role = any(
        role.value in user_roles for role in required_roles
    )

    if not has_required_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Requires SALES_MANAGER or OWNER role.",
        )

    return claims


def require_owner_claims(
    claims: Dict = Depends(get_claims)
) -> Dict:
    """
    Require OWNER role only.

    Args:
        claims: JWT claims

    Returns:
        Claims if authorized

    Raises:
        HTTPException: If user doesn't have OWNER role
    """
    user_roles = claims.get("roles", [])

    if Role.OWNER.value not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Requires OWNER role.",
        )

    return claims


# ============================================================================
# Integration Settings Dependencies
# ============================================================================


def get_ai_node_config(
    db: Session = Depends(get_db)
) -> Optional[object]:
    """
    Get AI Node integration configuration as a dependency.

    This allows other endpoints to easily access AI Node settings without
    manually querying the database.

    Usage:
        @router.post("/some-endpoint")
        def my_endpoint(config = Depends(get_ai_node_config)):
            if not config or not config.base_url:
                raise HTTPException(400, "AI Node not configured")

            bearer_token = config.get_secret()
            # ... use config

    Args:
        db: Database session

    Returns:
        IntegrationSetting instance for ai_node namespace, or None if not configured

    Example:
        ```python
        def trigger_ai_job(
            config: IntegrationSetting = Depends(get_ai_node_config),
            db: Session = Depends(get_db)
        ):
            if not config:
                raise HTTPException(400, "AI Node not configured")

            # Access config
            api_url = config.base_url
            token = config.get_secret()
            review_required = config.review_mode
        ```
    """
    from app.models.integrations import IntegrationSetting

    config = db.query(IntegrationSetting).filter(
        IntegrationSetting.namespace == "ai_node"
    ).first()

    return config


__all__ = [
    "get_db",
    "get_token_from_header",
    "get_claims",
    "require_sales_claims",
    "require_manager_claims",
    "require_owner_claims",
    "get_ai_node_config",
]
