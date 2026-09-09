"""
Pydantic models for the mock CAMARA / Nokia Network-as-Code service.

NOTE: These field names follow the *typical* real-world CAMARA API shapes
(Device Location Verification, Device Reachability, SIM Swap, QoD Congestion
Insights). Once contracts/examples/camara_device.json is confirmed, rename
fields here to match exactly — this is the ONLY file that needs edits for
that.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class Device(BaseModel):
    """Common device identifier block used across all CAMARA endpoints."""
    phoneNumber: str = Field(..., description="E.164 format, e.g. +212600112233")


# ---- Device Location Verification ----

class LocationVerificationRequest(BaseModel):
    device: Device
    latitude: float
    longitude: float
    accuracy: int = Field(..., description="Radius in meters to verify against")


class VerificationResult(str, Enum):
    TRUE = "TRUE"
    FALSE = "FALSE"
    PARTIAL = "PARTIAL"
    UNKNOWN = "UNKNOWN"


class CAMARALocation(BaseModel):
    device: Device
    lastLocationTime: int = Field(..., description="Unix ms")
    verificationResult: VerificationResult
    matchRate: Optional[int] = Field(None, description="0-100, confidence %")
    latitude: float
    longitude: float


# ---- Device Reachability Status ----

class ReachabilityType(str, Enum):
    SMS = "SMS"
    DATA = "DATA"
    UNKNOWN = "UNKNOWN"


class Reachability(BaseModel):
    device: Device
    lastStatusTime: int = Field(..., description="Unix ms")
    reachable: bool
    reachabilityType: ReachabilityType


# ---- SIM Swap / Identity Verification ----

class Verification(BaseModel):
    device: Device
    swapped: bool
    latestSimChangeTime: Optional[int] = Field(None, description="Unix ms, null if never swapped")


# ---- QoD Congestion Insights ----

class CongestionLevel(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Congestion(BaseModel):
    device: Device
    congestionLevel: CongestionLevel
    lastUpdatedTime: int = Field(..., description="Unix ms")


# ---- Health check ----

class Health(BaseModel):
    status: str
    service: str = "mock-camara"
