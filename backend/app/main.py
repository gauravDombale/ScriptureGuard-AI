from collections import defaultdict, deque
import logging
import time
from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from starlette.requests import Request

from app.config import get_settings
from app.routers import chat, health, image

settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("scriptureguard.api")
PUBLIC_PATHS = {"/health", "/ready", "/metrics", "/docs", "/redoc", "/openapi.json"}
RATE_LIMIT_BUCKETS: dict[str, deque[float]] = defaultdict(deque)
METRICS = {
    "requests_total": 0,
    "errors_total": 0,
    "rate_limited_total": 0,
    "unauthorized_total": 0,
    "request_duration_ms_sum": 0.0,
}

app = FastAPI(
    title="ScriptureGuard AI",
    description="Christianity-focused AI assistant with grounded KJV citations and safety guards.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def production_headers_and_request_logging(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or str(uuid4())
    started = time.perf_counter()
    response = early_rejection_response(request)
    if response is None:
        try:
            response = await call_next(request)
        except Exception:
            METRICS["errors_total"] += 1
            logger.exception(
                "Unhandled request failure",
                extra={"request_id": request_id, "path": request.url.path},
            )
            raise

    return finalize_response(request, response, request_id, started)


@app.get("/metrics", include_in_schema=False)
async def metrics() -> PlainTextResponse:
    if not settings.metrics_enabled:
        return PlainTextResponse("metrics_disabled 1\n", status_code=404)
    lines = [
        "# HELP scriptureguard_requests_total Total HTTP requests handled.",
        "# TYPE scriptureguard_requests_total counter",
        f"scriptureguard_requests_total {int(METRICS['requests_total'])}",
        "# HELP scriptureguard_errors_total Total unhandled HTTP errors.",
        "# TYPE scriptureguard_errors_total counter",
        f"scriptureguard_errors_total {int(METRICS['errors_total'])}",
        "# HELP scriptureguard_rate_limited_total Total rate-limited requests.",
        "# TYPE scriptureguard_rate_limited_total counter",
        f"scriptureguard_rate_limited_total {int(METRICS['rate_limited_total'])}",
        "# HELP scriptureguard_unauthorized_total Total unauthorized requests.",
        "# TYPE scriptureguard_unauthorized_total counter",
        f"scriptureguard_unauthorized_total {int(METRICS['unauthorized_total'])}",
        "# HELP scriptureguard_request_duration_ms_sum Sum of request durations in milliseconds.",
        "# TYPE scriptureguard_request_duration_ms_sum counter",
        f"scriptureguard_request_duration_ms_sum {METRICS['request_duration_ms_sum']:.2f}",
    ]
    return PlainTextResponse("\n".join(lines) + "\n")


def early_rejection_response(request: Request) -> JSONResponse | None:
    if request.method == "OPTIONS" or request.url.path in PUBLIC_PATHS:
        return None

    content_length = request.headers.get("content-length")
    if content_length and parse_content_length(content_length) > settings.max_request_body_bytes:
        return JSONResponse({"detail": "Request body too large"}, status_code=413)

    if settings.api_key_set and not has_valid_api_key(request):
        METRICS["unauthorized_total"] += 1
        return JSONResponse({"detail": "Missing or invalid API key"}, status_code=401)

    if settings.rate_limit_enabled and is_rate_limited(request):
        METRICS["rate_limited_total"] += 1
        return JSONResponse({"detail": "Rate limit exceeded"}, status_code=429)

    return None


def parse_content_length(value: str) -> int:
    try:
        return int(value)
    except ValueError:
        return 0


def has_valid_api_key(request: Request) -> bool:
    header_key = request.headers.get("x-api-key")
    authorization = request.headers.get("authorization", "")
    bearer_key = authorization.removeprefix("Bearer ").strip() if authorization.startswith("Bearer ") else ""
    return bool(settings.api_key_set.intersection({header_key or "", bearer_key}))


def is_rate_limited(request: Request) -> bool:
    now = time.monotonic()
    key = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    if not key and request.client:
        key = request.client.host
    key = key or "unknown"
    bucket = RATE_LIMIT_BUCKETS[key]
    while bucket and now - bucket[0] > 60:
        bucket.popleft()
    if len(bucket) >= settings.rate_limit_per_minute:
        return True
    bucket.append(now)
    return False


def finalize_response(request: Request, response, request_id: str, started: float):
    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    METRICS["requests_total"] += 1
    METRICS["request_duration_ms_sum"] += elapsed_ms
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time-Ms"] = str(elapsed_ms)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "same-origin"
    response.headers["X-Frame-Options"] = "DENY"
    logger.info(
        "Request completed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "elapsed_ms": elapsed_ms,
        },
    )
    return response


app.include_router(health.router)
app.include_router(chat.router)
app.include_router(image.router)
