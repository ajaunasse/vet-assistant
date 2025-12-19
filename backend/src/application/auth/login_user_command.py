"""Login user command and handler."""
from dataclasses import dataclass

from src.domain.entities import User, RefreshToken
from src.domain.repositories import UserRepository, RefreshTokenRepository
from src.infrastructure.security import PasswordService, JWTService


@dataclass
class LoginUserCommand:
    """Command to login a user."""
    email: str
    password: str


@dataclass
class LoginResponse:
    """Response from login containing tokens and user."""
    access_token: str
    refresh_token: str
    user: User


class LoginUserHandler:
    """Handler for user login."""

    def __init__(
        self,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
        password_service: PasswordService,
        jwt_service: JWTService,
    ):
        self.user_repository = user_repository
        self.refresh_token_repository = refresh_token_repository
        self.password_service = password_service
        self.jwt_service = jwt_service

    async def handle(self, command: LoginUserCommand) -> LoginResponse:
        """
        Handle user login.

        Args:
            command: Login command with credentials

        Returns:
            LoginResponse with tokens and user data

        Raises:
            ValueError: If credentials are invalid or email not verified
        """
        # Get user by email
        user = await self.user_repository.get_by_email(command.email)
        if not user:
            raise ValueError("Email ou mot de passe invalide")

        # Verify password
        if not self.password_service.verify_password(command.password, user.hashed_password):
            raise ValueError("Email ou mot de passe invalide")

        # Check if email is verified
        if not user.is_verified:
            raise ValueError("Email non vérifié. Veuillez vérifier votre boîte de réception pour l'email de vérification.")

        # Create access token
        access_token = self.jwt_service.create_access_token(
            data={"sub": user.id, "email": user.email}
        )

        # Create refresh token entity
        refresh_token_entity = RefreshToken.create(user_id=user.id)

        # Save refresh token to database
        await self.refresh_token_repository.create(refresh_token_entity)

        # Create JWT from refresh token
        refresh_token_jwt = self.jwt_service.create_refresh_token(
            data={"sub": user.id, "token_id": refresh_token_entity.id}
        )

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token_jwt,
            user=user,
        )
