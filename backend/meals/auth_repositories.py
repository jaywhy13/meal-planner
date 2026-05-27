from __future__ import annotations

from dataclasses import dataclass

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode


class InvalidPasswordResetToken(Exception):
    pass


@dataclass(frozen=True)
class UserData:
    id: int
    email: str
    first_name: str
    last_name: str


class UserRepository:
    def get(
        self,
        user_id: int | None = None,
        email: str | None = None,
    ) -> UserData | None:
        try:
            if email is not None:
                user = User.objects.get(email=email)
            elif user_id is not None:
                user = User.objects.get(pk=user_id)
            else:
                return None
        except User.DoesNotExist:
            return None
        return self._to_user_data(user)

    def email_exists(self, email: str) -> bool:
        return User.objects.filter(email=email).exists()

    def create(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
    ) -> UserData:
        user: User = User.objects.create_user(
            username=email[:150],
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        return self._to_user_data(user)

    def set_password(self, user_id: int, new_password: str) -> None:
        user: User = User.objects.get(pk=user_id)
        user.set_password(new_password)
        user.save()

    def make_password_reset_token(self, user_id: int) -> tuple[str, str]:
        user: User = User.objects.get(pk=user_id)
        uid: str = urlsafe_base64_encode(force_bytes(user.pk))
        token: str = default_token_generator.make_token(user)
        return uid, token

    def verify_password_reset_token(self, uid: str, token: str) -> int:
        try:
            pk: str = force_str(urlsafe_base64_decode(uid))
            user: User = User.objects.get(pk=pk)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as error:
            raise InvalidPasswordResetToken() from error
        if not default_token_generator.check_token(user, token):
            raise InvalidPasswordResetToken()
        return user.pk

    def _to_user_data(self, user: User) -> UserData:
        return UserData(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
        )
