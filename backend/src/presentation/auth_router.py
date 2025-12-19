"""FastAPI router for authentication endpoints."""
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.auth import (
    RegisterUserCommand,
    RegisterUserHandler,
    LoginUserCommand,
    LoginUserHandler,
    VerifyEmailCommand,
    VerifyEmailHandler,
    RefreshTokenCommand,
    RefreshTokenHandler,
    UpdateProfileCommand,
    UpdateProfileHandler,
    GetUserQuery,
    GetUserHandler,
    GetUserSessionsQuery,
    GetUserSessionsHandler,
    ResendVerificationCommand,
    ResendVerificationHandler,
)
from src.domain.entities import User
from src.infrastructure import (
    SQLUserRepository,
    SQLRefreshTokenRepository,
    SQLSessionRepository,
    PasswordService,
    JWTService,
    EmailService,
)
from src.infrastructure.database import get_database_session
from .dependencies import get_current_user, get_jwt_service
from .schemas import (
    RegisterRequest,
    LoginRequest,
    RefreshTokenRequest,
    UpdateProfileRequest,
    UserResponse,
    TokenResponse,
    VerifyEmailResponse,
    ResendVerificationRequest,
    ResendVerificationResponse,
    SessionResponse,
    VeterinaryAssessmentResponse,
    PatientDataResponse,
)


router = APIRouter(prefix="/auth", tags=["Authentication"])


# Dependency functions

def get_password_service() -> PasswordService:
    """Get password service instance."""
    return PasswordService()


def get_email_service() -> EmailService:
    """Get email service instance."""
    try:
        return EmailService()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Email service not configured: {str(e)}",
        )


def get_register_handler(
    db_session: Annotated[AsyncSession, Depends(get_database_session)],
    password_service: Annotated[PasswordService, Depends(get_password_service)],
    email_service: Annotated[EmailService, Depends(get_email_service)],
) -> RegisterUserHandler:
    """Get register user handler."""
    user_repo = SQLUserRepository(db_session)
    return RegisterUserHandler(user_repo, password_service, email_service)


def get_login_handler(
    db_session: Annotated[AsyncSession, Depends(get_database_session)],
    password_service: Annotated[PasswordService, Depends(get_password_service)],
    jwt_service: Annotated[JWTService, Depends(get_jwt_service)],
) -> LoginUserHandler:
    """Get login user handler."""
    user_repo = SQLUserRepository(db_session)
    refresh_token_repo = SQLRefreshTokenRepository(db_session)
    return LoginUserHandler(user_repo, refresh_token_repo, password_service, jwt_service)


def get_verify_email_handler(
    db_session: Annotated[AsyncSession, Depends(get_database_session)],
) -> VerifyEmailHandler:
    """Get verify email handler."""
    user_repo = SQLUserRepository(db_session)
    return VerifyEmailHandler(user_repo)


def get_refresh_token_handler(
    db_session: Annotated[AsyncSession, Depends(get_database_session)],
    jwt_service: Annotated[JWTService, Depends(get_jwt_service)],
) -> RefreshTokenHandler:
    """Get refresh token handler."""
    user_repo = SQLUserRepository(db_session)
    refresh_token_repo = SQLRefreshTokenRepository(db_session)
    return RefreshTokenHandler(user_repo, refresh_token_repo, jwt_service)


def get_update_profile_handler(
    db_session: Annotated[AsyncSession, Depends(get_database_session)],
) -> UpdateProfileHandler:
    """Get update profile handler."""
    user_repo = SQLUserRepository(db_session)
    return UpdateProfileHandler(user_repo)


def get_user_handler(
    db_session: Annotated[AsyncSession, Depends(get_database_session)],
) -> GetUserHandler:
    """Get user handler."""
    user_repo = SQLUserRepository(db_session)
    return GetUserHandler(user_repo)


def get_user_sessions_handler(
    db_session: Annotated[AsyncSession, Depends(get_database_session)],
) -> GetUserSessionsHandler:
    """Get user sessions handler."""
    session_repo = SQLSessionRepository(db_session)
    return GetUserSessionsHandler(session_repo)


def get_resend_verification_handler(
    db_session: Annotated[AsyncSession, Depends(get_database_session)],
    email_service: Annotated[EmailService, Depends(get_email_service)],
) -> ResendVerificationHandler:
    """Get resend verification handler."""
    user_repo = SQLUserRepository(db_session)
    return ResendVerificationHandler(user_repo, email_service)


