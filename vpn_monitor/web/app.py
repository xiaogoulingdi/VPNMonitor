from contextlib import asynccontextmanager
import threading

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from vpn_monitor.config import BASE_DIR, settings
from vpn_monitor.db import init_db
from vpn_monitor.services.collector import collector_loop, ingest_once
from vpn_monitor.web.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    stop_event = threading.Event()
    collector = None
    if settings.collector_enabled:
        ingest_once()
        collector = threading.Thread(target=collector_loop, args=(stop_event,), daemon=True)
        collector.start()
    yield
    stop_event.set()
    if collector:
        collector.join(timeout=3)


app = FastAPI(
    title="VPN Monitor",
    version="0.1.0",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "vpn_monitor" / "web" / "static")), name="static")
app.include_router(router)
