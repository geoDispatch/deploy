"""
mock-camara — a mock of Nokia NaC / CAMARA APIs for GeoDispatch local dev,
CI, and demo-safety-net use.

Response shapes match contracts/examples/camara_device.json EXACTLY:
  POST /location-retrieval      -> CAMARALocationResponse
  GET  /reachability/{phone}    -> CAMARAReachabilityResponse
  POST /location-verification   -> CAMARAVerificationResponse
  GET  /congestion-insights     -> CAMARACongestionResponse
  GET  /health                  -> mock's own health shape (not part of the
                                    locked contract)

Device identity (phone number) is passed via the REQUEST only — per the
schema, response bodies never echo it back (additionalProperties: false,
no phone/device field in any of the 4 response definitions).

This mock does NOT produce TriagedDevice — that's Go's job (haversine +
CAMARA data combination), never CAMARA's or this mock's.

Failure injection (for testing Go's CAMARA_TIMEOUT / QOS_FAILED handling):
  ?fail=timeout      -> ~5s delay, then 504 with code CAMARA_TIMEOUT
  ?fail=qos_failed   -> immediate 503 with code QOS_FAILED
  MOCK_FAILURE_RATE  -> env var (0.0-1.0), random failures on any request
"""

import os
import random
import asyncio
from datetime import datetime, timezone, timedelta

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.models import (
    Coordinates,
    CAMARALocationArea,
    CAMARALocationResponse,
    ReachabilityStatus,
    CAMARAReachabilityResponse,
    VerificationResult,
    CAMARAVerificationResponse,
    CongestionLevel,
    CAMARACongestionResponse,
    Health,
)

app = FastAPI(
    title="mock-camara",
    description="Mock Nokia NaC / CAMARA API for GeoDispatch, matching contracts/examples/camara_device.json",
    version="0.2.0",
)

FAILURE_RATE = float(os.getenv("MOCK_FAILURE_RATE", "0"))
ARTIFICIAL_LATENCY_MS = int(os.getenv("MOCK_LATENCY_MS", "0"))


def _iso_now() -> str:
    """ISO8601 with Z suffix, matching Nokia's raw format e.g. 2024-11-14T10:30:00Z"""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _iso_ago(days: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")


async def _maybe_inject_failure(fail: str | None):
    if ARTIFICIAL_LATENCY_MS:
        await asyncio.sleep(ARTIFICIAL_LATENCY_MS / 1000)

    if fail == "timeout":
        await asyncio.sleep(5)
        raise HTTPException(status_code=504, detail="CAMARA_TIMEOUT: simulated device timeout")

    if fail == "qos_failed":
        raise HTTPException(status_code=503, detail="QOS_FAILED: simulated QoS failure, fallback to standard")

    if FAILURE_RATE and random.random() < FAILURE_RATE:
        raise HTTPException(status_code=500, detail="Simulated random failure (MOCK_FAILURE_RATE)")


@app.get("/health", response_model=Health)
async def health():
    return Health(status="ok")


# ---- Location Retrieval ----

class LocationRetrievalRequest(BaseModel):
    phoneNumber: str = Field(..., description="E.164 — used to look up the device, not echoed in the response")


@app.post("/location-retrieval", response_model=CAMARALocationResponse)
async def location_retrieval(
    req: LocationRetrievalRequest,
    fail: str | None = Query(default=None, description="timeout | qos_failed"),
):
    await _maybe_inject_failure(fail)

    # Random plausible point near Rabat for local testing; real requests
    # would resolve this from the actual device's last known cell/GPS fix.
    lat = 33.9716 + random.uniform(-0.05, 0.05)
    lng = -6.8498 + random.uniform(-0.05, 0.05)

    return CAMARALocationResponse(
        lastLocationTime=_iso_now(),
        area=CAMARALocationArea(
            center=Coordinates(latitude=lat, longitude=lng),
            radius=500,
        ),
    )


# ---- Device Reachability ----

@app.get("/reachability/{phone_number}", response_model=CAMARAReachabilityResponse)
async def reachability(
    phone_number: str,
    fail: str | None = Query(default=None, description="timeout | qos_failed"),
):
    await _maybe_inject_failure(fail)

    status = random.choices(
        [ReachabilityStatus.CONNECTED_DATA, ReachabilityStatus.CONNECTED_SMS, ReachabilityStatus.NOT_CONNECTED],
        weights=[45, 40, 15],
    )[0]

    return CAMARAReachabilityResponse(
        lastStatusTime=_iso_now(),
        reachabilityStatus=status,
    )


# ---- Location Verification ----

class LocationVerificationRequest(BaseModel):
    phoneNumber: str
    latitude: float
    longitude: float
    accuracy: int = Field(..., description="Radius in metres to verify the device within")


@app.post("/location-verification", response_model=CAMARAVerificationResponse, response_model_exclude_none=True)
async def location_verification(
    req: LocationVerificationRequest,
    fail: str | None = Query(default=None, description="timeout | qos_failed"),
):
    await _maybe_inject_failure(fail)

    result = random.choices(
        [VerificationResult.TRUE, VerificationResult.PARTIAL, VerificationResult.FALSE, VerificationResult.UNKNOWN],
        weights=[55, 25, 15, 5],
    )[0]

    return CAMARAVerificationResponse(
        verificationResult=result,
        matchRate=random.randint(40, 89) if result == VerificationResult.PARTIAL else None,
        lastLocationTime=_iso_now(),
    )


# ---- Congestion Insights ----

@app.get("/congestion-insights", response_model=CAMARACongestionResponse)
async def congestion_insights(
    latitude: float = Query(...),
    longitude: float = Query(...),
    radius_km: float = Query(default=5.0),
    fail: str | None = Query(default=None, description="timeout | qos_failed"),
):
    await _maybe_inject_failure(fail)

    level = random.choices(
        [CongestionLevel.LOW, CongestionLevel.MEDIUM, CongestionLevel.HIGH, CongestionLevel.CRITICAL],
        weights=[35, 30, 25, 10],
    )[0]

    return CAMARACongestionResponse(
        level=level,
        timestamp=_iso_now(),
    )


@app.exception_handler(HTTPException)
async def camara_style_error_handler(request, exc: HTTPException):
    """
    Wrap errors in a shape close to real CAMARA error responses, so Go's
    error-parsing code exercises the same path against mock and real API.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": exc.status_code,
            "code": "CAMARA_TIMEOUT" if exc.status_code == 504 else "QOS_FAILED" if exc.status_code == 503 else "GENERIC_ERROR",
            "message": exc.detail,
        },
    )
