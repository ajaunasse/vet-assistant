"""FastAPI dependencies for authentication."""
import os
from typing import Optional, Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import User
from src.domain.repositories import UserRepository
from src.infrastructure import SQLUserRepository, JWTService
from src.infrastructure.database import get_database_session


# HTTP Bearer security scheme
security = HTTPBearer()


def get_jwt_service() -> JWTService:
    """Get JWT service instance."""
    secret_key = os.getenv("JWT_SECRET_KEY")
    if not secret_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT_SECRET_KEY not configured",
        )

    access_token_expire = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    refresh_token_expire = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "30"))

    return JWTService(
        secret_key=secret_key,
        access_token_expire_minutes=access_token_expire,
        refresh_token_expire_days=refresh_token_expire,
    )


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    jwt_service: Annotated[JWTService, Depends(get_jwt_service)],
    db_session: Annotated[AsyncSession, Depends(get_database_session)],
) -> User:
    """
    Get current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer credentials
        jwt_service: JWT service
        db_session: Database session

    Returns:
        Authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    # Extract token
    token = credentials.credentials

    # Verify token
    payload = jwt_service.verify_token(token, token_type="access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user ID from token
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    user_repository = SQLUserRepository(db_session)
    user = await user_repository.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is verified
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified",
        )

    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    jwt_service: JWTService = Depends(get_jwt_service),
    db_session: AsyncSession = Depends(get_database_session),
) -> Optional[User]:
    """
    Get current authenticated user from JWT token (optional).

    Returns None if no credentials provided or invalid.

    Args:
        credentials: HTTP Bearer credentials (optional)
        jwt_service: JWT service
        db_session: Database session

    Returns:
        Authenticated user or None
    """
    if not credentials:
        return None

    try:
        return await get_current_user(credentials, jwt_service, db_session)
    except HTTPException:
        return None
