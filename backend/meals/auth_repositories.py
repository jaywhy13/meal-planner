from __future__ import annotations

from dataclasses import dataclass

from django.contrib.auth.models import User


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

    def _to_user_data(self, user: User) -> UserData:
        return UserData(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
        )
