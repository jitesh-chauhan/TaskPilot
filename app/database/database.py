import logging

from pymongo import AsyncMongoClient
from starlette.requests import Request

from core.config import settings

logger = logging.getLogger(__name__)

mongodb_client = AsyncMongoClient(settings.MONGO_URI)


async def init_db():
    logger.info("Initializing MongoDB connection")

    try:
        db = mongodb_client[settings.DB_NAME]
        logger.info("MongoDB connection initialized successfully")
        return db
    except Exception as e:
        logger.error(
            "MongoDB initialization failed | error=%s",
            str(e),
            exc_info=True,
        )
        raise


async def close_db():
    logger.info("Closing MongoDB connection")
    try:
        mongodb_client = AsyncMongoClient(settings.MONGO_URI)
        await mongodb_client.close()
        logger.info("MongoDB connection closed successfully")
    except Exception as e:
        logger.error(
            "Failed to close MongoDB connection | error=%s",
            str(e),
            exc_info=True,
        )


async def get_db(request: Request):
    logger.debug("Providing database instance from application state")
    return request.app.state.db
