import logging
import time
from datetime import date

from jose import ExpiredSignatureError
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.apis.users.views import get_current_userid
from app.templates.init_templates import templates
from app.utils.api_handler import api_handler


logger = logging.getLogger(__name__)


async def login_page(request: Request, msg: str = None, error: str = None):
    logger.info("Login page accessed | method=%s", request.method)
    try:
        if request.method == "POST":
            form = await request.form()
            body = {"email": form.get("email"), "password": form.get("password")}

            logger.info("Login attempt | email=%s", body.get("email"))

            res = await api_handler("POST", "/login", body=body)

            if res.get("status") == "failed":
                logger.warning(
                    "Login failed | email=%s | reason=%s",
                    body.get("email"),
                    res.get("message"),
                )
                return templates.TemplateResponse(
                    "login.html",
                    {"request": request, "error": res.get("message"),  "is_auth_page": True},
                    status_code=401,
                )

            data_list = res.get("data", [])
            if data_list:
                token = data_list[0].get("access_token")
                logger.info("Login successful | email=%s", body.get("email"))

                response = RedirectResponse(url="/home", status_code=303)
                response.set_cookie(
                    key="access_token", value=token, httponly=True, max_age=3600
                )
                return response

            logger.warning("Login failed | email=%s | empty token response", body.get("email"))
            return templates.TemplateResponse(
                "login.html", {"request": request, "error": "Invalid email or password"}
            )

        return templates.TemplateResponse(
            "login.html", {"request": request, "error": error, "msg": msg,  "is_auth_page": True}
        )
    except Exception:
        logger.exception("Unhandled error while loading home page")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "Something went wrong",},
            status_code=500,
        )

async def homepage(request: Request, msg: str = None, error: str = None):
    logger.info("Home page requested")
    token = request.cookies.get("access_token")
    if not token:
        logger.warning("Home access denied | missing access_token")
        return RedirectResponse(
            url="/login?error=Session+expired.+Please+sign+in+again."
        )
    try:


        email = await get_current_userid(token)
        logger.debug("Authenticated user | email=%s", email)

        users = await api_handler("GET", "/users", params={"email": email}, token=token)
        if users.get("status") == "failed":
            message = users.get("message", "").lower()
            logger.warning(
                "User lookup failed | email=%s | message=%s", email, message
            )

            return RedirectResponse(
                url="/login?error=unauthorized",
                status_code=status.HTTP_303_SEE_OTHER,
            )

        todos_res = await api_handler(
            "GET", "/todos", params={"email": email}, token=token
        )

        if todos_res.get("status") == "failed":
            error = todos_res.get("message", "")
            logger.warning("Todo fetch failed | email=%s | message=%s", email, error)

        todos = todos_res.get("data", [])
        logger.info("Todos loaded | email=%s | count=%d", email, len(todos))

        return templates.TemplateResponse(
            "todo_list.html",
            {
                "request": request,
                "todos": todos,
                "msg": msg,
                "user": users.get("data")[0],
                "error": error,
            },
        )

    except ExpiredSignatureError:
        logger.warning("Session expired (JWT) during home access")
        return RedirectResponse(url="/login?error=session_expired")

    except Exception:
        logger.exception("Unhandled error while loading home page")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "Something went wrong"},
            status_code=500,
        )


async def register_page(request: Request, msg: str = None, error: str = None):
    logger.info("Register page accessed | method=%s", request.method)
    try:
        if request.method == "POST":
            form = await request.form()

            if form.get("password") != form.get("confirm_password"):
                logger.warning(
                    "Registration failed | email=%s | password mismatch",
                    form.get("email"),
                )
                return templates.TemplateResponse(
                    "register.html",
                    {"request": request, "error": "Passwords do not match", "is_auth_page": True},
                    status_code=400,
                )

            body = {
                "username": form.get("username"),
                "email": form.get("email"),
                "password": form.get("password"),
                "role": "user",
                "created_at": str(int(time.time() * 1000)),
                "updated_at": "",
                "enabled": True,
            }

            logger.info("User registration attempt | email=%s", body.get("email"))

            res = await api_handler("POST", "/users", body=body)
            if res.get("status") == "failed":
                logger.warning(
                    "Registration failed | email=%s | reason=%s",
                    body.get("email"),
                    res.get("message"),
                )
                return templates.TemplateResponse(
                    "register.html",
                    {"request": request, "error": res.get("message"), "is_auth_page": True },
                    status_code=400,
                )

            res = await api_handler(
                "POST",
                "/login",
                body={"email": form.get("email"), "password": form.get("password")},
            )

            if res.get("status") == "failed":
                logger.warning(
                    "Auto-login after registration failed | email=%s",
                    form.get("email"),
                )
                return templates.TemplateResponse(
                    "register.html",
                    {"request": request, "error": res.get("message"),  "is_auth_page": True},
                    status_code=400,
                )

            data_list = res.get("data", [])
            if data_list:
                token = data_list[0].get("access_token")
                logger.info("User registered and logged in | email=%s", form.get("email"))

                response = RedirectResponse(url="/home", status_code=303)
                response.set_cookie(
                    key="access_token", value=token, httponly=True, max_age=3600
                )
                return response

            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

        return templates.TemplateResponse(
            "register.html", {"request": request, "error": error, "msg": msg,  "is_auth_page": True}
        )
    except Exception:
        logger.exception("Unhandled error while loading home page")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "Something went wrong"},
            status_code=500,
        )