# API Endpoints

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    handler: Annotated[RegisterUserHandler, Depends(get_register_handler)],
) -> UserResponse:
    """
    Register a new user.

    Creates a new user account and sends a verification email.
    """
    try:
        command = RegisterUserCommand(
            email=request.email,
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name,
            clinic_name=request.clinic_name,
            order_number=request.order_number,
            specialty=request.specialty,
            is_student=request.is_student,
            school_name=request.school_name,
        )
        user = await handler.handle(command)

        return UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            clinic_name=user.clinic_name,
            order_number=user.order_number,
            specialty=user.specialty,
            is_student=user.is_student,
            school_name=user.school_name,
            is_verified=user.is_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    handler: Annotated[LoginUserHandler, Depends(get_login_handler)],
) -> TokenResponse:
    """
    Login with email and password.

    Returns access and refresh tokens upon successful authentication.
    """
    try:
        command = LoginUserCommand(email=request.email, password=request.password)
        response = await handler.handle(command)

        user_response = UserResponse(
            id=response.user.id,
            email=response.user.email,
            first_name=response.user.first_name,
            last_name=response.user.last_name,
            clinic_name=response.user.clinic_name,
            order_number=response.user.order_number,
            specialty=response.user.specialty,
            is_student=response.user.is_student,
            school_name=response.user.school_name,
            is_verified=response.user.is_verified,
            created_at=response.user.created_at,
            updated_at=response.user.updated_at,
        )

        return TokenResponse(
            access_token=response.access_token,
            refresh_token=response.refresh_token,
            user=user_response,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/verify-email", response_model=VerifyEmailResponse)
async def verify_email(
    handler: Annotated[VerifyEmailHandler, Depends(get_verify_email_handler)],
    token: Annotated[str, Query(..., description="Email verification token")],
) -> VerifyEmailResponse:
    """
    Verify user email with token.

    Confirms the user's email address using the token sent via email.
    """
    try:
        command = VerifyEmailCommand(token=token)
        user = await handler.handle(command)

        return VerifyEmailResponse(
            verified=True,
            message=f"Email {user.email} successfully verified",
        )
    except ValueError as e:
        return VerifyEmailResponse(verified=False, message=str(e))


@router.post("/resend-verification", response_model=ResendVerificationResponse)
async def resend_verification(
    request: ResendVerificationRequest,
    handler: Annotated[ResendVerificationHandler, Depends(get_resend_verification_handler)],
) -> ResendVerificationResponse:
    """
    Resend verification email.

    Sends a new verification email to the user.
    """
    try:
        command = ResendVerificationCommand(email=request.email)
        await handler.handle(command)

        return ResendVerificationResponse(
            success=True,
            message="Email de vérification renvoyé avec succès",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    handler: Annotated[RefreshTokenHandler, Depends(get_refresh_token_handler)],
) -> TokenResponse:
    """
    Refresh access token using refresh token.

    Returns new access and refresh tokens.
    """
    try:
        command = RefreshTokenCommand(refresh_token=request.refresh_token)
        response = await handler.handle(command)

        # We need to get user info for the response
        # Extract user_id from the new access token
        jwt_service = get_jwt_service()
        payload = jwt_service.verify_token(response.access_token, token_type="access")

        if payload:
            user_id = payload.get("sub")
            # Get user from database
            from src.infrastructure.database import get_database_session
            async for db_session in get_database_session():
                user_repo = SQLUserRepository(db_session)
                user = await user_repo.get_by_id(user_id)

                if user:
                    user_response = UserResponse(
                        id=user.id,
                        email=user.email,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        clinic_name=user.clinic_name,
                        order_number=user.order_number,
                        specialty=user.specialty,
                        is_student=user.is_student,
                        school_name=user.school_name,
                        is_verified=user.is_verified,
                        created_at=user.created_at,
                        updated_at=user.updated_at,
                    )

                    return TokenResponse(
                        access_token=response.access_token,
                        refresh_token=response.refresh_token,
                        user=user_response,
                    )
                break

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh token",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    """
    Get current user information.

    Requires authentication.
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        clinic_name=current_user.clinic_name,
        order_number=current_user.order_number,
        specialty=current_user.specialty,
        is_student=current_user.is_student,
        school_name=current_user.school_name,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    request: UpdateProfileRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    handler: Annotated[UpdateProfileHandler, Depends(get_update_profile_handler)],
) -> UserResponse:
    """
    Update user profile.

    Requires authentication.
    """
    try:
        command = UpdateProfileCommand(
            user_id=current_user.id,
            first_name=request.first_name,
            last_name=request.last_name,
            clinic_name=request.clinic_name,
            order_number=request.order_number,
            specialty=request.specialty,
            is_student=request.is_student,
            school_name=request.school_name,
        )
        user = await handler.handle(command)

        return UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            clinic_name=user.clinic_name,
            order_number=user.order_number,
            specialty=user.specialty,
            is_student=user.is_student,
            school_name=user.school_name,
            is_verified=user.is_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/sessions", response_model=List[SessionResponse])
async def get_user_sessions(
    current_user: Annotated[User, Depends(get_current_user)],
    handler: Annotated[GetUserSessionsHandler, Depends(get_user_sessions_handler)],
) -> List[SessionResponse]:
    """
    Get all sessions for current user.

    Requires authentication.
    """
    query = GetUserSessionsQuery(user_id=current_user.id)
    sessions = await handler.handle(query)

    return [
        SessionResponse(
            id=session.id,
            created_at=session.created_at,
            updated_at=session.updated_at,
            slug=session.slug,
            current_assessment=(
                VeterinaryAssessmentResponse(
                    assessment=session.current_assessment.assessment,
                    status=session.current_assessment.status,
                    localization=session.current_assessment.localization,
                    differentials=session.current_assessment.differentials,
                    diagnostics=session.current_assessment.diagnostics,
                    treatment=session.current_assessment.treatment,
                    prognosis=session.current_assessment.prognosis,
                    question=session.current_assessment.question,
                    confidence_level=session.current_assessment.confidence_level,
                )
                if session.current_assessment
                else None
            ),
            patient_data=(
                PatientDataResponse(**session.patient_data.to_dict())
                if session.patient_data
                else None
            ),
            is_collecting_data=session.is_collecting_data,
        )
        for session in sessions
    ]
