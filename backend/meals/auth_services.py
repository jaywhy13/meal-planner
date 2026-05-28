from __future__ import annotations

from dataclasses import dataclass

from typing import cast

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.settings import api_settings as jwt_settings
from rest_framework_simplejwt.tokens import RefreshToken

from django.conf import settings

from .auth_clients import EmailClient
from .auth_repositories import InvalidPasswordResetToken, UserData, UserRepository


class InvalidCredentials(Exception):
    pass


class EmailAlreadyExists(Exception):
    pass


class InvalidResetToken(Exception):
    pass


@dataclass(frozen=True)
class AuthResult:
    user: UserData
    refresh: RefreshToken


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository | None = None,
        email_client: EmailClient | None = None,
    ) -> None:
        self.user_repository = user_repository or UserRepository()
        self.email_client = email_client or EmailClient()

    def login(self, email: str, password: str) -> AuthResult:
        user_data: UserData | None = self.user_repository.get(email=email)
        if user_data is None:
            raise InvalidCredentials()

        authenticated_user: User | None = authenticate(
            username=email[:150],
            password=password,
        )
        if authenticated_user is None:
            raise InvalidCredentials()

        return AuthResult(
            user=user_data,
            refresh=cast(RefreshToken, RefreshToken.for_user(authenticated_user)),
        )

    def register(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
    ) -> AuthResult:
        if self.user_repository.email_exists(email):
            raise EmailAlreadyExists()

        new_user_data: UserData = self.user_repository.create(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        refresh = RefreshToken()
        refresh[jwt_settings.USER_ID_CLAIM] = new_user_data.id
        return AuthResult(user=new_user_data, refresh=refresh)

    def get_profile(self, user_id: int) -> UserData | None:
        return self.user_repository.get(user_id=user_id)

    def request_password_reset(self, email: str) -> None:
        user_data: UserData | None = self.user_repository.get(email=email)
        if user_data is None:
            return

        uid, token = self.user_repository.make_password_reset_token(user_data.id)
        reset_url: str = f"{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}"

        self.email_client.send_password_reset(
            recipient_email=email,
            recipient_name=user_data.first_name or user_data.email,
            reset_url=reset_url,
        )

    def reset_password(self, uid: str, token: str, new_password: str) -> None:
        try:
            user_id: int = self.user_repository.verify_password_reset_token(uid, token)
        except InvalidPasswordResetToken:
            raise InvalidResetToken()

        self.user_repository.set_password(user_id, new_password)
