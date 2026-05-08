import pytest
from datetime import datetime


BASE_URL = "/api/v1/users"


class TestCreateUserEndpoint:

    def test_create_user_returns_201(self, client):
        payload = {"username": "newuser"}

        response = client.post(f"{BASE_URL}/", json=payload)

        assert response.status_code == 201
        assert response.json()["username"] == "newuser"
        assert "id" in response.json()
        assert "created_at" in response.json()

    def test_create_user_response_structure(self, client):
        payload = {"username": "testuser"}

        response = client.post(f"{BASE_URL}/", json=payload)

        assert response.status_code == 201
        data = response.json()

        assert isinstance(data["id"], int)
        assert isinstance(data["username"], str)
        assert isinstance(data["created_at"], str)

        assert data["id"] > 0
        assert data["username"] == "testuser"

        datetime.fromisoformat(data["created_at"])

    def test_create_user_invalid_username_short(self, client):
        payload = {"username": "ab"}

        response = client.post(f"{BASE_URL}/", json=payload)

        assert response.status_code == 422
        assert "detail" in response.json()

    def test_create_user_missing_username(self, client):
        payload = {}

        response = client.post(f"{BASE_URL}/", json=payload)

        assert response.status_code == 422

    def test_create_user_duplicate_username(self, client, create_user_factory):
        create_user_factory(username="duplicate")
        payload = {"username": "duplicate"}

        response = client.post(f"{BASE_URL}/", json=payload)

        assert response.status_code == 400
        assert "Unable to create user" in response.json()["detail"]

    def test_create_user_long_username(self, client):
        long_name = "a" * 21
        payload = {"username": long_name}

        response = client.post(f"{BASE_URL}/", json=payload)

        assert response.status_code == 422


class TestGetUserEndpoint:

    def test_get_user_returns_200_or_201(self, client, create_user_factory):
        user = create_user_factory(username="gettest")

        response = client.get(f"{BASE_URL}/{user.id}")

        assert response.status_code in [200, 201]
        assert response.json()["id"] == user.id
        assert response.json()["username"] == "gettest"

    def test_get_user_response_structure(self, client, create_user_factory):
        user = create_user_factory(username="testuser")

        response = client.get(f"{BASE_URL}/{user.id}")

        assert response.status_code in [200, 201]
        data = response.json()

        assert data["id"] == user.id
        assert data["username"] == "testuser"
        assert "created_at" in data

        datetime.fromisoformat(data["created_at"])

    def test_get_user_not_found(self, client):
        non_existent_id = 99999

        response = client.get(f"{BASE_URL}/{non_existent_id}")

        assert response.status_code == 404
        assert "Unable to retrieve user" in response.json()["detail"]

    def test_get_user_invalid_id_format(self, client):
        invalid_id = "abc"

        response = client.get(f"{BASE_URL}/{invalid_id}")

        assert response.status_code == 422

    def test_get_user_negative_id(self, client):
        negative_id = -1

        response = client.get(f"{BASE_URL}/{negative_id}")

        assert response.status_code == 404


class TestUpdateUserEndpoint:

    def test_update_user_returns_200(self, client, create_user_factory):
        user = create_user_factory(username="original")
        payload = {"username": "updated"}

        response = client.post(f"{BASE_URL}/{user.id}", json=payload)

        assert response.status_code == 200
        assert response.json()["username"] == "updated"
        assert response.json()["id"] == user.id

    def test_update_user_response_structure(self, client, create_user_factory):
        user = create_user_factory(username="testupd")
        payload = {"username": "newname"}

        response = client.post(f"{BASE_URL}/{user.id}", json=payload)

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == user.id
        assert data["username"] == "newname"
        assert "updated_at" in data

        datetime.fromisoformat(data["updated_at"])

    def test_update_user_not_found(self, client):
        payload = {"username": "newname"}

        response = client.post(f"{BASE_URL}/99999", json=payload)

        assert response.status_code == 404
        assert "Unable to update user" in response.json()["detail"]

    def test_update_user_invalid_username_short(self, client, create_user_factory):
        user = create_user_factory(username="testshrt")
        payload = {"username": "ab"}

        response = client.post(f"{BASE_URL}/{user.id}", json=payload)

        assert response.status_code == 422

    def test_update_user_duplicate_username(self, client, create_user_factory):
        user1 = create_user_factory(username="user1xxx")
        create_user_factory(username="user2xxx")

        payload = {"username": "user2xxx"}

        response = client.post(f"{BASE_URL}/{user1.id}", json=payload)

        assert response.status_code == 400
        assert "Unable to update user" in response.json()["detail"]

        get_response = client.get(f"{BASE_URL}/{user1.id}")
        assert get_response.json()["username"] == "user1xxx"

    def test_update_user_missing_username(self, client, create_user_factory):
        user = create_user_factory(username="testmiss")
        payload = {}

        response = client.post(f"{BASE_URL}/{user.id}", json=payload)

        assert response.status_code == 422


class TestDeleteUserEndpoint:

    def test_delete_user_returns_204(self, client, create_user_factory):
        user = create_user_factory(username="todelete")

        response = client.delete(f"{BASE_URL}/{user.id}")

        assert response.status_code == 204
        assert response.content == b""

    def test_delete_user_actually_deleted(self, client, create_user_factory):
        user = create_user_factory(username="todelete2")
        user_id = user.id

        delete_response = client.delete(f"{BASE_URL}/{user_id}")

        assert delete_response.status_code == 204

        get_response = client.get(f"{BASE_URL}/{user_id}")
        assert get_response.status_code == 404

    def test_delete_user_not_found(self, client):
        non_existent_id = 99999

        response = client.delete(f"{BASE_URL}/{non_existent_id}")

        assert response.status_code == 404
        assert "Unable to delete user" in response.json()["detail"]

    def test_delete_user_invalid_id_format(self, client):
        invalid_id = "abc"

        response = client.delete(f"{BASE_URL}/{invalid_id}")

        assert response.status_code == 422

    def test_delete_user_negative_id(self, client):
        negative_id = -1

        response = client.delete(f"{BASE_URL}/{negative_id}")

        assert response.status_code == 404
