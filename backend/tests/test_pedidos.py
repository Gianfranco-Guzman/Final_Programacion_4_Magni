import pytest

from tests.conftest import crear_usuario


def _crear_pedido(client, direccion_id, forma_pago_id, producto_id, headers):
    return client.post(
        "/api/v1/pedidos/",
        json={
            "tipo_entrega": "sucursal",
            "forma_pago_id": forma_pago_id,
            "items": [{"producto_id": producto_id, "cantidad": 1}],
        },
        headers=headers,
    )


def test_crear_pedido_exitoso(client, cliente_headers, direccion, forma_pago_efectivo, producto, usuario_cliente):
    resp = _crear_pedido(client, direccion.id, forma_pago_efectivo.id, producto.id, cliente_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["estado_actual"] == "PENDIENTE"
    assert data["usuario_id"] == usuario_cliente.id
    assert float(data["total"]) > 0


def test_crear_pedido_producto_inexistente(client, cliente_headers, direccion, forma_pago_efectivo):
    resp = client.post(
        "/api/v1/pedidos/",
        json={
            "tipo_entrega": "sucursal",
            "forma_pago_id": forma_pago_efectivo.id,
            "items": [{"producto_id": 99999, "cantidad": 1}],
        },
        headers=cliente_headers,
    )
    assert resp.status_code == 404


def test_crear_pedido_sin_token(client, direccion, forma_pago_efectivo, producto):
    resp = client.post(
        "/api/v1/pedidos/",
        json={
            "direccion_entrega_id": direccion.id,
            "forma_pago_id": forma_pago_efectivo.id,
            "items": [{"producto_id": producto.id, "cantidad": 1}],
        },
    )
    assert resp.status_code == 401


def test_listar_pedidos_cliente_solo_propios(client, cliente_headers, direccion, forma_pago_efectivo, producto):
    _crear_pedido(client, direccion.id, forma_pago_efectivo.id, producto.id, cliente_headers)
    resp = client.get("/api/v1/pedidos/", headers=cliente_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) >= 1


def test_listar_pedidos_admin_ve_todos(client, admin_headers, cliente_headers, direccion, forma_pago_efectivo, producto):
    _crear_pedido(client, direccion.id, forma_pago_efectivo.id, producto.id, cliente_headers)
    resp = client.get("/api/v1/pedidos/", headers=admin_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_obtener_pedido_propio(client, cliente_headers, direccion, forma_pago_efectivo, producto):
    creado = _crear_pedido(client, direccion.id, forma_pago_efectivo.id, producto.id, cliente_headers)
    pedido_id = creado.json()["id"]

    resp = client.get(f"/api/v1/pedidos/{pedido_id}", headers=cliente_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == pedido_id
    assert "detalles" in data
    assert "historial" in data


def test_obtener_pedido_ajeno_como_cliente(client, db, roles, cliente_headers, direccion, forma_pago_efectivo, producto):
    from app.core.security import create_access_token

    otro = crear_usuario(db, "otro@test.com", "Otro12345!", "Otro", "Cliente", [roles["CLIENT"]])
    db.commit()
    otro_headers = {"Authorization": f"Bearer {create_access_token({'sub': str(otro.id), 'roles': ['CLIENT']})}"}

    creado = _crear_pedido(client, direccion.id, forma_pago_efectivo.id, producto.id, cliente_headers)
    pedido_id = creado.json()["id"]

    resp = client.get(f"/api/v1/pedidos/{pedido_id}", headers=otro_headers)
    assert resp.status_code == 403


def test_avanzar_estado_como_admin(client, admin_headers, cliente_headers, direccion, forma_pago_efectivo, producto):
    creado = _crear_pedido(client, direccion.id, forma_pago_efectivo.id, producto.id, cliente_headers)
    pedido_id = creado.json()["id"]

    resp = client.patch(f"/api/v1/pedidos/{pedido_id}/estado", headers=admin_headers, json={})
    assert resp.status_code == 200
    assert resp.json()["estado_actual"] == "CONFIRMADO"


def test_cancelar_pedido_como_cliente(client, cliente_headers, direccion, forma_pago_efectivo, producto):
    creado = _crear_pedido(client, direccion.id, forma_pago_efectivo.id, producto.id, cliente_headers)
    pedido_id = creado.json()["id"]

    resp = client.patch(
        f"/api/v1/pedidos/{pedido_id}/cancelar",
        headers=cliente_headers,
        json={"observacion": "Ya no lo quiero"},
    )
    assert resp.status_code == 200
    assert resp.json()["estado_actual"] == "CANCELADO"


def test_cancelar_pedido_sin_motivo(client, cliente_headers, direccion, forma_pago_efectivo, producto):
    creado = _crear_pedido(client, direccion.id, forma_pago_efectivo.id, producto.id, cliente_headers)
    pedido_id = creado.json()["id"]

    resp = client.patch(
        f"/api/v1/pedidos/{pedido_id}/cancelar",
        headers=cliente_headers,
        json={"observacion": ""},
    )
    assert resp.status_code == 422


def test_websocket_requiere_autenticacion(client):
    with pytest.raises(Exception):
        with client.websocket_connect("/api/v1/pedidos/ws") as ws:
            ws.receive_json()
