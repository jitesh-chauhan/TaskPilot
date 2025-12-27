import time
import logging

from fastapi import Body, Depends, HTTPException
from fastapi.responses import ORJSONResponse
from jose import jwt
from pymongo.asynchronous.database import AsyncDatabase

from app.apis.users.model import User, UserCreateReq
from app.database.database import get_db
from app.utils.auth_utils import hash_password

logger = logging.getLogger(__name__)


async def create_user(body: UserCreateReq = Body(), db: AsyncDatabase = Depends(get_db)):
    logger.info("Create user request received")

    try:
        body = body.model_dump()
        email = body.get("email")
        logger.debug("Checking if user exists: %s", email)

        existing_user = await db.users.find_one({"email": email})
        if existing_user:
            logger.warning("User already exists: %s", email)
            raise HTTPException(409, "User Already Exists")

        password = body.get("password")
        username = body.get("username")

        logger.debug("Hashing password for user: %s", email)
        hashed_pass = hash_password(password)

        timestamp = str(int(time.time() * 1000))
        user = User(
            **{
                "email": email,
                "username": username,
                "password": hashed_pass,
                "created_at": timestamp,
                "updated_at": "",
                "role": "user",
                "enabled": True,
            }
        )

        logger.debug("Inserting user into database: %s", email)
        await db.users.insert_one(user.model_dump(exclude={"_id"}))

        user_data = await db.users.find_one({"email": email})
        if user_data:
            user_data["id"] = str(user_data.pop("_id"))
            user_data.pop("password", None)

        logger.info("User created successfully: %s", email)
        return ORJSONResponse(
            {
                "data": [user_data],
                "status": "success",
                "message": "User Created Successfully",
            },
            status_code=201,
        )

    except HTTPException as e:
        logger.warning(
            "Create user failed for %s | %s",
            body.get("email"),
            e.detail,
        )
        return ORJSONResponse(
            {"data": [], "message": e.detail, "status": "failed"},
            e.status_code,
        )

    except Exception as e:
        logger.exception("Unexpected error while creating user")
        return ORJSONResponse(
            {"data": [], "status": "failed", "message": str(e)}, 500
        )


async def get_current_userid(token):
    logger.debug("Decoding JWT token to extract user_id")

    payload = jwt.decode(token, "Authorization", algorithms=["HS256"])
    email = payload.get("user_id")

    logger.debug("Extracted user_id from token: %s", email)
    return email


async def ger_user(email: str, db: AsyncDatabase = Depends(get_db)):
    logger.info("Get user request received for email: %s", email)

    try:
        user = await db.users.find_one({"email": email})
        if not user:
            logger.warning("User not found: %s", email)
            raise HTTPException(status_code=404, detail="User Not Found")

        user["id"] = str(user.pop("_id"))
        user.pop("password")

        logger.info("User retrieved successfully: %s", email)
        return ORJSONResponse(
            {"data": [user], "status": "success", "message": "User Found"},
            status_code=200,
        )

    except HTTPException as e:
        logger.warning(
            "Get user failed for %s | %s",
            email,
            e.detail,
        )
        return ORJSONResponse(
            {"data": [], "message": e.detail, "status": "failed"},
            e.status_code,
        )

    except Exception as e:
        logger.exception("Unexpected error while fetching user: %s", email)
        return ORJSONResponse(
            {"data": [], "status": "failed", "message": str(e)}, 500
        )
