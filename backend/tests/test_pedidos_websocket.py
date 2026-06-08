import pytest
from starlette.websockets import WebSocketDisconnect

from tests.conftest import auth_cookie_for, create_address, create_order


def test_websocket_rejects_missing_cookie(client):
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/api/v1/pedidos/ws"):
            pass

    assert exc_info.value.code == 1008


def test_client_can_only_subscribe_to_own_orders(
    client,
    session,
    client_user,
    other_client_user,
    catalog_setup,
):
    own_address = create_address(session, client_user.id)
    other_address = create_address(session, other_client_user.id)
    own_order = create_order(
        session,
        user_id=client_user.id,
        direccion_entrega_id=own_address.id,
        forma_pago_id=catalog_setup["forma_pago_id"],
    )
    other_order = create_order(
        session,
        user_id=other_client_user.id,
        direccion_entrega_id=other_address.id,
        forma_pago_id=catalog_setup["forma_pago_id"],
    )

    with client.websocket_connect(
        "/api/v1/pedidos/ws",
        cookies=auth_cookie_for(client_user, ["CLIENT"]),
    ) as websocket:
        websocket.send_json({"action": "subscribe-order", "order_id": own_order.id})
        assert websocket.receive_json()["event"] == "SUBSCRIBED"

        websocket.send_json({"action": "subscribe-order", "order_id": other_order.id})
        error_message = websocket.receive_json()
        assert error_message["event"] == "ERROR"
        assert "No tenés acceso" in error_message["data"]["detail"]


def test_staff_can_subscribe_and_receive_create_event(
    client,
    session,
    client_user,
    staff_user,
    catalog_setup,
):
    address = create_address(session, client_user.id)

    with client.websocket_connect(
        "/api/v1/pedidos/ws",
        cookies=auth_cookie_for(staff_user, ["PEDIDOS"]),
    ) as staff_socket:
        response = client.post(
            "/api/v1/pedidos/",
            json={
                "direccion_entrega_id": address.id,
                "forma_pago_id": catalog_setup["forma_pago_id"],
                "items": [{"producto_id": catalog_setup["producto_id"], "cantidad": 1}],
            },
            cookies=auth_cookie_for(client_user, ["CLIENT"]),
        )

        assert response.status_code == 201
        message = staff_socket.receive_json()
        assert message["event"] == "PEDIDO_CREATED"
        assert message["data"]["pedido"]["id"] == response.json()["id"]


def test_order_subscribers_receive_advance_and_cancel_events(
    client,
    session,
    client_user,
    staff_user,
    catalog_setup,
):
    address = create_address(session, client_user.id)
    order = create_order(
        session,
        user_id=client_user.id,
        direccion_entrega_id=address.id,
        forma_pago_id=catalog_setup["forma_pago_id"],
    )

    with client.websocket_connect(
        "/api/v1/pedidos/ws",
        cookies=auth_cookie_for(client_user, ["CLIENT"]),
    ) as customer_socket:
        customer_socket.send_json({"action": "subscribe-order", "order_id": order.id})
        assert customer_socket.receive_json()["event"] == "SUBSCRIBED"

        advance_response = client.patch(
            f"/api/v1/pedidos/{order.id}/estado",
            json={},
            cookies=auth_cookie_for(staff_user, ["PEDIDOS"]),
        )
        assert advance_response.status_code == 200
        advanced_message = customer_socket.receive_json()
        assert advanced_message["event"] == "PEDIDO_UPDATED"
        assert advanced_message["data"]["pedido"]["estado_actual"] == "CONFIRMADO"

        cancel_response = client.patch(
            f"/api/v1/pedidos/{order.id}/cancelar",
            json={},
            cookies=auth_cookie_for(staff_user, ["PEDIDOS"]),
        )
        assert cancel_response.status_code == 200
        cancelled_message = customer_socket.receive_json()
        assert cancelled_message["event"] == "PEDIDO_CANCELLED"
        assert cancelled_message["data"]["pedido"]["estado_actual"] == "CANCELADO"
