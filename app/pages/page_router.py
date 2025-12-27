from fastapi import APIRouter

from app.pages.pages import (
    add_todo_page,
    delete_todo,
    homepage,
    login_page,
    logout_user,
    register_page,
)

PageRouter = APIRouter(prefix="", tags=["Pages"])

PageRouter.add_api_route("/", homepage, name="home_redirect", methods=["GET"])
PageRouter.add_api_route("/login", login_page, name="login", methods=["POST", "GET"])
PageRouter.add_api_route(
    "/register", register_page, name="register", methods=["POST", "GET"]
)
PageRouter.add_api_route("/home", homepage, name="home")
PageRouter.add_api_route(
    "/add-todo", add_todo_page, name="todos", methods=["POST", "GET"]
)
PageRouter.add_api_route(
    "/delete-todo/{todo_id}", delete_todo, name="todos", methods=["POST"]
)
PageRouter.add_api_route("/logout", logout_user, name="todos", methods=["GET"])
