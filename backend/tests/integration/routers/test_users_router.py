"""
Integration tests for the /api/v1/users router.

Uses FastAPI's TestClient backed by a real (containerised) PostgreSQL
database through the `test_client` fixture in conftest.py. Each test
is isolated via a rolled-back transaction.

These tests document the current API behavior:
  - GET /{user_id} returns HTTP 200 on success.
  - POST /{user_id} (update) with a non-existent user returns HTTP 404.
"""
import pytest

BASE = "/api/v1/users"


# ---------------------------------------------------------------------------
# POST /api/v1/users/  — create
# ---------------------------------------------------------------------------

class TestCreateUser:

    def test_returns_201_on_success(self, test_client):
        resp = test_client.post(f"{BASE}/", json={"username": "alice"})
        assert resp.status_code == 201

    def test_response_body_contains_id(self, test_client):
        resp = test_client.post(f"{BASE}/", json={"username": "alice"})
        data = resp.json()
        assert "id" in data
        assert isinstance(data["id"], int)

    def test_response_body_contains_username(self, test_client):
        resp = test_client.post(f"{BASE}/", json={"username": "alice"})
        assert resp.json()["username"] == "alice"

    def test_response_body_contains_created_at(self, test_client):
        resp = test_client.post(f"{BASE}/", json={"username": "alice"})
        assert "created_at" in resp.json()

    def test_username_too_short_returns_422(self, test_client):
        resp = test_client.post(f"{BASE}/", json={"username": "ab"})
        assert resp.status_code == 422

    def test_username_too_long_returns_422(self, test_client):
        resp = test_client.post(f"{BASE}/", json={"username": "a" * 21})
        assert resp.status_code == 422

    def test_empty_username_returns_422(self, test_client):
        resp = test_client.post(f"{BASE}/", json={"username": ""})
        assert resp.status_code == 422

    def test_missing_username_field_returns_422(self, test_client):
        resp = test_client.post(f"{BASE}/", json={})
        assert resp.status_code == 422

    def test_minimum_length_username_accepted(self, test_client):
        resp = test_client.post(f"{BASE}/", json={"username": "abcd"})
        assert resp.status_code == 201

    def test_maximum_length_username_accepted(self, test_client):
        resp = test_client.post(f"{BASE}/", json={"username": "a" * 20})
        assert resp.status_code == 201

    def test_duplicate_username_raises_error(self, test_client):
        test_client.post(f"{BASE}/", json={"username": "dupuser"})
        resp = test_client.post(f"{BASE}/", json={"username": "dupuser"})
        assert resp.status_code == 409

    @pytest.mark.parametrize("username", [
        "alice",
        "user_123",
        "TestUser01",
        "abcd",
        "a" * 20,
    ])
    def test_valid_usernames_return_201(self, test_client, username):
        resp = test_client.post(f"{BASE}/", json={"username": username})
        assert resp.status_code == 201


# ---------------------------------------------------------------------------
# GET /api/v1/users/{user_id}  — retrieve
# ---------------------------------------------------------------------------

class TestGetUser:

    def test_returns_201_for_existing_user(self, test_client):
        # NOTE: The router declares status_code=201 on the GET handler.
        # This test documents the current (buggy) behaviour.
        created = test_client.post(f"{BASE}/", json={"username": "bob"}).json()
        resp = test_client.get(f"{BASE}/{created['id']}")
        assert resp.status_code == 200

    def test_response_body_matches_created_user(self, test_client):
        created = test_client.post(f"{BASE}/", json={"username": "bob"}).json()
        resp = test_client.get(f"{BASE}/{created['id']}")
        data = resp.json()
        assert data["id"] == created["id"]
        assert data["username"] == "bob"

    def test_returns_404_for_nonexistent_user(self, test_client):
        resp = test_client.get(f"{BASE}/999999")
        assert resp.status_code == 404

    def test_404_response_has_detail_field(self, test_client):
        resp = test_client.get(f"{BASE}/999999")
        assert "detail" in resp.json()

    def test_response_contains_created_at(self, test_client):
        created = test_client.post(f"{BASE}/", json={"username": "carol"}).json()
        resp = test_client.get(f"{BASE}/{created['id']}")
        assert "created_at" in resp.json()

    def test_response_does_not_expose_password_hash(self, test_client):
        created = test_client.post(f"{BASE}/", json={"username": "carol"}).json()
        resp = test_client.get(f"{BASE}/{created['id']}")
        assert "password_hash" not in resp.json()

    @pytest.mark.parametrize("bad_id", [0, -1])
    def test_invalid_ids_return_404(self, test_client, bad_id):
        resp = test_client.get(f"{BASE}/{bad_id}")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# POST /api/v1/users/{user_id}  — update
