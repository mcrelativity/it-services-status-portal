import os
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Portal de Estado de Servicios TI",
    version=os.getenv("APP_VERSION", "dev"),
    description="Aplicación académica para demostrar un flujo DevOps CI/CD en AWS.",
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

SERVICES = [
    {"name": "Correo institucional", "status": "Operativo"},
    {"name": "Portal institucional", "status": "Operativo"},
    {"name": "VPN", "status": "Operativo"},
    {"name": "Mesa de ayuda", "status": "Operativo"},
]


def current_version() -> str:
    return os.getenv("APP_VERSION", "dev")


def deployed_at() -> str:
    value = os.getenv("DEPLOYED_AT")
    if value:
        return value
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "services": SERVICES,
            "version": current_version(),
            "environment": os.getenv("APP_ENV", "production"),
            "deployed_at": deployed_at(),
        },
    )


@app.get("/health")
def health():
    return {"status": "ok", "version": current_version()}


@app.get("/api/services")
def services():
    return {
        "services": SERVICES,
        "version": current_version(),
        "environment": os.getenv("APP_ENV", "production"),
    }
