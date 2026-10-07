from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint(monkeypatch):
    monkeypatch.setenv("APP_VERSION", "test")
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "test"}


def test_services_endpoint_contains_expected_services():
    response = client.get("/api/services")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["services"]) >= 4
    assert all(item["status"] == "Operativo" for item in payload["services"])


def test_home_page_renders():
    response = client.get("/")
    assert response.status_code == 200
    assert "Portal de Estado de Servicios TI" in response.text


def test_services_summary():
    response = client.get("/api/services")
    assert response.status_code == 200
    summary = response.json()["summary"]
    assert summary["operational"] == 4
    assert summary["total"] == 4
