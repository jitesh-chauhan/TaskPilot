from fastapi import APIRouter, Depends

from app.apis.todos import views
from app.apis.todos.model import ErrorResponse, TodoResponse, TodoCreateResponse, TodoDeleteResponse
from app.utils.auth_utils import get_token

TodoRouter = APIRouter(
    prefix="/todos", tags=["Todos"], dependencies=[Depends(get_token)]
)

TodoRouter.add_api_route(
    "",
    views.get_todos_by_userid,
    methods=["GET"],
    response_model=TodoResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "User not found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    },
),
TodoRouter.add_api_route("/create", views.create_todo, methods=["POST"],
                         response_model=TodoCreateResponse,
                         responses={
                             401: {"model": ErrorResponse, "description": "Unauthorized"},
                             500: {"model": ErrorResponse, "description": "Internal Server Error"}
                         })
TodoRouter.add_api_route("", views.delete_todo, methods=["DELETE"],
                         response_model=TodoDeleteResponse,
                         responses={
                             401: {"model": ErrorResponse, "description": "Unauthorized"},
                             404: {"model": ErrorResponse, "description": "User not found"},
                             500: {"model": ErrorResponse, "description": "Internal Server Error"}
                         }
                         )
