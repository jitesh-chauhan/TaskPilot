from unittest.mock import AsyncMock, Mock

import pytest
from bson import ObjectId


class TestTodoAPI:

    @pytest.mark.asyncio
    async def test_get_todos_by_userid_success(
        self, client_with_mock_db, mock_db, sample_todo_list
    ):
        mock_collection = Mock()

        mock_cursor = Mock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.to_list = AsyncMock(return_value=sample_todo_list)

        mock_collection.find = Mock(return_value=mock_cursor)
        mock_db.todos = mock_collection

        response = await client_with_mock_db.get("/api/v1/todos?email=test@example.com")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["data"], list)
        assert len(data["data"]) == len(sample_todo_list)

    @pytest.mark.asyncio
    async def test_get_todos_by_userid_no_todos(self, client_with_mock_db, mock_db):
        mock_collection = Mock()

        mock_cursor = Mock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.to_list = AsyncMock(return_value=[])

        mock_collection.find = Mock(return_value=mock_cursor)
        mock_db.todos = mock_collection

        response = await client_with_mock_db.get("/api/v1/todos?email=test@example.com")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_todo_success(self, client_with_mock_db, mock_db):
        mock_collection = AsyncMock()
        mock_collection.insert_one = AsyncMock()
        mock_db.todos = mock_collection

        payload = {
            "title": "Test Todo",
            "description": "Test description",
            "priority": "High",
            "email": "test@example.com",
            "due_date": "2025-12-30",
        }

        response = await client_with_mock_db.post("/api/v1/todos/create", json=payload)

        assert response.status_code == 201
        assert response.json()["status"] == "success"

    @pytest.mark.asyncio
    async def test_create_todo_missing_title(self, client_with_mock_db):
        payload = {
            "description": "No title",
            "priority": "Low",
            "email": "test@example.com",
            "due_date": "2025-12-30",
        }

        response = await client_with_mock_db.post("/api/v1/todos/create", json=payload)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_todo_invalid_priority(self, client_with_mock_db):
        payload = {
            "title": "Invalid priority",
            "priority": "high",
            "email": "test@example.com",
            "due_date": "2025-12-30",
        }

        response = await client_with_mock_db.post("/api/v1/todos/create", json=payload)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_delete_todo_success(self, client_with_mock_db, mock_db):
        mock_collection = AsyncMock()
        result = AsyncMock()
        result.modified_count = 1

        mock_collection.update_one = AsyncMock(return_value=result)
        mock_db.todos = mock_collection

        todo_id = str(ObjectId())

        response = await client_with_mock_db.delete(f"/api/v1/todos?todo_id={todo_id}")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_todo_not_found(self, client_with_mock_db, mock_db):
        mock_collection = AsyncMock()
        result = AsyncMock()
        result.modified_count = 0

        mock_collection.update_one = AsyncMock(return_value=result)
        mock_db.todos = mock_collection

        todo_id = str(ObjectId())

        response = await client_with_mock_db.delete(f"/api/v1/todos?todo_id={todo_id}")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_complete_todo_success(self, client_with_mock_db, mock_db):
        mock_collection = AsyncMock()
        result = AsyncMock()
        result.modified_count = 1

        mock_collection.update_one = AsyncMock(return_value=result)
        mock_db.todos = mock_collection

        todo_id = str(ObjectId())

        response = await client_with_mock_db.put(
            f"/api/v1/todos/complete?todo_id={todo_id}"
        )

        assert response.status_code == 200

        body = response.json()
        assert body["status"] == "success"
        assert body["message"] == "Todo marked as completed"

        mock_collection.update_one.assert_awaited_once_with(
            {"_id": ObjectId(todo_id)},
            {"$set": {"completed": True}},
        )

    @pytest.mark.asyncio
    async def test_complete_todo_not_found(self, client_with_mock_db, mock_db):
        mock_collection = AsyncMock()
        result = AsyncMock()
        result.modified_count = 0

        mock_collection.update_one = AsyncMock(return_value=result)
        mock_db.todos = mock_collection

        todo_id = str(ObjectId())

        response = await client_with_mock_db.put(
            f"/api/v1/todos/complete?todo_id={todo_id}"
        )

        assert response.status_code == 404

        body = response.json()
        assert body["status"] == "failed"
        assert body["message"] == "Todo not found"

    @pytest.mark.asyncio
    async def test_complete_todo_invalid_object_id(self, client_with_mock_db, mock_db):
        mock_collection = AsyncMock()
        mock_db.todos = mock_collection

        invalid_todo_id = "not-a-valid-object-id"

        response = await client_with_mock_db.put(
            f"/api/v1/todos/complete?todo_id={invalid_todo_id}"
        )

        assert response.status_code == 500

        body = response.json()
        assert body["status"] == "failed"

    @pytest.mark.asyncio
    async def test_complete_todo_db_exception(self, client_with_mock_db, mock_db):
        mock_collection = AsyncMock()
        mock_collection.update_one = AsyncMock(side_effect=Exception("DB failure"))
        mock_db.todos = mock_collection

        todo_id = str(ObjectId())

        response = await client_with_mock_db.put(
            f"/api/v1/todos/complete?todo_id={todo_id}"
        )

        assert response.status_code == 500

        body = response.json()
        assert body["status"] == "failed"
        assert "DB failure" in body["message"]

