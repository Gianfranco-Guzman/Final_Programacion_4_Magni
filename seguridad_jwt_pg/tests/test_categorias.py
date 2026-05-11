"""
Tests del CRUD de Categorías.

Todas las rutas requieren JWT → se usa headers_usuario de conftest.
"""

import pytest
from fastapi.testclient import TestClient


API = "/api/v1/categorias"


class TestCategoriasCRUD:
    def test_create_ok(self, client: TestClient, headers_usuario):
        r = client.post(f"{API}/", json={
            "nombre": "Electrónica", "descripcion": "Dispositivos electrónicos",
        }, headers=headers_usuario)
        assert r.status_code == 201
        data = r.json()
        assert data["nombre"] == "Electrónica"
        assert data["id"] is not None

    def test_create_duplicate_name(self, client: TestClient, headers_usuario):
        client.post(f"{API}/", json={"nombre": "Ropa"}, headers=headers_usuario)
        r = client.post(f"{API}/", json={"nombre": "Ropa"}, headers=headers_usuario)
        assert r.status_code == 409

    def test_create_no_auth(self, client: TestClient):
        r = client.post(f"{API}/", json={"nombre": "Test"})
        assert r.status_code == 401

    def test_list_ok(self, client: TestClient, headers_usuario):
        client.post(f"{API}/", json={"nombre": "Cat1"}, headers=headers_usuario)
        client.post(f"{API}/", json={"nombre": "Cat2"}, headers=headers_usuario)
        r = client.get(f"{API}/", headers=headers_usuario)
        assert r.status_code == 200
        assert len(r.json()) == 2

    def test_get_one_ok(self, client: TestClient, headers_usuario):
        created = client.post(
            f"{API}/", json={"nombre": "Única"}, headers=headers_usuario
        ).json()
        r = client.get(f"{API}/{created['id']}", headers=headers_usuario)
        assert r.status_code == 200
        assert r.json()["nombre"] == "Única"

    def test_get_not_found(self, client: TestClient, headers_usuario):
        r = client.get(f"{API}/999", headers=headers_usuario)
        assert r.status_code == 404

    def test_update_ok(self, client: TestClient, headers_usuario):
        created = client.post(
            f"{API}/", json={"nombre": "Vieja"}, headers=headers_usuario
        ).json()
        r = client.patch(
            f"{API}/{created['id']}",
            json={"nombre": "Nueva"},
            headers=headers_usuario,
        )
        assert r.status_code == 200
        assert r.json()["nombre"] == "Nueva"

    def test_update_not_found(self, client: TestClient, headers_usuario):
        r = client.patch(
            f"{API}/999", json={"nombre": "X"}, headers=headers_usuario
        )
        assert r.status_code == 404

    def test_delete_ok(self, client: TestClient, headers_usuario):
        created = client.post(
            f"{API}/", json={"nombre": "Borrable"}, headers=headers_usuario
        ).json()
        r = client.delete(f"{API}/{created['id']}", headers=headers_usuario)
        assert r.status_code == 204
        # Verificar que ya no existe
        r2 = client.get(f"{API}/{created['id']}", headers=headers_usuario)
        assert r2.status_code == 404

    def test_delete_not_found(self, client: TestClient, headers_usuario):
        r = client.delete(f"{API}/999", headers=headers_usuario)
        assert r.status_code == 404