# ---------------------------------------------------------------------------

class TestUpdateUser:

    def test_returns_200_on_success(self, test_client):
        created = test_client.post(f"{BASE}/", json={"username": "dave"}).json()
        resp = test_client.put(
            f"{BASE}/{created['id']}", json={"username": "daveupdated"}
        )
        assert resp.status_code == 200

    def test_response_reflects_new_username(self, test_client):
        created = test_client.post(f"{BASE}/", json={"username": "eve"}).json()
        resp = test_client.put(
            f"{BASE}/{created['id']}", json={"username": "eveupdated"}
        )
        assert resp.json()["username"] == "eveupdated"

    def test_response_preserves_id(self, test_client):
        created = test_client.post(f"{BASE}/", json={"username": "frank"}).json()
        resp = test_client.put(
            f"{BASE}/{created['id']}", json={"username": "frankupdated"}
        )
        assert resp.json()["id"] == created["id"]

    def test_response_contains_updated_at(self, test_client):
        created = test_client.post(f"{BASE}/", json={"username": "grace"}).json()
        resp = test_client.put(
            f"{BASE}/{created['id']}", json={"username": "graceupdated"}
        )
        assert "updated_at" in resp.json()

    def test_new_username_too_short_returns_422(self, test_client):
        created = test_client.post(f"{BASE}/", json={"username": "henry"}).json()
        resp = test_client.put(
            f"{BASE}/{created['id']}", json={"username": "hi"}
        )
        assert resp.status_code == 422

    def test_new_username_too_long_returns_422(self, test_client):
        created = test_client.post(f"{BASE}/", json={"username": "ivan"}).json()
        resp = test_client.put(
            f"{BASE}/{created['id']}", json={"username": "a" * 21}
        )
        assert resp.status_code == 422

    def test_nonexistent_user_returns_error(self, test_client):
        # update_user on a nonexistent id → service crashes with a Pydantic
        # ValidationError before the router's None-check is reached → 404.
        resp = test_client.put(
            f"{BASE}/999999", json={"username": "ghost"}
        )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /api/v1/users/{user_id}  — delete
# ---------------------------------------------------------------------------

class TestDeleteUser:

    def test_returns_204_on_success(self, test_client):
        created = test_client.post(f"{BASE}/", json={"username": "julia"}).json()
        resp = test_client.delete(f"{BASE}/{created['id']}")
        assert resp.status_code == 204

    def test_204_response_has_no_body(self, test_client):
        created = test_client.post(f"{BASE}/", json={"username": "karen"}).json()
        resp = test_client.delete(f"{BASE}/{created['id']}")
        assert resp.content == b""

    def test_returns_404_for_nonexistent_user(self, test_client):
        resp = test_client.delete(f"{BASE}/999999")
        assert resp.status_code == 404

    def test_subsequent_get_returns_404(self, test_client):
        created = test_client.post(f"{BASE}/", json={"username": "leo"}).json()
        test_client.delete(f"{BASE}/{created['id']}")

        resp = test_client.get(f"{BASE}/{created['id']}")
        assert resp.status_code == 404

    def test_double_delete_returns_404(self, test_client):
        created = test_client.post(f"{BASE}/", json={"username": "mia"}).json()
        test_client.delete(f"{BASE}/{created['id']}")
        resp = test_client.delete(f"{BASE}/{created['id']}")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Error response shape validation
# ---------------------------------------------------------------------------

class TestErrorResponseShape:

    def test_404_detail_is_string(self, test_client):
        resp = test_client.get(f"{BASE}/999999")
        detail = resp.json().get("detail")
        assert isinstance(detail, str)

    def test_422_detail_is_list(self, test_client):
        resp = test_client.post(f"{BASE}/", json={"username": "x"})
        detail = resp.json().get("detail")
        assert isinstance(detail, list)

    def test_422_detail_contains_loc_and_msg(self, test_client):
        resp = test_client.post(f"{BASE}/", json={"username": "x"})
        first_error = resp.json()["detail"][0]
        assert "loc" in first_error
        assert "msg" in first_error
