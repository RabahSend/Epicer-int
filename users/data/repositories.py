from __future__ import annotations

from users.models import User


class UserRepository:
    def get_by_id(self, user_id: int) -> User | None:
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def get_by_email(self, email: str) -> User | None:
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    def list(self) -> list[User]:
        return list(User.objects.all())

    def create(self, email: str, first_name: str, last_name: str) -> User:
        return User.objects.create(
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
