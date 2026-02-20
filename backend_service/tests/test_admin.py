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


def test_admin_cannot_modify_or_delete_system_user(client, db_session):
    from db_module import crud, schemas, models
    import uuid

    # Create an admin
    admin_in = schemas.UserCreate(
        email="admin_sys@example.com",
        username="adminsys",
        password="Password123",
        full_name="Admin",
    )
    admin = crud.create_user_with_role(db_session, admin_in, role=models.UserRole.ADMIN.value)
    token = _login_and_get_token(client, admin.username, "Password123")

    # Create a system user directly (bypassing role validation on create_user_with_role)
    system_user = models.User(
        id=str(uuid.uuid4()),
        email="system@example.com",
        username="system",
        full_name="System User",
        hashed_password=crud.get_password_hash("SomePassword123"),
        role="system",
        is_active=False,
    )
    db_session.add(system_user)
    db_session.commit()

    # Update forbidden
    resp = client.patch(
        f"/api/v1/admin/users/{system_user.id}",
        json={"full_name": "Nope"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400

    # Reset password forbidden
    resp = client.post(
        f"/api/v1/admin/users/{system_user.id}/reset-password",
        json={"password": "Newpass123"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400

    # Delete forbidden
    resp = client.delete(
        f"/api/v1/admin/users/{system_user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400


def test_admin_can_create_user_with_role_and_status(client, db_session):
    from db_module import crud, schemas, models

    admin_in = schemas.UserCreate(
        email="admin_create@example.com",
        username="admincreate",
        password="Password123",
        full_name="Admin",
    )
    admin = crud.create_user_with_role(db_session, admin_in, role=models.UserRole.ADMIN.value)
    token = _login_and_get_token(client, admin.username, "Password123")

    resp = client.post(
        "/api/v1/admin/users",
        json={
            "email": "inactive_user@example.com",
            "username": "inactive_user",
            "password": "Password123",
            "full_name": "Inactive User",
            "role": "user",
            "is_active": False,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "inactive_user"
    assert data["role"] == "user"
    assert data["is_active"] is False

    # Inactive users cannot login
    resp2 = client.post(
        "/api/v1/auth/login",
        data={"username": "inactive_user", "password": "Password123"},
    )
    assert resp2.status_code == 403


def test_admin_can_update_username(client, db_session, test_user):
    from db_module import crud, schemas, models

    admin_in = schemas.UserCreate(
        email="admin_update_username@example.com",
        username="adminupd",
        password="Password123",
        full_name="Admin",
    )
    admin = crud.create_user_with_role(db_session, admin_in, role=models.UserRole.ADMIN.value)
    token = _login_and_get_token(client, admin.username, "Password123")

    resp = client.patch(
        f"/api/v1/admin/users/{test_user.id}",
        json={"username": "renamed_user"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["username"] == "renamed_user"

    token2 = _login_and_get_token(client, "renamed_user", "Password123")
    assert isinstance(token2, str) and len(token2) > 10


def test_admin_cannot_set_username_to_system(client, db_session, test_user):
    from db_module import crud, schemas, models

    admin_in = schemas.UserCreate(
        email="admin_no_system@example.com",
        username="adminnosys",
        password="Password123",
        full_name="Admin",
    )
    admin = crud.create_user_with_role(db_session, admin_in, role=models.UserRole.ADMIN.value)
    token = _login_and_get_token(client, admin.username, "Password123")

    resp = client.patch(
        f"/api/v1/admin/users/{test_user.id}",
        json={"username": "system"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400


def test_admin_username_conflict_returns_400(client, db_session, test_user):
    from db_module import crud, schemas, models

    admin_in = schemas.UserCreate(
        email="admin_conflict@example.com",
        username="adminconflict",
        password="Password123",
        full_name="Admin",
    )
    admin = crud.create_user_with_role(db_session, admin_in, role=models.UserRole.ADMIN.value)
    token = _login_and_get_token(client, admin.username, "Password123")

    other_in = schemas.UserCreate(
        email="other_user@example.com",
        username="otheruser",
        password="Password123",
        full_name="Other",
    )
    other = crud.create_user(db_session, other_in)

    resp = client.patch(
        f"/api/v1/admin/users/{test_user.id}",
        json={"username": other.username},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400


def test_admin_create_duplicate_username_returns_400(client, db_session):
    from db_module import crud, schemas, models

    admin_in = schemas.UserCreate(
        email="admin_dup@example.com",
        username="admindup",
        password="Password123",
        full_name="Admin",
    )
    admin = crud.create_user_with_role(db_session, admin_in, role=models.UserRole.ADMIN.value)
    token = _login_and_get_token(client, admin.username, "Password123")

    payload = {
        "email": "dup1@example.com",
        "username": "dupuser",
        "password": "Password123",
        "full_name": "Dup 1",
        "role": "user",
        "is_active": True,
    }
    resp1 = client.post(
        "/api/v1/admin/users",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp1.status_code == 201

    payload2 = dict(payload)
    payload2["email"] = "dup2@example.com"
    resp2 = client.post(
        "/api/v1/admin/users",
        json=payload2,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp2.status_code == 400
