"""Provocar cinco respuestas 404 para activar la alarma real del portal."""
import argparse
from datetime import UTC, datetime
from urllib.error import HTTPError
from urllib.request import urlopen

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("url", help="URL HTTPS del portal de esta evaluación")
args = parser.parse_args()
if not args.url.startswith("https://"):
    parser.error("se requiere la URL HTTPS del portal")

for _ in range(5):
    try:
        with urlopen(args.url.rstrip("/") + "/static/evaluacion-alarma-404.txt", timeout=10):
            raise SystemExit("La ruta de prueba devolvió una respuesta inesperada.")
    except HTTPError as exc:
        if exc.code != 404:
            raise
        print(datetime.now(UTC).isoformat(), "HTTP 404", exc.headers.get("apigw-requestid"))

