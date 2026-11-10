from fastapi import APIRouter, Depends, Query

from app.api.deps import current_user
from app.models import User
from app.services.weather import WeatherService

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("")
async def weather(latitude: float = Query(..., ge=-90, le=90), longitude: float = Query(..., ge=-180, le=180), _: User = Depends(current_user)) -> dict:
    return await WeatherService().current_and_forecast(latitude, longitude)
