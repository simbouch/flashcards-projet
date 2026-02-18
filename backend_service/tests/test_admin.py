import pytest


pytestmark = [pytest.mark.admin, pytest.mark.integration]


def _login_and_get_token(client, username: str, password: str) -> str:
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": password},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_admin_routes_forbidden_for_non_admin(client, test_user):
    token = _login_and_get_token(client, test_user.username, "Password123")
    resp = client.get(
        "/api/v1/admin/stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


def test_admin_stats_ok_for_admin(client, db_session):
    from db_module import crud, schemas, models

    admin_in = schemas.UserCreate(
        email="admin@example.com",
        username="adminuser",
        password="Password123",
        full_name="Admin User",
    )
    admin = crud.create_user_with_role(db_session, admin_in, role=models.UserRole.ADMIN.value)

    token = _login_and_get_token(client, admin.username, "Password123")
    resp = client.get(
        "/api/v1/admin/stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "users_total" in data
    assert "admins_total" in data


def test_admin_can_promote_user_and_reset_password(client, db_session, test_user):
    from db_module import crud, schemas, models

    admin_in = schemas.UserCreate(
        email="admin2@example.com",
        username="adminuser2",
        password="Password123",
        full_name="Admin User 2",
    )
    admin = crud.create_user_with_role(db_session, admin_in, role=models.UserRole.ADMIN.value)
    token = _login_and_get_token(client, admin.username, "Password123")

    # Promote test_user
    resp = client.patch(
        f"/api/v1/admin/users/{test_user.id}",
        json={"role": "admin"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["role"] == "admin"

    # Reset password
    resp = client.post(
        f"/api/v1/admin/users/{test_user.id}/reset-password",
        json={"password": "Newpass123"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200

    # Login with new password works
    token2 = _login_and_get_token(client, test_user.username, "Newpass123")
    assert isinstance(token2, str) and len(token2) > 10


def test_admin_cannot_demote_self(client, db_session):
    from db_module import crud, schemas, models

    admin_in = schemas.UserCreate(
        email="admin3@example.com",
        username="adminuser3",
        password="Password123",
        full_name="Admin User 3",
    )
    admin = crud.create_user_with_role(db_session, admin_in, role=models.UserRole.ADMIN.value)
    token = _login_and_get_token(client, admin.username, "Password123")

    resp = client.patch(
        f"/api/v1/admin/users/{admin.id}",
        json={"role": "user"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400
