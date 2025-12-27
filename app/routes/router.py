from fastapi import FastAPI

from app.apis.auth.routes import AuthRouter
from app.apis.todos.routes import TodoRouter
from app.apis.users.routes import UserRouter
from app.pages.page_router import PageRouter


def include_routes(app: FastAPI):
    app.include_router(
        TodoRouter,
        prefix="/api/v1",
    )
    app.include_router(
        AuthRouter,
        prefix="/api/v1",
    )
    app.include_router(
        UserRouter,
        prefix="/api/v1",
    )
    app.include_router(
        PageRouter,
        prefix="",
    )
