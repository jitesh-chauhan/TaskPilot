from unittest.mock import AsyncMock, patch

import pytest


class TestAuthAPI:

    @pytest.mark.asyncio
    async def test_login_success(
        self,
        client_with_mock_db,
        mock_db,
        sample_user_document,
        mock_password_hash,
    ):
        mock_collection = AsyncMock()
        mock_collection.find_one = AsyncMock(return_value=sample_user_document)

        mock_db.users = mock_collection

        login_data = {
            "email": "test@example.com",
            "password": "securepassword123",
        }

        response = await client_with_mock_db.post("/api/v1/login", json=login_data)

        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        assert isinstance(data["data"], list)
        assert len(data["data"]) == 1
        assert "access_token" in data["data"][0]

    @pytest.mark.asyncio
    async def test_login_user_not_found(self, client_with_mock_db, mock_db):
        mock_collection = AsyncMock()
        mock_collection.find_one = AsyncMock(return_value=None)
        mock_db.users = mock_collection

        login_data = {
            "email": "nonexistent@example.com",
            "password": "password123",
        }

        response = await client_with_mock_db.post("/api/v1/login", json=login_data)

        assert response.status_code == 404
        body = response.json()
        assert body["status"] == "failed"
        assert body["message"] == "User not found"

    @pytest.mark.asyncio
    async def test_login_wrong_password(
        self,
        client_with_mock_db,
        mock_db,
        sample_user_document,
    ):
        mock_collection = AsyncMock()
        mock_collection.find_one = AsyncMock(return_value=sample_user_document)
        mock_db.users = mock_collection

        with patch(
            "app.utils.auth_utils.verify_password",
            return_value=False,
        ):
            login_data = {
                "email": "test@example.com",
                "password": "wrongpassword",
            }

            response = await client_with_mock_db.post(
                "/api/v1/login",
                json=login_data,
            )

        assert response.status_code == 401
        body = response.json()
        assert body["status"] == "failed"
        assert body["message"] == "Incorrect password"

    @pytest.mark.asyncio
    async def test_login_missing_fields(self, client_with_mock_db):
        response = await client_with_mock_db.post(
            "/api/v1/login",
            json={"password": "password123"},
        )
        assert response.status_code == 422

        response = await client_with_mock_db.post(
            "/api/v1/login",
            json={"email": "test@example.com"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_login_invalid_email_format(self, client_with_mock_db):
        login_data = {
            "email": "not-an-email",
            "password": "password123",
        }

        response = await client_with_mock_db.post(
            "/api/v1/login",
            json=login_data,
        )

        assert response.status_code == 422
