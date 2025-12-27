
from unittest.mock import AsyncMock, patch

import pytest


class TestUserAPI:

    @pytest.mark.asyncio
    async def test_create_user_success(
        self, client_with_mock_db, mock_db, sample_user_data
    ):
        mock_collection = AsyncMock()

        mock_collection.find_one = AsyncMock(
            side_effect=[
                None,
                {
                    "_id": "new_user_id",
                    "email": sample_user_data["email"],
                    "username": sample_user_data["username"],
                    "password": "hashed_password",
                    "role": "user",
                    "enabled": True,
                    "created_at": "123",
                    "updated_at": "",
                },
            ]
        )

        mock_collection.insert_one = AsyncMock()
        mock_db.users = mock_collection

        with patch(
            "app.utils.auth_utils.hash_password", return_value="hashed_password"
        ):
            response = await client_with_mock_db.post(
                "/api/v1/users", json=sample_user_data
            )

        assert response.status_code == 201

        body = response.json()
        assert body["status"] == "success"
        assert len(body["data"]) == 1
        assert body["data"][0]["id"] == "new_user_id"
        assert "password" not in body["data"][0]

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(
        self, client_with_mock_db, mock_db, sample_user_data
    ):
        mock_collection = AsyncMock()
        mock_collection.find_one = AsyncMock(return_value={"_id": "existing_user_id"})
        mock_db.users = mock_collection
        response = await client_with_mock_db.post(
            "/api/v1/users", json=sample_user_data
        )

        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_get_user_by_email_success(
        self, client_with_mock_db, mock_db, sample_user_document
    ):

        mock_collection = AsyncMock()
        mock_collection.find_one = AsyncMock(return_value=sample_user_document)

        mock_db.users = mock_collection

        response = await client_with_mock_db.get(
            f"/api/v1/users?email={sample_user_document['email']}"
        )

        assert response.status_code == 200
        response_data = response.json()
        assert "data" in response_data
        assert len(response_data["data"]) == 1

        user = response_data["data"][0]

        assert user["email"] == sample_user_document["email"]
        assert user["username"] == sample_user_document["username"]

        assert "password" not in user
        assert "hashed_password" not in user

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, client_with_mock_db, mock_db):
        mock_collection = AsyncMock()
        mock_collection.find_one = AsyncMock(return_value=None)

        mock_db.users = mock_collection

        response = await client_with_mock_db.get(
            "/api/v1/users?email=nonexistent@example.com"
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_user_missing_email_param(self, client_with_mock_db):
        response = await client_with_mock_db.get("/api/v1/users")

        assert response.status_code == 422
