"""
Tests del módulo de autenticación.

Cubre: registro, login, rutas protegidas, RBAC (roles).
"""

import pytest
from fastapi.testclient import TestClient


class TestRegister:
    def test_register_ok(self, client: TestClient):
        r = client.post("/api/v1/auth/register", json={
            "username": "nuevo", "full_name": "Nuevo User",
            "email": "nuevo@example.com", "password": "Password1!",
        })
        assert r.status_code == 201
        data = r.json()
        assert data["username"] == "nuevo"
        assert data["role"] == "user"
        assert "hashed_password" not in data

    def test_register_duplicate_username(self, client: TestClient, usuario_registrado):
        r = client.post("/api/v1/auth/register", json={
            "username": "juanperez", "full_name": "Otro",
            "email": "otro@example.com", "password": "Password1!",
        })
        assert r.status_code == 409

    def test_register_duplicate_email(self, client: TestClient, usuario_registrado):
        r = client.post("/api/v1/auth/register", json={
            "username": "otro", "full_name": "Otro",
            "email": "juan@example.com", "password": "Password1!",
        })
        assert r.status_code == 409

    def test_register_short_password(self, client: TestClient):
        r = client.post("/api/v1/auth/register", json={
            "username": "test", "full_name": "Test",
            "email": "test@example.com", "password": "corta",
        })
        assert r.status_code == 422


class TestLogin:
    def test_login_ok(self, client: TestClient, usuario_registrado):
        r = client.post("/api/v1/auth/token", data={
            "username": "juanperez", "password": "Password123!",
        })
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 1800

    def test_login_wrong_password(self, client: TestClient, usuario_registrado):
        r = client.post("/api/v1/auth/token", data={
            "username": "juanperez", "password": "WRONGPASS!",
        })
        assert r.status_code == 401

    def test_login_nonexistent_user(self, client: TestClient):
        r = client.post("/api/v1/auth/token", data={
            "username": "noexiste", "password": "whatever",
        })
        assert r.status_code == 401


class TestProtectedRoutes:
    def test_me_ok(self, client: TestClient, headers_usuario):
        r = client.get("/api/v1/auth/me", headers=headers_usuario)
        assert r.status_code == 200
        assert r.json()["username"] == "juanperez"

    def test_me_no_token(self, client: TestClient):
        r = client.get("/api/v1/auth/me")
        assert r.status_code == 401

    def test_me_invalid_token(self, client: TestClient):
        r = client.get("/api/v1/auth/me", headers={
            "Authorization": "Bearer token.invalido.falso"
        })
        assert r.status_code == 401

    def test_privado_ok(self, client: TestClient, headers_usuario):
        r = client.get("/api/v1/auth/privado", headers=headers_usuario)
        assert r.status_code == 200
        assert "mensaje" in r.json()


class TestRBAC:
    def test_admin_list_users(self, client: TestClient, headers_admin):
        r = client.get("/api/v1/auth/admin/usuarios", headers=headers_admin)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_user_cannot_list_users(self, client: TestClient, headers_usuario):
        r = client.get("/api/v1/auth/admin/usuarios", headers=headers_usuario)
        assert r.status_code == 403

    def test_admin_deactivate_user(
        self, client: TestClient, headers_admin, usuario_registrado
    ):
        user_id = usuario_registrado["id"]
        r = client.post(
            f"/api/v1/auth/admin/usuarios/{user_id}/desactivar",
            headers=headers_admin,
        )
        assert r.status_code == 200
        assert r.json()["disabled"] is True

    def test_admin_activate_user(
        self, client: TestClient, headers_admin, usuario_registrado
    ):
        user_id = usuario_registrado["id"]
        # Desactivar primero
        client.post(
            f"/api/v1/auth/admin/usuarios/{user_id}/desactivar",
            headers=headers_admin,
        )
        # Reactivar
        r = client.post(
            f"/api/v1/auth/admin/usuarios/{user_id}/activar",
            headers=headers_admin,
        )
        assert r.status_code == 200
        assert r.json()["disabled"] is False
