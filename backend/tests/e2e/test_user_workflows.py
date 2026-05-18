"""
End-to-end tests for user workflows.

These tests exercise complete multi-step user journeys through the HTTP API
and then verify the resulting database state using the same `db_session` that
backs the `test_client` fixture.  They confirm that the system behaves
correctly as a whole — not just that individual endpoints return the right
status codes.
"""
import pytest

BASE = "/api/v1/users"


# ---------------------------------------------------------------------------
# Create → Retrieve
# ---------------------------------------------------------------------------

class TestCreateAndRetrieveWorkflow:

    def test_created_user_is_immediately_retrievable(self, test_client):
        post_resp = test_client.post(f"{BASE}/", json={"username": "workflow_user"})
        assert post_resp.status_code == 201
        user_id = post_resp.json()["id"]

        get_resp = test_client.get(f"{BASE}/{user_id}")
        assert get_resp.status_code == 200  # router declares 200 on GET
        assert get_resp.json()["id"] == user_id
        assert get_resp.json()["username"] == "workflow_user"

    def test_retrieved_user_data_matches_creation_payload(self, test_client):
        payload = {"username": "consistency_check"}
        created = test_client.post(f"{BASE}/", json=payload).json()
        fetched = test_client.get(f"{BASE}/{created['id']}").json()

        assert fetched["username"] == payload["username"]
        assert fetched["id"] == created["id"]
        assert fetched["created_at"] == created["created_at"]

    def test_multiple_users_have_distinct_ids(self, test_client):
        ids = set()
        for i in range(5):
            resp = test_client.post(f"{BASE}/", json={"username": f"muser{i:03d}"})
            assert resp.status_code == 201
            ids.add(resp.json()["id"])

        assert len(ids) == 5

    def test_each_user_retrievable_by_own_id(self, test_client):
        users = {}
        for i in range(3):
            username = f"fetch_user{i}"
            resp = test_client.post(f"{BASE}/", json={"username": username}).json()
            users[resp["id"]] = username

        for user_id, expected_username in users.items():
            resp = test_client.get(f"{BASE}/{user_id}")
            assert resp.status_code == 200
            assert resp.json()["username"] == expected_username


# ---------------------------------------------------------------------------
# Create → Update → Retrieve
# ---------------------------------------------------------------------------

class TestCreateUpdateRetrieveWorkflow:

    def test_update_is_reflected_on_subsequent_get(self, test_client):
        created = test_client.post(f"{BASE}/", json={"username": "before_update"}).json()
        test_client.post(
            f"{BASE}/{created['id']}", json={"username": "after_update"}
        )

        fetched = test_client.get(f"{BASE}/{created['id']}").json()
        assert fetched["username"] == "after_update"

    def test_id_is_stable_after_update(self, test_client):
        created = test_client.post(f"{BASE}/", json={"username": "stable_id"}).json()
        original_id = created["id"]

        test_client.post(f"{BASE}/{original_id}", json={"username": "stable_id_v2"})

        fetched = test_client.get(f"{BASE}/{original_id}").json()
        assert fetched["id"] == original_id

    def test_update_does_not_affect_other_users(self, test_client):
        u1 = test_client.post(f"{BASE}/", json={"username": "isolated_one"}).json()
        u2 = test_client.post(f"{BASE}/", json={"username": "isolated_two"}).json()

        test_client.post(f"{BASE}/{u1['id']}", json={"username": "isolated_one_v2"})

        u2_fetched = test_client.get(f"{BASE}/{u2['id']}").json()
        assert u2_fetched["username"] == "isolated_two"

    def test_sequential_updates_keep_latest_value(self, test_client):
        created = test_client.post(f"{BASE}/", json={"username": "seq_update"}).json()
        uid = created["id"]

        test_client.post(f"{BASE}/{uid}", json={"username": "seq_updatev2"})
        test_client.post(f"{BASE}/{uid}", json={"username": "seq_updatev3"})

        fetched = test_client.get(f"{BASE}/{uid}").json()
        assert fetched["username"] == "seq_updatev3"

    def test_updated_at_timestamp_is_present(self, test_client):
        created = test_client.post(f"{BASE}/", json={"username": "ts_user"}).json()
        update_resp = test_client.post(
            f"{BASE}/{created['id']}", json={"username": "ts_user_v2"}
        ).json()

        assert "updated_at" in update_resp
        assert update_resp["updated_at"] is not None


# ---------------------------------------------------------------------------
# Create → Delete → Retrieve
# ---------------------------------------------------------------------------

class TestCreateDeleteWorkflow:

    def test_deleted_user_not_retrievable(self, test_client):
        created = test_client.post(f"{BASE}/", json={"username": "delete_me"}).json()
        uid = created["id"]

        del_resp = test_client.delete(f"{BASE}/{uid}")
        assert del_resp.status_code == 204

        get_resp = test_client.get(f"{BASE}/{uid}")
        assert get_resp.status_code == 404

    def test_delete_returns_no_body(self, test_client):
        created = test_client.post(f"{BASE}/", json={"username": "no_body"}).json()
        resp = test_client.delete(f"{BASE}/{created['id']}")
        assert resp.content == b""

    def test_deleting_one_user_does_not_affect_another(self, test_client):
        u1 = test_client.post(f"{BASE}/", json={"username": "del_u1"}).json()
        u2 = test_client.post(f"{BASE}/", json={"username": "del_u2"}).json()

        test_client.delete(f"{BASE}/{u1['id']}")

        assert test_client.get(f"{BASE}/{u2['id']}").status_code == 200

    def test_re_creating_deleted_username_succeeds(self, test_client):
        # After deletion the unique constraint on username is released.
        created = test_client.post(f"{BASE}/", json={"username": "reuse_name"}).json()
        test_client.delete(f"{BASE}/{created['id']}")

        resp = test_client.post(f"{BASE}/", json={"username": "reuse_name"})
        assert resp.status_code == 201
        assert resp.json()["username"] == "reuse_name"


