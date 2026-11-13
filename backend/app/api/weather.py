from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Query

from app.services.weather import WeatherService, KASHMIR_DISTRICTS

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("")
async def legacy_weather(
    latitude: float = Query(33.8731, ge=-90, le=90),
    longitude: float = Query(75.1487, ge=-180, le=180),
    district: Optional[str] = Query(None)
) -> Dict[str, Any]:
    """Microclimate query returning 7-day spray feasibility and 12h rain safety."""
    svc = WeatherService()
    return await svc.get_7day_spray_forecast(latitude, longitude, district)


@router.get("/spray-forecast")
async def spray_forecast(
    latitude: float = Query(33.7182, ge=-90, le=90),
    longitude: float = Query(75.1548, ge=-180, le=180),
    district: Optional[str] = Query("Shopian")
) -> Dict[str, Any]:
    """7-day agricultural spray window forecast with SKUAST-K Kashmir advisory directives."""
    svc = WeatherService()
    return await svc.get_7day_spray_forecast(latitude, longitude, district)


@router.get("/districts")
def list_districts() -> List[Dict[str, Any]]:
    """Returns list of major apple-growing districts of Kashmir with pre-configured coordinates."""
    return [
        {
            "id": key,
            "name": val["name"],
            "latitude": val["lat"],
            "longitude": val["lon"],
            "elevation_m": val["elevation_m"],
        }
        for key, val in KASHMIR_DISTRICTS.items()
    ]


@router.get("/reverse-geocode")
async def reverse_geocode(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
) -> Dict[str, Any]:
    """Reverse geocode GPS coordinates to place/orchard belt name."""
    svc = WeatherService()
    return await svc.reverse_geocode(latitude, longitude)
