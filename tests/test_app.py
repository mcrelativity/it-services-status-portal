from fastapi.testclient import TestClient

import app.main as main_module
from app.main import app

client = TestClient(app)


def fake_probe(service):
    return {
        **service,
        "status": "Operativo",
        "http_code": 200,
        "latency_ms": 25,
        "checked_at": "2026-10-07T00:00:00+00:00",
        "detail": "Respuesta HTTP 200",
    }


def test_health_endpoint(monkeypatch):
    monkeypatch.setenv("APP_VERSION", "test")
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "test"}


def test_services_endpoint_reports_live_check_fields(monkeypatch):
    monkeypatch.setattr(main_module, "probe_service", fake_probe)
    response = client.get("/api/services")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["services"]) == 4
    assert payload["summary"] == {"operational": 4, "total": 4}
    assert all(item["http_code"] == 200 for item in payload["services"])
    assert all("latency_ms" in item for item in payload["services"])


def test_home_page_explains_monitoring(monkeypatch):
    monkeypatch.setattr(main_module, "probe_service", fake_probe)
    response = client.get("/")
    assert response.status_code == 200
    assert "Portal de Monitoreo de Servicios TI" in response.text
    assert "¿Cómo funciona?" in response.text
    assert "GitHub API" in response.text


def test_summary_counts_unavailable_services():
    monitored = [
        {"status": "Operativo"},
        {"status": "No disponible"},
        {"status": "Operativo"},
    ]
    assert main_module.service_summary(monitored) == {
        "operational": 2,
        "total": 3,
    }
