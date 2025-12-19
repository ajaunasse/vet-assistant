"""Refresh token command and handler."""
from dataclasses import dataclass

from src.domain.entities import RefreshToken
from src.domain.repositories import UserRepository, RefreshTokenRepository
from src.infrastructure.security import JWTService


@dataclass
class RefreshTokenCommand:
    """Command to refresh access token."""
    refresh_token: str


@dataclass
class RefreshTokenResponse:
    """Response from token refresh."""
    access_token: str
    refresh_token: str


class RefreshTokenHandler:
    """Handler for refreshing access tokens."""

    def __init__(
        self,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
        jwt_service: JWTService,
    ):
        self.user_repository = user_repository
        self.refresh_token_repository = refresh_token_repository
        self.jwt_service = jwt_service

    async def handle(self, command: RefreshTokenCommand) -> RefreshTokenResponse:
        """
        Handle token refresh.

        Args:
            command: Refresh command with refresh token

        Returns:
            RefreshTokenResponse with new tokens

        Raises:
            ValueError: If refresh token is invalid or expired
        """
        # Verify refresh token JWT
        payload = self.jwt_service.verify_token(command.refresh_token, token_type="refresh")
        if not payload:
            raise ValueError("Invalid refresh token")

        user_id = payload.get("sub")
        token_id = payload.get("token_id")

        if not user_id or not token_id:
            raise ValueError("Invalid refresh token payload")

        # Get user
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        # Check if user is still verified
        if not user.is_verified:
            raise ValueError("User email not verified")

        # Create new access token
        access_token = self.jwt_service.create_access_token(
            data={"sub": user.id, "email": user.email}
        )

        # Create new refresh token entity
        new_refresh_token_entity = RefreshToken.create(user_id=user.id)

        # Save new refresh token to database
        await self.refresh_token_repository.create(new_refresh_token_entity)

        # Create new refresh token JWT
        new_refresh_token_jwt = self.jwt_service.create_refresh_token(
            data={"sub": user.id, "token_id": new_refresh_token_entity.id}
        )

        return RefreshTokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token_jwt,
        )
