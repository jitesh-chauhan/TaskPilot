import time
import logging
from datetime import datetime

from bson import ObjectId
from fastapi import Body, HTTPException
from fastapi.params import Depends
from fastapi.responses import ORJSONResponse
from pymongo.asynchronous.database import AsyncDatabase

from app.apis.todos.model import TodoCreate
from app.database.database import get_db


logger = logging.getLogger(__name__)


async def create_todo(body: TodoCreate = Body(), db: AsyncDatabase = Depends(get_db)):
    try:
        logger.info("Create todo request received")
        body = body.model_dump()
        due_date = body.get("due_date")
        priority = body.get("priority")
        title = body.get("title")
        description = body.get("description")
        email = body.get("email")

        logger.debug(
            "Todo payload received | email=%s | title=%s | priority=%s",
            email,
            title,
            priority,
        )

        date_obj = datetime.strptime(due_date, "%Y-%m-%d")
        due_date_ts = int(date_obj.timestamp() * 1000)
        current_time = int(time.time() * 1000)

        await db.todos.insert_one(
            {
                "user_id": email,
                "title": title,
                "description": description,
                "due_date": str(due_date_ts),
                "completed": False,
                "priority": priority,
                "created_at": str(current_time),
                "updated_at": "",
                "is_deleted": False,
                "deleted_at": "",
            }
        )

        logger.info("Todo created successfully | email=%s | title=%s", email, title)

        return ORJSONResponse(
            {"data": [], "status": "success", "message": "Todo Created"}, 201
        )

    except Exception as e:
        logger.exception("Error while creating todo")
        return ORJSONResponse({"data": [], "message": str(e), "status": "failed"}, 500)


async def get_todos_by_userid(email: str, db: AsyncDatabase = Depends(get_db)):
    try:
        logger.info("Get todos request received | email=%s", email)

        todos = (
            await db.todos.find({"user_id": email, "is_deleted": False})
            .sort("-created_at")
            .to_list(100)
        )

        if not todos:
            logger.warning("No todos found for user | email=%s", email)
            raise HTTPException(status_code=404, detail="No Todos Found")

        for todo in todos:
            todo["id"] = str(todo.pop("_id"))
            due_date_str = todo.get("due_date")
            timestamp_ms = int(due_date_str)
            todo["due_date"] = datetime.fromtimestamp(timestamp_ms / 1000).strftime(
                "%Y-%m-%d"
            )

        logger.info("Todos fetched successfully | email=%s | count=%d", email, len(todos))

        return ORJSONResponse({"data": todos}, 200)

    except HTTPException as e:
        logger.warning(
            "Handled error while fetching todos | email=%s | reason=%s",
            email,
            e.detail,
        )
        return ORJSONResponse(
            {"data": [], "message": str(e.detail), "status": "failed"}, e.status_code
        )
    except Exception as e:
        logger.exception("Unhandled error while fetching todos | email=%s", email)
        return ORJSONResponse({"data": [], "message": str(e), "status": "failed"}, 500)


async def delete_todo(todo_id: str, db: AsyncDatabase = Depends(get_db)):
    try:
        logger.info("Delete todo request received | todo_id=%s", todo_id)

        current_time = str(int(time.time()))
        result = await db.todos.update_one(
            {"_id": ObjectId(todo_id)},
            {"$set": {"is_deleted": True, "deleted_at": current_time}},
        )

        if result.modified_count == 0:
            logger.warning("Todo not found | todo_id=%s", todo_id)
            raise HTTPException(status_code=404, detail="Todo not found")

        logger.info("Todo marked as deleted | todo_id=%s", todo_id)

        return ORJSONResponse(
            {"data": [], "message": "Todo marked as deleted", "status": "success"},
            status_code=200,
        )

    except HTTPException as e:
        logger.warning(
            "Handled error while deleting todo | todo_id=%s | reason=%s",
            todo_id,
            e.detail,
        )
        return ORJSONResponse(
            {"data": [], "message": str(e.detail), "status": "failed"}, e.status_code
        )
    except Exception as e:
        logger.exception("Unhandled error while deleting todo | todo_id=%s", todo_id)
        return ORJSONResponse({"data": [], "message": str(e), "status": "failed"}, 500)
