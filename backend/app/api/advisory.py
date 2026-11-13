from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query

from app.services.advisory import (
    get_spray_calendar,
    get_fertilizers,
    get_compatibility_rules,
    calculate_tank_mix,
    get_pesticide_dealers,
    get_expert_advisors,
    get_product_buy_links,
    SKUAST_ANNUAL_SPRAY_CALENDAR,
)

router = APIRouter(prefix="/advisory", tags=["advisory"])


@router.get("/fertilizers")
def list_fertilizers(
    category: Optional[str] = Query(None, description="Optional category filter (e.g. fertilizer, biostimulant)"),
    search: Optional[str] = Query(None, description="Optional keyword search (e.g. Urea, Calcium, Zinc, Boron, NPK)")
) -> List[Dict[str, Any]]:
    """Returns official SKUAST-K apple orchard fertilizers, foliar nutrients, and trace minerals with tank calibrations."""
    fertilizers = get_fertilizers()
    if category:
        fertilizers = [f for f in fertilizers if category.lower() in f.get("category", "").lower()]
    if search:
        s = search.lower()
        fertilizers = [
            f for f in fertilizers
            if s in f.get("name", "").lower() or s in f.get("purpose", "").lower() or s in f.get("stage", "").lower()
        ]
    return fertilizers


@router.get("/calendar")
def full_spray_calendar() -> List[Dict[str, Any]]:
    """Returns the official 8-stage SKUAST-Kashmir Annual Apple Spray Calendar."""
    return get_spray_calendar()


@router.post("/calendar/import")
def import_spray_calendar(stages: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Imports or synchronizes the official SKUAST-Kashmir Annual Apple Spray Calendar."""
    calendar = stages if stages else get_spray_calendar()
    fertilizers = get_fertilizers()
    return {
        "status": "success",
        "imported_stages_count": len(calendar),
        "imported_fertilizers_count": len(fertilizers),
        "stages": calendar,
        "fertilizers": fertilizers,
        "source": "SKUAST-Kashmir Directorate of Extension",
        "message": f"Successfully imported {len(calendar)} phenological stages and {len(fertilizers)} foliar fertilizers.",
    }


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


@router.get("/dealers")
def list_dealers(
    district: Optional[str] = Query(None, description="Kashmir district (e.g. Shopian, Sopore, Baramulla, Pulwama, Anantnag)"),
    latitude: Optional[float] = Query(None, description="User GPS latitude for distance sorting"),
    longitude: Optional[float] = Query(None, description="User GPS longitude for distance sorting"),
) -> List[Dict[str, Any]]:
    """Returns licensed pesticide & fertilizer dealers in Kashmir, sorted by nearest GPS distance."""
    return get_pesticide_dealers(district=district, lat=latitude, lon=longitude)


@router.get("/experts")
def list_experts(
    district: Optional[str] = Query(None, description="Optional district to prioritize local KVK and extension offices")
) -> List[Dict[str, Any]]:
    """Returns SKUAST-K plant pathology scientists, KVK extension officers, and official toll-free Kisan helplines."""
    return get_expert_advisors(district=district)


@router.get("/buy-links")
def product_buy_links(
    product: str = Query(..., description="Chemical formulation name, e.g. Mancozeb 75 WP (Indofil M-45)")
) -> Dict[str, Any]:
    """Returns direct verified links to buy the recommended fungicide/chemical online via authentic agricultural portals."""
    return get_product_buy_links(product)
