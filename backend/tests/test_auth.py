def test_registro_exitoso(client, roles):
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": "nuevo@test.com",
            "password": "NuevaClave1!",
            "nombre": "Nuevo",
            "apellido": "Usuario",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "nuevo@test.com"
    assert data["nombre"] == "Nuevo"


def test_registro_email_duplicado(client, usuario_cliente):
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": "cliente@test.com",
            "password": "NuevaClave1!",
            "nombre": "Otro",
            "apellido": "Cliente",
        },
    )
    assert resp.status_code == 422


def test_login_correcto(client, usuario_cliente):
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "cliente@test.com", "password": "Cliente123!"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "refresh_token" in data


def test_login_credenciales_invalidas(client, usuario_cliente):
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "cliente@test.com", "password": "MalaClave99!"},
    )
    assert resp.status_code == 401


def test_login_usuario_inexistente(client):
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "noexiste@test.com", "password": "CualquierClave1!"},
    )
    assert resp.status_code == 401


def test_me_con_token_valido(client, cliente_headers, usuario_cliente):
    resp = client.get("/api/v1/auth/me", headers=cliente_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "cliente@test.com"
    assert data["is_active"] is True


def test_me_sin_token(client):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401


def test_refresh_token(client, usuario_cliente):
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "cliente@test.com", "password": "Cliente123!"},
    )
    assert login.status_code == 200
    refresh_token = login.json()["refresh_token"]

    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_logout(client, usuario_cliente):
    client.post(
        "/api/v1/auth/login",
        json={"email": "cliente@test.com", "password": "Cliente123!"},
    )
    resp = client.post("/api/v1/auth/logout")
    assert resp.status_code == 200
    assert "cerrada" in resp.json()["message"].lower()
