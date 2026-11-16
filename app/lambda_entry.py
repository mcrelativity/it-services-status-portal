import logging

from mangum import Mangum

from app.main import app, monitor_services, service_summary

logging.getLogger("mangum").setLevel(logging.WARNING)
api_handler = Mangum(app, lifespan="off")


def handler(event, context):
    if event.get("source") == "portal.scheduler":
        return service_summary(monitor_services())
    return api_handler(event, context)

