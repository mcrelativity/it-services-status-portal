import app.lambda_entry as entry


def test_scheduled_probe_checks_dependencies(monkeypatch):
    monkeypatch.setattr(entry, "monitor_services", lambda: [{"status": "Operativo"}])
    assert entry.handler({"source": "portal.scheduler"}, None) == {"operational": 1, "total": 1}

