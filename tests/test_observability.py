import logging
from urllib.error import URLError

from test_app import client, fake_probe

import app.main as portal


def test_health_exposes_deployed_revision(monkeypatch):
    monkeypatch.setenv("APP_REVISION", "test-revision")
    response = client.get("/health")
    assert response.headers["X-Portal-Revision"] == "test-revision"


def test_failure_is_logged_with_target_and_without_exception_details(monkeypatch, caplog):
    def offline(request, timeout):
        assert timeout == 3
        raise URLError("internal-diagnostic")

    monkeypatch.setattr(portal, "urlopen", offline)
    with caplog.at_level(logging.INFO, logger="app.main"):
        payload = client.get("/api/services").json()

    assert payload["summary"] == {"operational": 0, "total": 4}
    assert all(item["detail"] == "Sin respuesta: URLError" for item in payload["services"])
    assert caplog.text.count("service_check unavailable") == 4
    assert "internal-diagnostic" not in caplog.text


def test_successful_probe_is_logged(monkeypatch, caplog):
    monkeypatch.setattr(portal, "probe_service", fake_probe)
    with caplog.at_level(logging.INFO, logger="app.main"):
        client.get("/api/services")
    assert caplog.text.count("service_check available") == 4
