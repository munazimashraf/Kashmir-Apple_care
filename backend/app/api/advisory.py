from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query

from app.services.advisory import (
    get_spray_calendar,
    get_compatibility_rules,
    calculate_tank_mix,
    SKUAST_ANNUAL_SPRAY_CALENDAR,
)

router = APIRouter(prefix="/advisory", tags=["advisory"])


@router.get("/calendar")
def full_spray_calendar() -> List[Dict[str, Any]]:
    """Returns the official 8-stage SKUAST-Kashmir Annual Apple Spray Calendar."""
    return get_spray_calendar()


@router.get("/calendar/{stage_id}")
def stage_spray_calendar(stage_id: str) -> Dict[str, Any]:
    """Returns detailed chemical formulations, dosages, and cultural sanitation for a specific stage."""
    calendar = get_spray_calendar()
    for stage in calendar:
        if stage["id"] == stage_id or stage["stage_name"].lower() == stage_id.lower():
            return stage
    raise HTTPException(status_code=404, detail=f"Stage '{stage_id}' not found in SKUAST spray calendar.")


@router.get("/compatibility")
def chemical_compatibility() -> List[Dict[str, Any]]:
    """Returns SKUAST-K chemical compatibility rules and tank mixing guidelines."""
    return get_compatibility_rules()


@router.get("/tank-calculator")
def tank_calculator(
    chemical: str = Query("Mancozeb 75 WP", description="Name of the chemical formulation"),
    water_liters: float = Query(1000.0, ge=1.0, le=10000.0, description="Volume of spray tank in liters")
) -> Dict[str, Any]:
    """Calculates exact required chemical weight or volume for any spray tank capacity."""
    return calculate_tank_mix(chemical, water_liters)