async def add_todo_page(request: Request, msg: str = None, error: str = None):
    logger.info("Add todo page accessed | method=%s", request.method)
    try:
        token = request.cookies.get("access_token")
        if not token:
            logger.warning("Add todo denied | missing access_token")
            return RedirectResponse(url="/login")

        email = await get_current_userid(token)
        logger.debug("Add todo user | email=%s", email)

        users = await api_handler("GET", "/users", params={"email": email}, token=token)
        if users.get("status") == "failed":
            logger.warning("Add todo user validation failed | email=%s", email)
            message = users.get("message", "").lower()
            if "token" in message or "unauthorized" in message or "expired" in message:
                return RedirectResponse(url="/login?error=session_expired")
            return RedirectResponse(url="/login?error=account_not_found")

        if request.method == "POST":
            form = await request.form()
            body = {
                "title": form.get("todo"),
                "description": form.get("description"),
                "due_date": form.get("due_date"),
                "priority": form.get("priority"),
                "email": await get_current_userid(token),
            }

            logger.info("Creating todo | email=%s | title=%s", email, body.get("title"))

            res = await api_handler("POST", "/todos/create", body=body, token=token)
            if res.get("status") == "failed":
                logger.warning(
                    "Todo creation failed | email=%s | reason=%s",
                    email,
                    res.get("message"),
                )
                return templates.TemplateResponse(
                    "add_todo.html", {"request": request,"error": res.get("message"), "today": date.today().isoformat()}
                )

            logger.info("Todo created | email=%s", email)
            return RedirectResponse(url="/home", status_code=status.HTTP_303_SEE_OTHER)
        return templates.TemplateResponse(
            "add_todo.html",
            {"request": request, "user": users.get("data")[0], "today": date.today().isoformat(), "error": error, "msg": msg},
        )

    except Exception:
        logger.exception("Unhandled error while loading home page")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "Something went wrong"},
            status_code=500,
        )


async def delete_todo(request: Request, todo_id: str):
    logger.info("Delete todo requested | todo_id=%s", todo_id)
    token = request.cookies.get("access_token")
    if not token:
        logger.warning("Delete todo denied | missing access_token")
        return RedirectResponse(url="/login")
    try:

        await api_handler("DELETE", "/todos", params={"todo_id": todo_id}, token=token)
        logger.info("Todo deleted | todo_id=%s", todo_id)

        return RedirectResponse(url="/home?msg=Task+Removed", status_code=303)
    except Exception:
        logger.exception("Unhandled error while loading home page")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "Something went wrong"},
            status_code=500,
        )

async def logout_user(request: Request):
    logger.info("User logout initiated")
    try:
        response = RedirectResponse(url="/login", status_code=302)
        response.delete_cookie(key="access_token")

        logger.info("User logged out successfully")
        return response
    except Exception:
        logger.exception("Unhandled error while loading home page")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "Something went wrong"},
            status_code=500,
        )


async def complete_todo_page(request: Request, todo_id: str):
    logger.info("Mark complete todo requested | todo_id=%s", todo_id)
    token = request.cookies.get("access_token")
    if not token:
        logger.warning("Mark complete todo denied | missing access_token")
        return RedirectResponse(url="/login")
    try:
        await api_handler("PUT", "/todos/complete", params={"todo_id": todo_id}, token=token)
        logger.info("Todo deleted | todo_id=%s", todo_id)

        return RedirectResponse(url="/home?msg=Task+Completed", status_code=303)
    except Exception:
        logger.exception("Unhandled error while loading home page")
        return templates.TemplateResponse(
                "error.html",
                {"request": request, "error": "Something went wrong"},
                status_code=500,
            )
