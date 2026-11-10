import asyncio
import io
import pytest
import httpx
from PIL import Image, ImageDraw

from app.main import app
from app.services.plant_guard import check_is_plant
from app.services.advisory import build_advisory


def test_health():
    async def _run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            res = await client.get("/health")
            assert res.status_code == 200
            assert res.json() == {"status": "ok"}
    asyncio.run(_run())


def test_plant_guard_with_leaf():
    # Green foliage sample
    leaf_img = Image.new("RGB", (224, 224), color=(34, 139, 34))
    is_plant, reason, _ = check_is_plant(leaf_img)
    assert is_plant is True
    assert "Valid" in reason


def test_plant_guard_rejects_non_plant():
    # Solid blue / vehicle tone
    car_img = Image.new("RGB", (224, 224), color=(20, 50, 220))
    is_plant, reason, _ = check_is_plant(car_img)
    assert is_plant is False
    assert "No plant leaf" in reason or "non-plant" in reason


def test_skuast_advisory_contents():
    # Test apple scab at Green Tip
    adv_gt = build_advisory("apple_scab", "Green Tip", False)
    assert adv_gt["disease_common"] == "Apple Scab"
    assert any("Mancozeb" in p["product"] for p in adv_gt["recommendations"])
    assert any("DRY WINDOW" in g for g in adv_gt["guardrails"])

    # Test rain warning postponement
    adv_rain = build_advisory("apple_scab", "Pink Bud", True)
    assert any("POSTPONE" in g for g in adv_rain["guardrails"])

    # Test Full Bloom honeybee shield
    adv_bloom = build_advisory("powdery_mildew", "Full Bloom", False)
    assert any("POLLINATOR SHIELD" in g for g in adv_bloom["guardrails"])

    # Test healthy leaf
    adv_healthy = build_advisory("healthy", "Fruit Growth", False)
    assert adv_healthy["disease_common"] == "Healthy Apple Leaf"
    assert any("No chemical" in p["product"] for p in adv_healthy["recommendations"])


def test_diagnose_inappropriate_image():
    async def _run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            img = Image.new("RGB", (224, 224), color=(240, 240, 240))
            draw = ImageDraw.Draw(img)
            draw.text((20, 50), "Non-plant document text", fill=(0, 0, 0))

            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            buf.seek(0)

            files = {"file": ("document.jpg", buf, "image/jpeg")}
            data = {"growth_stage": "Green Tip", "rain_within_12_hours": "false"}
            res = await client.post("/api/v1/diagnoses/upload", files=files, data=data)
            assert res.status_code == 200
            json_res = res.json()
            assert json_res["inappropriate"] is True
            assert json_res["is_plant"] is False
            assert "INAPPROPRIATE IMAGE" in json_res["guardrails"][0]
    asyncio.run(_run())


def test_leaf_held_in_hand():
    # Green leaf in center with skin-tone border (simulating farmer hand holding leaf)
    img = Image.new("RGB", (128, 128), color=(220, 160, 120)) # skin tone background
    draw = ImageDraw.Draw(img)
    draw.rectangle([25, 20, 105, 110], fill=(34, 139, 34)) # central green leaf
    is_plant, reason, _ = check_is_plant(img)
    assert is_plant is True
    assert "Valid" in reason


def test_weather_spray_forecast_endpoints():
    async def _run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # 1. Test districts listing
            dist_res = await client.get("/api/v1/weather/districts")
            assert dist_res.status_code == 200
            districts = dist_res.json()
            assert any(d["name"].startswith("Shopian") for d in districts)
            assert any(d["name"].startswith("Sopore") for d in districts)

            # 2. Test 7-day spray forecast
            fc_res = await client.get("/api/v1/weather/spray-forecast?district=Shopian")
            assert fc_res.status_code == 200
            fc_data = fc_res.json()
            assert "Shopian" in fc_data["district"]
            assert len(fc_data["forecast_days"]) == 7
            first_day = fc_data["forecast_days"][0]
            assert "status" in first_day
            assert first_day["status"] in ["optimal", "marginal", "no_spray"]
            assert "best_hours" in first_day
            assert "skuast_directive" in first_day

    asyncio.run(_run())


def test_skuast_annual_spray_calendar_endpoints():
    async def _run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # 1. Full 8-stage calendar
            cal_res = await client.get("/api/v1/advisory/calendar")
            assert cal_res.status_code == 200
            calendar = cal_res.json()
            assert len(calendar) == 8
            assert calendar[0]["stage_name"] == "Delayed Dormant"
            assert calendar[1]["stage_name"] == "Green Tip"
            assert calendar[3]["stage_name"] == "Full Bloom"
            assert calendar[7]["stage_name"] == "Post-Harvest / Pre-Leaf Fall"

            # 2. Stage by ID
            stage_res = await client.get("/api/v1/advisory/calendar/green_tip")
            assert stage_res.status_code == 200
            stage_gt = stage_res.json()
            assert stage_gt["stage_name"] == "Green Tip"
            assert any("Mancozeb" in p["product"] for p in stage_gt["products"])

            # 3. Compatibility rules
            comp_res = await client.get("/api/v1/advisory/compatibility")
            assert comp_res.status_code == 200
            compat = comp_res.json()
            assert len(compat) >= 5
            assert any("incompatible" in c["status"] for c in compat)

            # 4. Tank calculator
            calc_res = await client.get("/api/v1/advisory/tank-calculator?chemical=Score&water_liters=500")
            assert calc_res.status_code == 200
            calc_data = calc_res.json()
            assert "Score" in calc_data["chemical"]
            assert calc_data["water_liters"] == 500.0
            assert "150" in calc_data["total_quantity"]

    asyncio.run(_run())
