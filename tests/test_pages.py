from unittest.mock import AsyncMock

import pytest


class TestPages:

    @pytest.mark.asyncio
    async def test_home_redirect(self, client_with_mock_db):

        response = await client_with_mock_db.get("/", follow_redirects=False)

        assert response.status_code in [200, 307, 308]

    @pytest.mark.asyncio
    async def test_login_page_get(self, client_with_mock_db):
        response = await client_with_mock_db.get("/login")

        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_login_page_post(self, client_with_mock_db):
        response = await client_with_mock_db.post(
            "/login",
            data={"email": "test@example.com", "password": "securepassword123"},
            follow_redirects=False,
        )

        assert response.status_code in [401, 302, 303, 307, 308]

    @pytest.mark.asyncio
    async def test_register_page_get(self, client_with_mock_db):

        response = await client_with_mock_db.get("/register")

        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_home_page_requires_auth(self, client_with_mock_db):

        response = await client_with_mock_db.get("/home", follow_redirects=False)

        assert response.status_code in [307, 308]
        assert "login" in response.headers.get("location", "").lower()

    @pytest.mark.asyncio
    async def test_add_todo_page_get(self, client_with_mock_db):
        response = await client_with_mock_db.get("/add-todo", follow_redirects=False)

        assert response.status_code in [307, 308]
        assert "login" in response.headers.get("location", "").lower()

    @pytest.mark.asyncio
    async def test_delete_todo_page(self, client_with_mock_db, mock_db):
        mock_collection = AsyncMock()
        mock_delete_result = AsyncMock()
        mock_delete_result.deleted_count = 1
        mock_collection.delete_one = AsyncMock(return_value=mock_delete_result)
        mock_db.__getitem__.return_value = mock_collection

        todo_id = "test_todo_123"
        response = await client_with_mock_db.post(
            f"/delete-todo/{todo_id}", follow_redirects=False
        )

        assert response.status_code in [307, 308]

    @pytest.mark.asyncio
    async def test_logout_page(self, client_with_mock_db):
        response = await client_with_mock_db.get("/logout", follow_redirects=False)

        assert response.status_code in [302, 303, 307, 308]
        assert "login" in response.headers.get("location", "").lower()
