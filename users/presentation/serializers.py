from __future__ import annotations

from typing import Any


class UserSerializer:
    required_fields = ("email",)

    def load(self, data: dict[str, Any]) -> dict[str, str]:
        missing = [field for field in self.required_fields if not data.get(field)]
        if missing:
            raise ValueError(f"Champs manquants : {', '.join(missing)}.")

        return {
            "email": str(data["email"]),
            "first_name": str(data.get("first_name", "")),
            "last_name": str(data.get("last_name", "")),
        }

    def dump(self, user: Any) -> dict[str, Any]:
        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }

    def dump_many(self, users: list[Any]) -> list[dict[str, Any]]:
        return [self.dump(user) for user in users]
