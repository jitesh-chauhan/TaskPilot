from fastapi import APIRouter

from app.apis.auth import views
from app.apis.auth.model import LoginResponse, ErrorResponse

AuthRouter = APIRouter(prefix="", tags=["Auth"])

AuthRouter.add_api_route("/login", views.login, name="login", methods=["POST"], response_model=LoginResponse,
                         responses={
                             # 400: {"model": ErrorResponse, "description": "Missing fields"},
                             401: {"model": ErrorResponse, "description": "Unauthorized"},
                             404: {"model": ErrorResponse, "description": "User not found"},
                             500: {"model": ErrorResponse, "description": "Internal Server Error"}
                         }
                         )
