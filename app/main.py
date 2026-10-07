import os
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import FastAPI
from fastapi import Request as FastAPIRequest
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent
TIMEOUT_SECONDS = 3

app = FastAPI(
    title="Portal de Monitoreo de Servicios TI",
    version=os.getenv("APP_VERSION", "dev"),
    description=(
        "Aplicación académica que comprueba la disponibilidad de servicios "
        "externos mediante solicitudes HTTP y demuestra un flujo DevOps CI/CD en AWS."
    ),
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

SERVICE_TARGETS = [
    {
        "name": "GitHub API",
        "description": "Repositorio y automatización CI/CD del proyecto.",
        "url": "https://api.github.com",
    },
    {
        "name": "PyPI",
        "description": "Registro desde donde se obtienen dependencias Python.",
        "url": "https://pypi.org/pypi/fastapi/json",
    },
    {
        "name": "Python.org",
        "description": "Sitio oficial del lenguaje utilizado por la aplicación.",
        "url": "https://www.python.org/",
    },
    {
        "name": "AWS",
        "description": "Proveedor Cloud donde se ejecuta el contenedor.",
        "url": "https://aws.amazon.com/",
    },
]


def current_version() -> str:
    return os.getenv("APP_VERSION", "dev")


def deployed_at() -> str:
    value = os.getenv("DEPLOYED_AT")
    if value:
        return value
    return datetime.now(UTC).isoformat(timespec="seconds")


def probe_service(service: dict[str, str]) -> dict[str, object]:
    started = time.perf_counter()
    checked_at = datetime.now(UTC).isoformat(timespec="seconds")
    request = Request(
        service["url"],
        headers={"User-Agent": "it-services-status-portal/1.2"},
        method="GET",
    )

    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            code = response.status
        latency_ms = round((time.perf_counter() - started) * 1000)
        status = "Operativo" if 200 <= code < 400 else "No disponible"
        return {
            **service,
            "status": status,
            "http_code": code,
            "latency_ms": latency_ms,
            "checked_at": checked_at,
            "detail": f"Respuesta HTTP {code}",
        }
    except HTTPError as exc:
        latency_ms = round((time.perf_counter() - started) * 1000)
        return {
            **service,
            "status": "No disponible",
            "http_code": exc.code,
            "latency_ms": latency_ms,
            "checked_at": checked_at,
            "detail": f"Respuesta HTTP {exc.code}",
        }
    except (URLError, TimeoutError, OSError) as exc:
        latency_ms = round((time.perf_counter() - started) * 1000)
        return {
            **service,
            "status": "No disponible",
            "http_code": None,
            "latency_ms": latency_ms,
            "checked_at": checked_at,
            "detail": f"Sin respuesta: {type(exc).__name__}",
        }


def monitor_services() -> list[dict[str, object]]:
    with ThreadPoolExecutor(max_workers=len(SERVICE_TARGETS)) as executor:
        return list(executor.map(probe_service, SERVICE_TARGETS))


def service_summary(services: list[dict[str, object]]) -> dict[str, int]:
    operational = sum(service["status"] == "Operativo" for service in services)
    return {"operational": operational, "total": len(services)}


@app.get("/", response_class=HTMLResponse)
def index(request: FastAPIRequest):
    services = monitor_services()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "services": services,
            "version": current_version(),
            "environment": os.getenv("APP_ENV", "production"),
            "deployed_at": deployed_at(),
            "summary": service_summary(services),
            "timeout_seconds": TIMEOUT_SECONDS,
        },
    )


@app.get("/health")
def health():
    return {"status": "ok", "version": current_version()}


@app.get("/api/services")
def services():
    monitored = monitor_services()
    return {
        "services": monitored,
        "version": current_version(),
        "environment": os.getenv("APP_ENV", "production"),
        "summary": service_summary(monitored),
        "method": "HTTP GET en tiempo real al consultar el endpoint",
        "timeout_seconds": TIMEOUT_SECONDS,
    }
