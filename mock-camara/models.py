"""
Pydantic models for the mock CAMARA / Nokia Network-as-Code service.

These mirror contracts/examples/camara_device.json EXACTLY:
  - Response bodies contain ONLY the fields in the schema (additionalProperties:
    false in the source schema — no phone/device wrapper in responses; device
    identity is passed via the request, not echoed back).
  - Timestamps are ISO8601 strings here, matching Nokia's raw API format —
    NOT Unix ms. Go converts to Unix ms when building TriagedDevice internally.
  - matchRate is only included when verificationResult == "PARTIAL".
  - TriagedDevice is NOT served by this mock — it's Go's derived output after
    haversine zone calculation, built by combining the 4 responses below.
    It's modelled here only for use in test fixtures, never returned by an
    endpoint.
"""

from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Optional
from enum import Enum


# ---- Shared ----

class Coordinates(BaseModel):
    model_config = ConfigDict(extra="forbid")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


# ---- Location Retrieval ----

class AreaType(str, Enum):
    CIRCLE = "CIRCLE"


class CAMARALocationArea(BaseModel):
    model_config = ConfigDict(extra="forbid")
    areaType: AreaType = AreaType.CIRCLE
    center: Coordinates
    radius: float = Field(..., ge=0, description="Location accuracy radius in metres (~500m urban)")


class CAMARALocationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    lastLocationTime: str = Field(..., description="ISO8601, e.g. 2024-11-14T10:30:00Z")
    area: CAMARALocationArea


# ---- Device Reachability ----

class ReachabilityStatus(str, Enum):
    CONNECTED_DATA = "CONNECTED_DATA"
    CONNECTED_SMS = "CONNECTED_SMS"
    NOT_CONNECTED = "NOT_CONNECTED"


class CAMARAReachabilityResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    lastStatusTime: str = Field(..., description="ISO8601")
    reachabilityStatus: ReachabilityStatus


# ---- Location Verification ----

class VerificationResult(str, Enum):
    TRUE = "TRUE"
    FALSE = "FALSE"
    PARTIAL = "PARTIAL"
    UNKNOWN = "UNKNOWN"


class CAMARAVerificationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    verificationResult: VerificationResult
    matchRate: Optional[int] = Field(
        default=None, ge=0, le=100,
        description="Only present when verificationResult is PARTIAL",
    )
    lastLocationTime: str = Field(..., description="ISO8601")

    @model_validator(mode="after")
    def _match_rate_only_on_partial(self):
        # Enforce the schema's documented rule at the mock level too, so the
        # mock never emits a shape the real API wouldn't.
        if self.verificationResult != VerificationResult.PARTIAL:
            self.matchRate = None
        return self


# ---- Congestion Insights ----

class CongestionLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CAMARACongestionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    level: CongestionLevel
    timestamp: str = Field(..., description="ISO8601")


# ---- TriagedDevice (reference only — NOT served by this mock) ----

class TriagedDevice(BaseModel):
    """
    Go's derived output, modelled here only so test fixtures can be built
    against the real shape. This mock never returns this type from an
    endpoint — zone assignment is Go's job, never CAMARA's or the mock's.
    """
    model_config = ConfigDict(extra="forbid")
    phone: str = Field(..., pattern=r"^\+[1-9]\d{1,14}$")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    location_radius_m: float = Field(..., ge=0)
    last_location_time: str
    reachability_status: ReachabilityStatus
    last_status_time: str
    zone: str = Field(..., pattern=r"^(red|orange|green)$")
    distance_km: float = Field(..., ge=0)


# ---- Health check (mock's own — not part of the locked contract) ----

class Health(BaseModel):
    status: str
    service: str = "mock-camara"