# ---------------------------------------------------------------------------
# Data consistency — DB state verification
# ---------------------------------------------------------------------------

class TestDatabaseConsistency:

    def test_created_user_exists_in_db(self, test_client, db_session):
        from app.models.user import User

        resp = test_client.post(f"{BASE}/", json={"username": "db_check"}).json()
        db_session.expire_all()

        user_in_db = db_session.query(User).filter_by(id=resp["id"]).first()
        assert user_in_db is not None
        assert user_in_db.username == "db_check"

    def test_deleted_user_absent_from_db(self, test_client, db_session):
        from app.models.user import User

        resp = test_client.post(f"{BASE}/", json={"username": "db_del"}).json()
        uid = resp["id"]
        test_client.delete(f"{BASE}/{uid}")
        db_session.expire_all()

        user_in_db = db_session.query(User).filter_by(id=uid).first()
        assert user_in_db is None

    def test_updated_username_persisted_in_db(self, test_client, db_session):
        from app.models.user import User

        created = test_client.post(f"{BASE}/", json={"username": "db_before"}).json()
        uid = created["id"]
        test_client.post(f"{BASE}/{uid}", json={"username": "db_after"})
        db_session.expire_all()

        user_in_db = db_session.query(User).filter_by(id=uid).first()
        assert user_in_db.username == "db_after"

    def test_username_uniqueness_enforced_in_db(self, test_client, db_session):
        from app.models.user import User

        test_client.post(f"{BASE}/", json={"username": "unique_check"})
        test_client.post(f"{BASE}/", json={"username": "unique_check"})
        db_session.expire_all()

        count = (
            db_session.query(User)
            .filter_by(username="unique_check")
            .count()
        )
        assert count == 1

    def test_default_role_stored_in_db(self, test_client, db_session):
        from app.models.user import User

        resp = test_client.post(f"{BASE}/", json={"username": "role_check"}).json()
        db_session.expire_all()

        user_in_db = db_session.query(User).filter_by(id=resp["id"]).first()
        assert user_in_db.role == "user"


# ---------------------------------------------------------------------------
# Complex relationship workflows
# ---------------------------------------------------------------------------

class TestRelationshipWorkflows:

    def test_user_can_be_added_to_group(self, test_client, db_session):
        from tests.factories import make_group, make_group_user
        from app.models.group_user import GroupUser

        # Create user via API
        resp = test_client.post(f"{BASE}/", json={"username": "group_member"}).json()
        db_session.expire_all()

        from app.models.user import User
        user = db_session.query(User).filter_by(id=resp["id"]).first()

        group = make_group(db_session, name="test_group")
        gu = make_group_user(db_session, user, group, name="gm_alias")

        db_session.refresh(user)
        assert len(user.groups) == 1
        assert user.groups[0].group_id == group.id

    def test_user_with_group_memberships_deleted_cleans_junction(
        self, test_client, db_session
    ):
        from tests.factories import make_group, make_group_user
        from app.models.group_user import GroupUser
        from app.models.user import User

        resp = test_client.post(f"{BASE}/", json={"username": "cleanup_user"}).json()
        uid = resp["id"]
        db_session.expire_all()

        user = db_session.query(User).filter_by(id=uid).first()
        group = make_group(db_session, name="cleanup_group")
        make_group_user(db_session, user, group, name="cleanup_alias")
        db_session.flush()

        # Delete via API
        del_resp = test_client.delete(f"{BASE}/{uid}")
        assert del_resp.status_code == 204
        db_session.expire_all()

        leftover = (
            db_session.query(GroupUser).filter_by(user_id=uid).all()
        )
        assert leftover == []

    def test_candidate_pool_references_album_and_group(self, db_session):
        from tests.factories import make_album, make_group, make_candidate_pool

        album = make_album(db_session, title="Pool Album")
        group = make_group(db_session, name="pool_group")
        cp = make_candidate_pool(db_session, album, group)

        db_session.refresh(cp)
        assert cp.album_id == album.id
        assert cp.group_id == group.id

    def test_group_album_history_composite_key(self, db_session):
        from tests.factories import make_album, make_group, make_group_album_history
        from app.models.group_album_history import GroupAlbumHistory

        album = make_album(db_session, title="History Album")
        group = make_group(db_session, name="history_group")
        gah = make_group_album_history(db_session, group, album, month=3, year=2024)

        stored = (
            db_session.query(GroupAlbumHistory)
            .filter_by(group_id=group.id, album_id=album.id)
            .first()
        )
        assert stored is not None
        assert stored.month == 3
        assert stored.year == 2024
