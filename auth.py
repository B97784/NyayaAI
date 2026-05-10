"""Auth helpers: password hashing + session helpers."""
import re
import bcrypt
from fastapi import HTTPException, Request

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def hash_password(pw: str) -> bytes:
    return bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt())


def verify_password(pw: str, h: bytes) -> bool:
    try:
        return bcrypt.checkpw(pw.encode("utf-8"), h)
    except Exception:
        return False


def validate_email(email: str) -> str:
    email = (email or "").strip().lower()
    if not EMAIL_RE.match(email):
        raise HTTPException(400, "Invalid email")
    return email


def validate_password(pw: str) -> str:
    if not pw or len(pw) < 8:
        raise HTTPException(400, "Password must be at least 8 characters")
    return pw


def current_user_id(request: Request) -> int:
    uid = request.session.get("uid")
    if not uid:
        raise HTTPException(401, "Not authenticated")
    return uid
