import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from starlette import status
from starlette.requests import Request

from app.database.database import close_db, init_db
from app.routes.router import include_routes
from app.utils.logging import setup_logging

setup_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup initiated")

    app.state.db = await init_db()

    try:
        await app.state.db.command("ping")
        logger.info("MongoDB ping successful")
    except Exception as e:
        logger.warning(
            "MongoDB ping failed, retrying after delay | error=%s",
            str(e),
            exc_info=True,
        )
        await asyncio.sleep(5)
        logger.info("Retrying MongoDB initialization")
        await init_db()

    logger.info("Application startup completed")
    yield

    logger.info("Application shutdown initiated")
    await close_db()
    logger.info("Application shutdown completed")


app = FastAPI(lifespan=lifespan, title="To-Do App")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    logger.warning(
        "Request validation error | path=%s | errors=%s",
        request.url.path,
        exc.errors(),
    )
    return ORJSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"message": "Invalid Documents ", "status": "failed"},
    )


logger.info("Registering application routes")
include_routes(app)
logger.info("Routes registered successfully")
