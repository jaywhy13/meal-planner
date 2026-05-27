from __future__ import annotations

from dataclasses import dataclass

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.settings import api_settings as jwt_settings
from rest_framework_simplejwt.tokens import RefreshToken

from .auth_repositories import UserData, UserRepository


class InvalidCredentials(Exception):
    pass


class EmailAlreadyExists(Exception):
    pass


@dataclass(frozen=True)
class AuthResult:
    user: UserData
    refresh: RefreshToken


class AuthService:
    def __init__(self, user_repository: UserRepository | None = None) -> None:
        self.user_repository = user_repository or UserRepository()

    def login(self, email: str, password: str) -> AuthResult:
        user_data: UserData | None = self.user_repository.get(email=email)
        if user_data is None:
            raise InvalidCredentials()

        authenticated_user: User | None = authenticate(
            username=email[:150], password=password,
        )
        if authenticated_user is None:
            raise InvalidCredentials()

        return AuthResult(
            user=user_data,
            refresh=RefreshToken.for_user(authenticated_user),
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
