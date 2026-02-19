import uuid
from unittest.mock import patch

import pytest


def _login_and_get_token(client, username: str, password: str) -> str:
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": password},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.mark.integration
def test_user_can_self_delete_with_password(client, db_session):
    from db_module import crud, schemas

    suffix = uuid.uuid4().hex
    password = "Password123"
    user_in = schemas.UserCreate(
        email=f"selfdel_{suffix}@example.com",
        username=f"selfdel_{suffix}",
        password=password,
        full_name="Self Delete",
    )
    user = crud.create_user(db_session, user_in)

    token = _login_and_get_token(client, user.username, password)
    resp = client.post(
        "/api/v1/users/me/delete",
        json={"password": password},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 204

    db_session.expire_all()
    assert crud.get_user(db_session, user.id) is None


@pytest.mark.integration
def test_self_delete_rejects_wrong_password(client, db_session):
    from db_module import crud, schemas

    suffix = uuid.uuid4().hex
    password = "Password123"
    user_in = schemas.UserCreate(
        email=f"selfdel2_{suffix}@example.com",
        username=f"selfdel2_{suffix}",
        password=password,
        full_name="Self Delete 2",
    )
    user = crud.create_user(db_session, user_in)

    token = _login_and_get_token(client, user.username, password)
    resp = client.post(
        "/api/v1/users/me/delete",
        json={"password": "WrongPassword123"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Incorrect password"

    db_session.expire_all()
    assert crud.get_user(db_session, user.id) is not None


@pytest.mark.integration
def test_last_admin_cannot_self_delete(client, db_session):
    from db_module import crud, schemas, models

    suffix = uuid.uuid4().hex
    password = "Password123"
    admin_in = schemas.UserCreate(
        email=f"admin_selfdel_{suffix}@example.com",
        username=f"adminselfdel_{suffix}",
        password=password,
        full_name="Admin Self Delete",
    )
    admin = crud.create_user_with_role(db_session, admin_in, role=models.UserRole.ADMIN.value)

    token = _login_and_get_token(client, admin.username, password)

    # Make the test deterministic regardless of other tests that might create admins.
    with patch("db_module.crud.count_admin_users", return_value=1):
        resp = client.post(
            "/api/v1/users/me/delete",
            json={"password": password},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert resp.status_code == 400
    assert resp.json()["detail"] == "Cannot delete the last admin account"

    db_session.expire_all()
    assert crud.get_user(db_session, admin.id) is not None
