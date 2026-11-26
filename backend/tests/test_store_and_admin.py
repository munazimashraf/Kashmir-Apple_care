import asyncio
import httpx
import pytest
from app.main import app
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.api.store import seed_default_products


@pytest.fixture(autouse=True, scope="module")
def ensure_db_ready():
    async def _init():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        async with SessionLocal() as db:
            await seed_default_products(db)
    asyncio.run(_init())


def test_store_product_listing_and_filtering():
    async def _run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # 1. Health check
            h_res = await client.get("/health")
            assert h_res.status_code == 200

            # 2. List all products
            res = await client.get("/api/v1/store/products")
            assert res.status_code == 200
            products = res.json()
            assert len(products) >= 10
            assert any("M9" in p["name"] for p in products)
            assert any("Trellis" in p["name"] or "Posts" in p["name"] for p in products)

            # 3. Filter by category
            cat_res = await client.get("/api/v1/store/products?category=Rootstocks%20%26%20Trees")
            assert cat_res.status_code == 200
            cat_prods = cat_res.json()
            assert len(cat_prods) >= 2
            assert all(p["category"] == "Rootstocks & Trees" for p in cat_prods)

            # 4. Search by keyword
            search_res = await client.get("/api/v1/store/products?search=Gala")
            assert search_res.status_code == 200
            search_prods = search_res.json()
            assert len(search_prods) >= 1
            assert any("Gala" in p["name"] for p in search_prods)
    asyncio.run(_run())


def test_customer_order_placement_and_tracking():
    async def _run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # 1. Get products to find an ID
            p_res = await client.get("/api/v1/store/products")
            products = p_res.json()
            assert len(products) > 0
            p1 = products[0]
            p2 = products[1]

            # 2. Customer places order
            order_payload = {
                "customer_name": "Tariq Ahmad Dar",
                "customer_phone": "9419012345",
                "customer_email": "tariq.orchards@example.com",
                "district": "Shopian",
                "delivery_address": "Pinjora Apple Belt, Near Jamia Masjid, Shopian",
                "payment_method": "Cash on Delivery",
                "items": [
                    {
                        "product_id": p1["id"],
                        "name": p1["name"],
                        "category": p1["category"],
                        "size": p1["size"],
                        "price": p1["price"],
                        "quantity": 10,
                        "image_url": p1["image_url"],
                        "total": p1["price"] * 10,
                    },
                    {
                        "product_id": p2["id"],
                        "name": p2["name"],
                        "category": p2["category"],
                        "size": p2["size"],
                        "price": p2["price"],
                        "quantity": 5,
                        "image_url": p2["image_url"],
                        "total": p2["price"] * 5,
                    },
                ],
                "notes": "Deliver directly to orchard road near cold store.",
            }
            order_res = await client.post("/api/v1/store/orders", json=order_payload)
            assert order_res.status_code == 201
            order_data = order_res.json()
            assert order_data["order_number"].startswith("HD-")
            assert order_data["customer_name"] == "Tariq Ahmad Dar"
            assert order_data["status"] == "received"
            assert order_data["total_amount"] == round((p1["price"] * 10) + (p2["price"] * 5), 2)

            # 3. Customer tracks order by phone
            track_res = await client.get("/api/v1/store/orders/track?phone=9419012345")
            assert track_res.status_code == 200
            tracked = track_res.json()
            assert len(tracked) >= 1
            assert tracked[0]["order_number"] == order_data["order_number"]

            # 4. Customer tracks order by exact order number
            track_num_res = await client.get(f"/api/v1/store/orders/track?order_number={order_data['order_number']}")
            assert track_num_res.status_code == 200
            assert track_num_res.json()[0]["id"] == order_data["id"]
    asyncio.run(_run())


