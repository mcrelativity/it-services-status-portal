"""Buscar formatos de credenciales AWS en el código de la revisión."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CREDENTIAL = re.compile(
    r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"
    r"|(?im:^\s*(?:export\s+)?aws_(?:secret_access_key|session_token)\s*[:=]\s*['\"]?[A-Za-z0-9/+=]{32,})"
    r"|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE\sKEY-----"
)

for folder in ("app", "tests", "infra", ".github", "scripts"):
    for path in (ROOT / folder).rglob("*"):
        if path.is_file() and path.suffix in (".py", ".yml", ".yaml", ".ps1", ".txt", ".json"):
            if CREDENTIAL.search(path.read_text(encoding="utf-8", errors="ignore")):
                raise SystemExit(f"Posible credencial en {path.relative_to(ROOT)}")

print("S02 OK: sin formatos de claves persistentes en los archivos inspeccionados")
