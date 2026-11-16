import logging

from mangum import Mangum

from app.main import app

logging.getLogger("mangum").setLevel(logging.WARNING)
handler = Mangum(app, lifespan="off")
