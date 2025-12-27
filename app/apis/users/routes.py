from fastapi import APIRouter, Depends

from app.apis.auth.model import ErrorResponse
from app.apis.users.model import UserResponse
from app.apis.users.views import create_user, ger_user
from app.utils.auth_utils import get_token

UserRouter = APIRouter(
    prefix="/users", tags=["users"], dependencies=[Depends(get_token)]
)

UserRouter.add_api_route("", create_user, methods=["POST"],
                         response_model=UserResponse,
                         responses={
                             401: {"model": ErrorResponse, "description": "Unauthorized"},
                             409: {"model": ErrorResponse, "description": "User not found"},
                             500: {"model": ErrorResponse, "description": "Internal Server Error"}
                         }
                         )
UserRouter.add_api_route("", ger_user, methods=["GET"],
                         response_model=UserResponse,
                         responses={
                             401: {"model": ErrorResponse, "description": "Unauthorized"},
                             404: {"model": ErrorResponse, "description": "User not found"},
                             500: {"model": ErrorResponse, "description": "Internal Server Error"}
                         }
                         )
