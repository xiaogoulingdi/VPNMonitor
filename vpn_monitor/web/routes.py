from io import StringIO
import csv
import json
from urllib.parse import parse_qs

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from vpn_monitor.auth import make_session, verify_password, verify_session
from vpn_monitor.config import BASE_DIR, settings
from vpn_monitor.services.analytics import export_rows, query_active, query_events, query_options, query_summary


templates = Jinja2Templates(directory=str(BASE_DIR / "vpn_monitor" / "web" / "templates"))
router = APIRouter()

CSV_FIELDS = ["id", "time_utc", "source_ip", "source_port", "email", "inbound", "outbound", "network", "destination", "domain", "dest_port", "category", "action", "raw"]


def current_user(request: Request) -> str | None:
    return verify_session(request.cookies.get(settings.cookie_name))


def is_authenticated(request: Request) -> bool:
    return current_user(request) is not None


def unauthorized_json() -> JSONResponse:
    return JSONResponse({"detail": "Not authenticated"}, status_code=401)


def redirect_to_login() -> RedirectResponse:
    response = RedirectResponse("login", status_code=302)
    response.headers["Cache-Control"] = "no-store"
    return response


def require_api_auth(request: Request):
    if not is_authenticated(request):
        return unauthorized_json()
    return None


@router.get("/login", response_class=HTMLResponse)
@router.get("/login.html", response_class=HTMLResponse)
async def login_page(request: Request):
    if is_authenticated(request):
        return RedirectResponse("./", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": request.query_params.get("error")})


@router.post("/login")
async def login(request: Request):
    body = (await request.body())[:8192].decode("utf-8", "replace")
    data = parse_qs(body)
    username = data.get("username", [""])[0]
    password = data.get("password", [""])[0]
    if not verify_password(username, password):
        return RedirectResponse("login?error=1", status_code=302)
    response = RedirectResponse("./", status_code=302)
    response.set_cookie(settings.cookie_name, make_session(username), max_age=settings.session_ttl_seconds, httponly=True, samesite="lax", path=settings.cookie_path)
    response.headers["Cache-Control"] = "no-store"
    return response


@router.get("/logout")
async def logout():
    response = RedirectResponse("login", status_code=302)
    response.delete_cookie(settings.cookie_name, path=settings.cookie_path)
    response.headers["Cache-Control"] = "no-store"
    return response


@router.get("/", response_class=HTMLResponse)
@router.get("/index.html", response_class=HTMLResponse)
async def index(request: Request):
    if not is_authenticated(request):
        return redirect_to_login()
    return templates.TemplateResponse("index.html", {"request": request, "active_window_minutes": max(settings.active_window_seconds // 60, 1)})


@router.get("/health")
async def health():
    return {"ok": True, "db": str(settings.db_path), "access_log": str(settings.access_log), "collector_enabled": settings.collector_enabled}


@router.get("/api/options")
async def api_options(request: Request):
    if response := require_api_auth(request):
        return response
    return query_options()


@router.get("/api/summary")
async def api_summary(request: Request):
    if response := require_api_auth(request):
        return response
    return query_summary(request.query_params)


@router.get("/api/active")
async def api_active(request: Request):
    if response := require_api_auth(request):
        return response
    return query_active(request.query_params)


@router.get("/api/events")
async def api_events(request: Request):
    if response := require_api_auth(request):
        return response
    return query_events(request.query_params)


@router.get("/api/export.json")
async def export_json(request: Request):
    if response := require_api_auth(request):
        return response
    rows = export_rows(request.query_params)
    return Response(json.dumps(rows, ensure_ascii=False, indent=2), media_type="application/json", headers={"Content-Disposition": "attachment; filename=vpn-monitor-events.json"})


@router.get("/api/export.csv")
async def export_csv(request: Request):
    if response := require_api_auth(request):
        return response
    rows = export_rows(request.query_params)
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=CSV_FIELDS)
    writer.writeheader()
    for row in rows:
        writer.writerow({field: row.get(field, "") for field in CSV_FIELDS})
    return PlainTextResponse(output.getvalue(), media_type="text/csv; charset=utf-8", headers={"Content-Disposition": "attachment; filename=vpn-monitor-events.csv"})
