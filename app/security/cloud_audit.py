import os
import time
import logging
from datetime import datetime, timezone
from fastapi import Request

logger = logging.getLogger("zt-dispatch-cloud-audit")

def _setup_cloud_logging():
    """Ініціалізує Cloud Logging якщо є GCP credentials."""
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("K_SERVICE"):
        try:
            from google.cloud import logging as cloud_logging
            client = cloud_logging.Client()
            client.setup_logging()
            logger.info("Cloud Logging connected successfully")
            return True
        except Exception as e:
            logger.warning(f"Cloud Logging unavailable, falling back to stdout: {e}")
    return False

_cloud_enabled = _setup_cloud_logging()

async def cloud_audit_middleware(request: Request, call_next):
    """Middleware для незмінного логування всіх HTTP-запитів у GCP Cloud Logging."""
    start = time.time()
    response = await call_next(request)
    latency = round(time.time() - start, 3)

    log_payload = {
        "event": "http_request",
        "service": "zt-dispatch",
        "endpoint": request.url.path,
        "method": request.method,
        "status_code": response.status_code,
        "latency_seconds": latency,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if response.status_code >= 400:
        logger.error(log_payload)
    else:
        logger.info(log_payload)

    return response
