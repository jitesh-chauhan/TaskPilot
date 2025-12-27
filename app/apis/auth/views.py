import logging

from fastapi import Body, Depends
from fastapi.responses import ORJSONResponse
from pymongo.asynchronous.database import AsyncDatabase
from starlette.exceptions import HTTPException

from app.apis.auth.model import AuthModel
from app.database.database import get_db
from app.utils.auth_utils import signJWT, verify_password


logger = logging.getLogger(__name__)


async def login(body: AuthModel = Body(), db: AsyncDatabase = Depends(get_db)):
    try:
        logger.info("Login request received")

        body = body.model_dump()
        email = body.get("email")
        password = body.get("password")

        if not email or not password:
            logger.warning("Login failed: email or password missing")
            raise HTTPException(400, "Email and password are required")

        user = await db.users.find_one({"email": email})
        if not user:
            logger.warning("Login failed: user not found | email=%s", email)
            raise HTTPException(404, "User not found")

        if not verify_password(password, user["password"]):
            logger.warning("Login failed: incorrect password | email=%s", email)
            raise HTTPException(401, "Incorrect password")

        token = signJWT(str(user.get("email")))

        logger.info("Login successful | email=%s", email)

        return ORJSONResponse(
            {"data": [token], "status": "success", "message": "Login successful"}
        )

    except HTTPException as e:
        logger.warning(
            "Handled login error | email=%s | status=%s | reason=%s",
            body.get("email") if isinstance(body, dict) else None,
            e.status_code,
            e.detail,
        )
        return ORJSONResponse(
            {"data": [], "message": e.detail, "status": "failed"}, e.status_code
        )

    except Exception as e:
        logger.exception("Unhandled error during login")
        return ORJSONResponse({"data": [], "status": "failed", "message": str(e)}, 500)
