import time
from typing import Dict

import bcrypt
from fastapi import HTTPException, Request
from fastapi.responses import ORJSONResponse
from jose import ExpiredSignatureError, JWTError, jwt

from core.config import settings


def hash_password(password):
    salt = bcrypt.gensalt()
    password_bytes = password.encode("utf-8")
    password_hash = bcrypt.hashpw(password_bytes, salt).decode("utf-8")
    return password_hash


def verify_password(raw_password: str, hash_password: str):
    if not raw_password or not hash_password:
        return False
    password_bytes = raw_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hash_password.encode("utf-8"))


def signJWT(user_id: str) -> Dict[str, str]:
    payload = {"user_id": user_id, "expires": time.time() + 24 * 60 * 60}
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")
    return {"access_token": token}


def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        if decoded_token["expires"] >= time.time():
            return decoded_token
        return None
    except ExpiredSignatureError:
        return None
    except JWTError:
        return None


async def get_token(request: Request):
    try:
        token = request.headers.get(settings.JWT_SECRET_KEY)
        if not token:
            raise HTTPException(
                status_code=403, detail=f"Header '{settings.JWT_SECRET_KEY}' is missing!"
            )
        payload = decodeJWT(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Token is invalid or expired")
        return payload
    except HTTPException as e:
        return ORJSONResponse(
            content={"data": [], "message": e.detail, "status": "failed"},
            status_code=e.status_code,
        )
