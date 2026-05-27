from fastapi.testclient import TestClient

from app.main import RATE_LIMIT_BUCKETS, app, settings
from app.services.bible_retriever import BibleRetriever


def test_health_adds_production_headers() -> None:
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["x-request-id"]


def test_readiness_reports_core_checks() -> None:
    client = TestClient(app)
    response = client.get("/ready")

    assert response.status_code == 200
    payload = response.json()
    assert payload["checks"]["bible_corpus"] is True
    assert payload["checks"]["cors_configured"] is True
    assert payload["checks"]["rate_limit_enabled"] is True
    assert payload["checks"]["request_size_limited"] is True


def test_metrics_endpoint_exposes_prometheus_counters() -> None:
    client = TestClient(app)
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "scriptureguard_requests_total" in response.text


def test_api_key_gate_is_enforced_when_configured() -> None:
    previous = settings.api_keys
    settings.api_keys = "test-secret"
    client = TestClient(app)
    try:
        missing = client.post("/not-found", json={"message": "hello"})
        allowed = client.post("/not-found", headers={"X-API-Key": "test-secret"}, json={})
    finally:
        settings.api_keys = previous

    assert missing.status_code == 401
    assert allowed.status_code == 404


def test_request_body_limit_rejects_large_payload() -> None:
    previous = settings.max_request_body_bytes
    settings.max_request_body_bytes = 4
    client = TestClient(app)
    try:
        response = client.post("/not-found", content="too-large")
    finally:
        settings.max_request_body_bytes = previous

    assert response.status_code == 413


def test_rate_limit_rejects_excess_requests() -> None:
    previous_enabled = settings.rate_limit_enabled
    previous_limit = settings.rate_limit_per_minute
    settings.rate_limit_enabled = True
    settings.rate_limit_per_minute = 1
    RATE_LIMIT_BUCKETS.clear()
    client = TestClient(app)
    try:
        first = client.post("/not-found", json={})
        second = client.post("/not-found", json={})
    finally:
        settings.rate_limit_enabled = previous_enabled
        settings.rate_limit_per_minute = previous_limit
        RATE_LIMIT_BUCKETS.clear()

    assert first.status_code == 404
    assert second.status_code == 429


async def test_retriever_prioritizes_explicit_reference() -> None:
    retriever = BibleRetriever()

    verses = await retriever.retrieve_verses("What does John 3:16 teach?", "protestant")

    assert verses
    assert verses[0].reference == "John 3:16"