def test_admin_login_stats_and_order_management():
    async def _run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # 1. Admin login with valid credentials
            login_res = await client.post(
                "/api/v1/store/admin/login",
                json={"email": "admin@applecare.kashmir", "password": "AppleCare@Admin2026"},
            )
            assert login_res.status_code == 200
            token = login_res.json()["access_token"]
            assert token

            # Also allow username "admin"
            alias_res = await client.post(
                "/api/v1/store/admin/login",
                json={"email": "admin", "password": "AppleCare@Admin2026"},
            )
            assert alias_res.status_code == 200

            # Invalid password
            bad_res = await client.post(
                "/api/v1/store/admin/login",
                json={"email": "admin@applecare.kashmir", "password": "WrongPassword!"},
            )
            assert bad_res.status_code == 401

            headers = {"Authorization": f"Bearer {token}"}

            # 2. Admin stats
            stats_res = await client.get("/api/v1/store/admin/stats", headers=headers)
            assert stats_res.status_code == 200
            stats = stats_res.json()
            assert stats["total_orders"] >= 1
            assert stats["total_products"] >= 10
            assert stats["received_orders"] >= 1

            # 3. Admin list orders
            orders_res = await client.get("/api/v1/store/admin/orders", headers=headers)
            assert orders_res.status_code == 200
            orders = orders_res.json()
            assert len(orders) >= 1
            first_order = orders[0]

            # 4. Admin update order status to 'confirmed'
            patch1 = await client.patch(
                f"/api/v1/store/admin/orders/{first_order['id']}/status",
                headers=headers,
                json={"status": "confirmed", "notes": "Approved by orchard desk"},
            )
            assert patch1.status_code == 200
            assert patch1.json()["status"] == "confirmed"

            # 5. Admin update order status to 'dispatched'
            patch2 = await client.patch(
                f"/api/v1/store/admin/orders/{first_order['id']}/status",
                headers=headers,
                json={"status": "dispatched", "notes": "Dispatched via Shopian Agri Logistics truck #JK03-4521"},
            )
            assert patch2.status_code == 200
            assert patch2.json()["status"] == "dispatched"

            # 6. Admin update order status to 'delivered'
            patch3 = await client.patch(
                f"/api/v1/store/admin/orders/{first_order['id']}/status",
                headers=headers,
                json={"status": "delivered", "notes": "Delivered and verified at orchard gate."},
            )
            assert patch3.status_code == 200
            assert patch3.json()["status"] == "delivered"
    asyncio.run(_run())


def test_admin_product_crud():
    async def _run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # Login as admin
            login_res = await client.post(
                "/api/v1/store/admin/login",
                json={"email": "admin@applecare.kashmir", "password": "AppleCare@Admin2026"},
            )
            token = login_res.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            # 1. Admin adds new product
            new_prod_payload = {
                "name": "Custom High-Density Stainless Bamboo Support Clips",
                "category": "Trellis & Support",
                "size": "25mm Bamboo to 12G Wire Lock (Pack of 200)",
                "price": 650.0,
                "image_url": "https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=600&q=80",
                "description": "Stainless spring clips for affixing central leader training canes directly to structural trellis wires.",
                "stock_quantity": 80,
                "in_stock": True,
                "badge": "Anti-Slip Lock",
            }
            create_res = await client.post("/api/v1/store/admin/products", headers=headers, json=new_prod_payload)
            assert create_res.status_code == 201
            created_prod = create_res.json()
            assert created_prod["name"] == new_prod_payload["name"]
            assert created_prod["price"] == 650.0
            prod_id = created_prod["id"]

            # 2. Admin updates product (change price and size)
            update_res = await client.put(
                f"/api/v1/store/admin/products/{prod_id}",
                headers=headers,
                json={"price": 620.0, "size": "30mm Heavy Gauge (Pack of 200)"},
            )
            assert update_res.status_code == 200
            updated_prod = update_res.json()
            assert updated_prod["price"] == 620.0
            assert updated_prod["size"] == "30mm Heavy Gauge (Pack of 200)"

            # 3. Admin deletes product
            del_res = await client.delete(f"/api/v1/store/admin/products/{prod_id}", headers=headers)
            assert del_res.status_code == 200
            assert del_res.json()["status"] == "deleted"

            # 4. Verify product no longer returned
            get_res = await client.get(f"/api/v1/store/products/{prod_id}")
            assert get_res.status_code == 404
    asyncio.run(_run())
