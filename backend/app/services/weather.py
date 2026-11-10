from datetime import datetime, timezone
from typing import Any

import httpx

from app.core.config import get_settings


class WeatherService:
    async def current_and_forecast(self, latitude: float, longitude: float) -> dict[str, Any]:
        settings = get_settings()
        if not settings.openweather_api_key or settings.openweather_api_key == "development-unused":
            raise RuntimeError("OpenWeather API key is not configured.")
        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": settings.openweather_api_key,
            "units": "metric",
            "cnt": 5,
        }
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get("https://api.openweathermap.org/data/2.5/forecast", params=params)
            response.raise_for_status()
        payload = response.json()
        now = datetime.now(timezone.utc).timestamp()
        next_12h = [item for item in payload.get("list", []) if item.get("dt", 0) <= now + 12 * 3600]
        rain_within_12_hours = any(float(item.get("pop", 0)) >= 0.4 or item.get("rain", {}).get("3h", 0) > 0 for item in next_12h)
        return {"provider": "openweathermap", "rain_within_12_hours": rain_within_12_hours, "current": payload.get("list", [{}])[0], "forecast": next_12h}
