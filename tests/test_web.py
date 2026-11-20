"""Pengujian integrasi antarmuka web (Flask test client)."""
import pytest

from src.db import ping
from web.app import app


@pytest.fixture()
def client():
    app.config.update(TESTING=True)
    with app.test_client() as c:
        yield c


def test_halaman_login_tampil(client):
    assert client.get("/login").status_code == 200


def test_tanpa_login_dialihkan(client):
    resp = client.get("/")
    assert resp.status_code in (301, 302)


@pytest.mark.skipif(not ping(), reason="MySQL aplikasi belum siap")
def test_login_admin_dan_dashboard(client):
    resp = client.post("/login", data={"username": "admin", "password": "admin123"})
    assert resp.status_code in (301, 302)
    assert client.get("/").status_code == 200
    assert client.get("/pelanggan").status_code == 200


@pytest.mark.skipif(not ping(), reason="MySQL aplikasi belum siap")
def test_login_pelanggan_tidak_bisa_admin(client):
    client.post("/login", data={"username": "budi", "password": "budi123"})
    resp = client.get("/pelanggan")
    assert resp.status_code in (301, 302)  # dialihkan, bukan 200
