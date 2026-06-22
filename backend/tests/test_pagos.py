def _crear_pedido_mp(client, headers, direccion_id, forma_pago_id, producto_id):
    return client.post(
        "/api/v1/pedidos/",
        json={
            "direccion_entrega_id": direccion_id,
            "forma_pago_id": forma_pago_id,
            "items": [{"producto_id": producto_id, "cantidad": 1}],
        },
        headers=headers,
    )


def test_crear_pago_sin_configuracion_mp(client, cliente_headers, direccion, forma_pago_mp, producto):
    pedido = _crear_pedido_mp(client, cliente_headers, direccion.id, forma_pago_mp.id, producto.id)
    assert pedido.status_code == 201
    pedido_id = pedido.json()["id"]

    resp = client.post(
        "/api/v1/pagos/crear",
        json={
            "pedido_id": pedido_id,
            "token": "test_token",
            "payment_method_id": "visa",
            "payer_email": "cliente@test.com",
            "installments": 1,
        },
        headers=cliente_headers,
    )
    assert resp.status_code in (500, 502)


def test_crear_pago_pedido_no_pendiente(client, cliente_headers, admin_headers, direccion, forma_pago_mp, producto):
    pedido = _crear_pedido_mp(client, cliente_headers, direccion.id, forma_pago_mp.id, producto.id)
    pedido_id = pedido.json()["id"]

    client.patch(f"/api/v1/pedidos/{pedido_id}/estado", headers=admin_headers, json={})

    resp = client.post(
        "/api/v1/pagos/crear",
        json={
            "pedido_id": pedido_id,
            "token": "test_token",
            "payment_method_id": "visa",
            "payer_email": "cliente@test.com",
            "installments": 1,
        },
        headers=cliente_headers,
    )
    assert resp.status_code == 409


def test_crear_pago_pedido_no_mercadopago(client, cliente_headers, direccion, forma_pago_efectivo, producto):
    pedido = client.post(
        "/api/v1/pedidos/",
        json={
            "tipo_entrega": "sucursal",
            "forma_pago_id": forma_pago_efectivo.id,
            "items": [{"producto_id": producto.id, "cantidad": 1}],
        },
        headers=cliente_headers,
    )
    pedido_id = pedido.json()["id"]

    resp = client.post(
        "/api/v1/pagos/crear",
        json={
            "pedido_id": pedido_id,
            "token": "test_token",
            "payment_method_id": "visa",
            "payer_email": "cliente@test.com",
            "installments": 1,
        },
        headers=cliente_headers,
    )
    assert resp.status_code == 422


def test_obtener_pago_no_existente(client, cliente_headers, direccion, forma_pago_mp, producto):
    pedido = _crear_pedido_mp(client, cliente_headers, direccion.id, forma_pago_mp.id, producto.id)
    pedido_id = pedido.json()["id"]

    resp = client.get(f"/api/v1/pagos/{pedido_id}", headers=cliente_headers)
    assert resp.status_code == 404


def test_webhook_topic_no_payment_es_ignorado(client):
    resp = client.post("/api/v1/pagos/webhook?topic=merchant_order")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ignored"


def test_webhook_payment_sin_id_devuelve_400(client):
    resp = client.post("/api/v1/pagos/webhook?topic=payment")
    assert resp.status_code == 400
