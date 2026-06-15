from datetime import date


def test_resumen_sin_autenticacion(client):
    resp = client.get("/api/v1/estadisticas/resumen")
    assert resp.status_code == 401


def test_resumen_como_cliente_es_rechazado(client, cliente_headers):
    resp = client.get("/api/v1/estadisticas/resumen", headers=cliente_headers)
    assert resp.status_code == 403


def test_resumen_como_admin(client, admin_headers):
    resp = client.get("/api/v1/estadisticas/resumen", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "ventas_hoy" in data
    assert "ticket_promedio" in data
    assert "pedidos_activos" in data
    assert "ingresos_mes_actual" in data


def test_productos_top(client, admin_headers):
    resp = client.get("/api/v1/estadisticas/productos-top", headers=admin_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_pedidos_por_estado(client, admin_headers):
    resp = client.get("/api/v1/estadisticas/pedidos-por-estado", headers=admin_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_ingresos_por_forma_pago(client, admin_headers):
    desde = date.today().replace(day=1).isoformat()
    hasta = date.today().isoformat()
    resp = client.get(
        "/api/v1/estadisticas/ingresos",
        headers=admin_headers,
        params={"desde": desde, "hasta": hasta},
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_ventas_agrupacion_invalida(client, admin_headers):
    resp = client.get(
        "/api/v1/estadisticas/ventas",
        headers=admin_headers,
        params={"agrupacion": "semana_invalida"},
    )
    assert resp.status_code == 422


def test_ventas_rango_fechas_invalido(client, admin_headers):
    resp = client.get(
        "/api/v1/estadisticas/ventas",
        headers=admin_headers,
        params={"desde": "2024-12-31", "hasta": "2024-01-01"},
    )
    assert resp.status_code == 422


def test_ventas_periodo_exitoso(client, admin_headers):
    desde = date.today().replace(day=1).isoformat()
    hasta = date.today().isoformat()
    resp = client.get(
        "/api/v1/estadisticas/ventas",
        headers=admin_headers,
        params={"desde": desde, "hasta": hasta, "agrupacion": "day"},
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
