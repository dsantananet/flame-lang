"""Versioned input contract for the server-side IgnisPyro simulation engine.

This module validates inputs; it does not simulate fire propagation.
"""
from datetime import datetime, timezone
from math import isfinite

SCHEMA_VERSION = "1.0"

class ContractError(ValueError):
    pass

def _utc(value):
    if not isinstance(value, str):
        raise ContractError("valid_time must be an ISO 8601 string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ContractError("invalid valid_time") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ContractError("valid_time must include timezone")
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

def validate_weather(payload):
    if not isinstance(payload, dict) or payload.get("schema_version") != SCHEMA_VERSION:
        raise ContractError("unsupported schema_version")
    if not isinstance(payload.get("source"), str) or not payload["source"].strip():
        raise ContractError("source required")
    valid_time = _utc(payload.get("valid_time"))
    crs = payload.get("geometry_crs")
    if crs != "EPSG:4326":
        raise ContractError("geometry_crs must be EPSG:4326")
    point = payload.get("point")
    if not isinstance(point, dict):
        raise ContractError("point required")
    lat, lon = point.get("lat"), point.get("lon")
    if any(isinstance(x, bool) or not isinstance(x, (float, int)) or not isfinite(x) for x in (lat, lon)):
        raise ContractError("invalid coordinates")
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ContractError("coordinates outside geographic bounds")
    variables = payload.get("variables")
    if not isinstance(variables, dict) or not variables:
        raise ContractError("nonempty variables required")
    allowed = {"temperature_c": (-100, 70), "relative_humidity_pct": (0, 100),
               "wind_speed_ms": (0, 150), "wind_direction_deg": (0, 360),
               "precipitation_mm_h": (0, 1000), "pressure_hpa": (300, 1100)}
    for key, measurement in variables.items():
        if key not in allowed or not isinstance(measurement, (int, float)) or isinstance(measurement, bool) or not isfinite(measurement):
            raise ContractError(f"invalid variable: {key}")
        low, high = allowed[key]
        if not low <= measurement <= high:
            raise ContractError(f"out of range: {key}")
    quality = payload.get("quality_flags", [])
    if not isinstance(quality, list) or any(not isinstance(x, str) for x in quality):
        raise ContractError("quality_flags must be an array of strings")
    return {**payload, "valid_time": valid_time}
