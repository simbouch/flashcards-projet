# Admin & “system” user management

This document explains how **admin accounts** are created/managed, and how the reserved **`system`** account is protected.

## Quick definitions

- **Roles** (see `db_module/models.py`):
  - `user`: normal user
  - `admin`: administrator
- **Reserved account name**:
  - `system` is a *reserved internal username* (it’s not a role).

## Admin accounts

### 1) Initial admin bootstrap (backend startup)

On backend startup (`backend_service/src/main.py`), the function `bootstrap_initial_admin()` runs.
It can create the *first* admin account automatically **only if no admin exists yet**.

Environment variables (see `backend_service/src/config.py`):
- `INITIAL_ADMIN_USERNAME`
- `INITIAL_ADMIN_PASSWORD`
- `INITIAL_ADMIN_EMAIL` (optional)
- `INITIAL_ADMIN_FULL_NAME` (optional)
- `INITIAL_ADMIN_ALLOW_PROMOTE_EXISTING` (default `false`)

Rules (see `backend_service/src/scripts/bootstrap_admin.py`):
- No-op when `TESTING=true`
- If an admin already exists: **no-op**
- `INITIAL_ADMIN_USERNAME=system` is **rejected** (reserved)
- If a user already exists (same username/email):
  - promoted to admin **only if** `INITIAL_ADMIN_ALLOW_PROMOTE_EXISTING=true`
- If creating a brand-new admin: `INITIAL_ADMIN_PASSWORD` must be set

Recommended local-dev pattern:
- Put these variables in your local `.env` (gitignored), not in git.

### 2) Ongoing admin management (API + UI)

Admin-only endpoints are mounted under:
- `GET /api/v1/admin/stats`
- `GET /api/v1/admin/users`
- `POST /api/v1/admin/users` (create user)
- `PATCH /api/v1/admin/users/{user_id}` (update user: role, is_active, etc.)
- `POST /api/v1/admin/users/{user_id}/reset-password`
- `DELETE /api/v1/admin/users/{user_id}`

These endpoints require an authenticated **admin** (`get_current_admin_user`).

Safety rules enforced in `backend_service/src/api/endpoints/admin.py`:
- Admin cannot delete themselves
- Admin cannot deactivate themselves
- Admin cannot change their own role
- You **cannot delete/demote/deactivate the last admin**

## Reserved `system` account

The username `system` is reserved to avoid using it as a normal interactive account.

### What is blocked (by design)

**Login is blocked** (`backend_service/src/api/endpoints/auth.py`):
- `POST /api/v1/auth/login` rejects username `system` with HTTP 403

**Registration is blocked** (`backend_service/src/api/endpoints/auth.py`):
- `POST /api/v1/auth/register` rejects username `system` with HTTP 400

**Admin actions are blocked** (`backend_service/src/api/endpoints/admin.py`):
- cannot create a user with username `system`
- cannot modify `system`
- cannot delete `system`
- cannot reset password for `system`

**Self-delete is blocked** (`backend_service/src/api/endpoints/users.py`):
- `POST /api/v1/users/me/delete` rejects if the current user is `system`

### Practical consequence

- There is **no “system password to keep”** for logging in.
- The `system` username is reserved/protected so it cannot be used as a normal account.

## Recovery checklist (if you lose admin access)

1. Set `INITIAL_ADMIN_USERNAME` in `.env`.
2. If the user already exists and you want to promote them: set `INITIAL_ADMIN_ALLOW_PROMOTE_EXISTING=true`.
3. Restart the backend service.
4. If you need a brand-new admin: also set `INITIAL_ADMIN_PASSWORD`.

