from __future__ import annotations


class InvalidUserError(ValueError):
    """Règle métier utilisateur non respectée."""


def validate_email(email: str) -> None:
    if not email or "@" not in email or "." not in email.split("@")[-1]:
        raise InvalidUserError("Adresse email invalide.")


def validate_user(email: str, first_name: str, last_name: str) -> None:
    validate_email(email)
    if not first_name.strip() and not last_name.strip():
        raise InvalidUserError("Un prénom ou un nom est requis.")
