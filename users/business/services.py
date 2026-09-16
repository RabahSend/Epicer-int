from __future__ import annotations

from users.business.rules import validate_user
from users.data.repositories import UserRepository
from users.models import User


class UserService:
    def __init__(self) -> None:
        self.repository = UserRepository()

    def list_users(self) -> list[User]:
        return self.repository.list()

    def get_user(self, user_id: int) -> User | None:
        return self.repository.get_by_id(user_id)

    def register_user(self, email: str, first_name: str = "", last_name: str = "") -> User:
        email = email.strip().lower()
        first_name = first_name.strip()
        last_name = last_name.strip()
        validate_user(email, first_name, last_name)

        if self.repository.get_by_email(email) is not None:
            raise ValueError("Un utilisateur existe déjà avec cet email.")

        return self.repository.create(email, first_name, last_name)
