import httpx
from fastapi import APIRouter, HTTPException, Query

from app.services.weather import WeatherService

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("")
async def weather(latitude: float = Query(..., ge=-90, le=90), longitude: float = Query(..., ge=-180, le=180)) -> dict:
    try:
        return await WeatherService().current_and_forecast(latitude, longitude)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 401:
            raise HTTPException(
                status_code=502,
                detail="OpenWeather rejected the API key. Verify it is active and belongs to OpenWeather.",
            ) from exc
        raise HTTPException(status_code=502, detail="OpenWeather returned an error.") from exc
    except (httpx.HTTPError, RuntimeError) as exc:
        raise HTTPException(status_code=503, detail=f"Weather service unavailable: {exc}") from exc
