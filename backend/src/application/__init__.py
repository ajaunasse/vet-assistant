"""Application layer containing use cases, commands, and queries."""
# Commands
from .create_session_command import CreateSessionCommand
from .send_message_command import SendMessageCommand

# Queries
from .get_session_query import GetSessionQuery
from .get_session_messages_query import GetSessionMessagesQuery
from .get_session_by_slug_query import GetSessionBySlugQuery

# Handlers
from .create_session_handler import CreateSessionHandler
from .send_message_handler import SendMessageHandler
from .get_session_handler import GetSessionHandler
from .get_session_messages_handler import GetSessionMessagesHandler

# Auth
from .auth import (
    RegisterUserCommand,
    RegisterUserHandler,
    LoginUserCommand,
    LoginUserHandler,
    LoginResponse,
    VerifyEmailCommand,
    VerifyEmailHandler,
    RefreshTokenCommand,
    RefreshTokenHandler,
    RefreshTokenResponse,
    UpdateProfileCommand,
    UpdateProfileHandler,
    LinkSessionToUserCommand,
    LinkSessionToUserHandler,
    GetUserQuery,
    GetUserHandler,
    GetUserSessionsQuery,
    GetUserSessionsHandler,
)

__all__ = [
    # Commands
    "CreateSessionCommand",
    "SendMessageCommand",
    # Queries
    "GetSessionQuery",
    "GetSessionMessagesQuery",
    "GetSessionBySlugQuery",
    # Handlers
    "CreateSessionHandler",
    "SendMessageHandler",
    "GetSessionHandler",
    "GetSessionMessagesHandler",
    # Auth
    "RegisterUserCommand",
    "RegisterUserHandler",
    "LoginUserCommand",
    "LoginUserHandler",
    "LoginResponse",
    "VerifyEmailCommand",
    "VerifyEmailHandler",
    "RefreshTokenCommand",
    "RefreshTokenHandler",
    "RefreshTokenResponse",
    "UpdateProfileCommand",
    "UpdateProfileHandler",
    "LinkSessionToUserCommand",
    "LinkSessionToUserHandler",
    "GetUserQuery",
    "GetUserHandler",
    "GetUserSessionsQuery",
    "GetUserSessionsHandler",
]