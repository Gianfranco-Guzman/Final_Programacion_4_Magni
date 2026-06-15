import io


def test_subir_imagen_sin_autenticacion(client):
    content = io.BytesIO(b"fake image data")
    resp = client.post(
        "/api/v1/uploads/imagen",
        files={"file": ("test.jpg", content, "image/jpeg")},
    )
    assert resp.status_code == 401


def test_subir_imagen_como_cliente_es_rechazado(client, cliente_headers):
    content = io.BytesIO(b"fake image data")
    resp = client.post(
        "/api/v1/uploads/imagen",
        headers=cliente_headers,
        files={"file": ("test.jpg", content, "image/jpeg")},
    )
    assert resp.status_code == 403


def test_subir_imagen_formato_invalido(client, admin_headers):
    content = io.BytesIO(b"GIF89a fake gif data")
    resp = client.post(
        "/api/v1/uploads/imagen",
        headers=admin_headers,
        files={"file": ("test.gif", content, "image/gif")},
    )
    assert resp.status_code == 400
    assert "formato" in resp.json()["detail"].lower()


def test_subir_imagen_vacia(client, admin_headers):
    content = io.BytesIO(b"")
    resp = client.post(
        "/api/v1/uploads/imagen",
        headers=admin_headers,
        files={"file": ("test.jpg", content, "image/jpeg")},
    )
    assert resp.status_code == 400


def test_subir_imagen_sin_cloudinary_configurado(client, admin_headers):
    content = io.BytesIO(b"fake jpeg content" * 50)
    resp = client.post(
        "/api/v1/uploads/imagen",
        headers=admin_headers,
        files={"file": ("test.jpg", content, "image/jpeg")},
    )
    assert resp.status_code == 500
    assert "Cloudinary" in resp.json()["detail"]


def test_eliminar_imagen_sin_autenticacion(client):
    resp = client.delete("/api/v1/uploads/imagen/test/public_id")
    assert resp.status_code == 401


def test_eliminar_imagen_sin_cloudinary_configurado(client, admin_headers):
    resp = client.delete("/api/v1/uploads/imagen/test/public_id", headers=admin_headers)
    assert resp.status_code == 500
