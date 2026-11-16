"""Pruebas de integración del portal y de los permisos efectivos de CodeBuild."""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

root = Path(__file__).resolve().parents[2]
url = os.environ["PORTAL_URL"].rstrip("/")
release = json.loads((root / "release.json").read_text(encoding="utf-8"))


def aws(*args):
    return subprocess.run(
        ["aws", *args, "--no-cli-pager", "--output", "json"],
        check=False,
        capture_output=True,
        text=True,
        timeout=25,
    )


def query(*args):
    result = aws(*args)
    if result.returncode:
        raise RuntimeError(result.stderr)
    return json.loads(result.stdout)


with urlopen(f"{url}/health", timeout=15) as response:
    payload = json.load(response)
    assert payload == {"status": "ok", "version": release["version"]}, payload
    assert response.headers["X-Portal-Revision"] == release["revision"]
print(f"T01 OK: /health confirma {release['version']} @ {release['revision']}")

with urlopen(f"{url}/api/services", timeout=15) as response:
    payload = json.load(response)
    checks = payload["services"]
    assert {item["name"] for item in checks} == {"GitHub API", "PyPI", "Python.org", "AWS"}
    assert all(item["url"].startswith("https://") for item in checks)
    assert all(item["status"] in {"Operativo", "No disponible"} for item in checks)
    assert all(isinstance(item["latency_ms"], int) and item["latency_ms"] >= 0 for item in checks)
    assert all(
        datetime.fromisoformat(item["checked_at"]).utcoffset() is not None for item in checks
    )
    assert payload["summary"] == {
        "operational": sum(item["status"] == "Operativo" for item in checks),
        "total": 4,
    }
    assert payload["version"] == release["version"]
with urlopen(url, timeout=15) as response:
    assert "Portal de Monitoreo de Servicios TI" in response.read().decode()
with urlopen(f"{url}/static/styles.css", timeout=15) as response:
    assert response.headers["Content-Type"].startswith("text/css")
print("T02 OK: interfaz, CSS, contrato de API y resultados de cuatro servicios")

routes = query("apigatewayv2", "get-routes", "--api-id", os.environ["PORTAL_API_ID"])
assert {item["RouteKey"] for item in routes["Items"]} == {
    "GET /",
    "GET /health",
    "GET /api/services",
    "GET /static/{proxy+}",
}
for method, path in [("POST", "/health"), ("GET", "/docs"), ("GET", "/openapi.json")]:
    try:
        with urlopen(Request(f"{url}{path}", method=method), timeout=10):
            raise AssertionError(f"{method} {path} expuesto")
    except HTTPError as exc:
        assert exc.code == 404, (method, path, exc.code)
function = os.environ["PORTAL_FUNCTION"]
function_config = query("lambda", "get-function-configuration", "--function-name", function)
assert function_config["Environment"]["Variables"]["APP_REVISION"] == release["revision"]
assert function_config["LoggingConfig"]["LogFormat"] == "JSON"
assert (
    query("lambda", "list-function-url-configs", "--function-name", function)["FunctionUrlConfigs"]
    == []
)
print("S03 OK: solo rutas GET explícitas, sin URL directa Lambda y con logging JSON")

denied = aws("s3api", "list-objects-v2", "--bucket", os.environ["AUDIT_BUCKET"], "--max-keys", "1")
assert denied.returncode != 0 and "AccessDenied" in denied.stderr, denied.stderr
print("S01 OK: AWS devuelve AccessDenied al rol de pruebas sobre el bucket de auditoría")
