import base64
import logging
import random
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_db
from app.models import StoreOrder, StoreProduct
from app.schemas.api import (
    AdminLoginResponse,
    AdminStatsResponse,
    LoginRequest,
    OrderCreateRequest,
    OrderResponse,
    OrderStatusUpdateRequest,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)

LOGGER = logging.getLogger("applecare.store")
router = APIRouter(prefix="/store", tags=["store"])
security = HTTPBearer()

# Default High-Density Orchard Catalog (Curated SKUAST-K Standard Equipment)
INITIAL_HD_PRODUCTS = [
    {
        "name": "Red Velox / Gala Schnico on M9 Rootstock",
        "category": "Rootstocks & Trees",
        "size": "2-Year Feathered (7+ branches, Dutch standard)",
        "price": 480.0,
        "image_url": "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?auto=format&fit=crop&w=600&q=80",
        "description": "Certified virus-free feathered high-density apple tree on M9 clonal rootstock. Pre-trained branch angles for rapid year-2 fruiting and intensive production.",
        "stock_quantity": 850,
        "in_stock": True,
        "badge": "Certified Virus-Free",
    },
    {
        "name": "King Roat / Jeromine on M9 T337 Rootstock",
        "category": "Rootstocks & Trees",
        "size": "2-Year Feathered (5-7 branches)",
        "price": 450.0,
        "image_url": "https://images.unsplash.com/photo-1619566636858-adf3ef46400b?auto=format&fit=crop&w=600&q=80",
        "description": "Vigorous spurred high-color apple cultivar on true M9-T337 rootstock. Exceptional fruit skin finish and compact canopy architecture for Kashmir climate.",
        "stock_quantity": 620,
        "in_stock": True,
        "badge": "SKUAST Certified",
    },
    {
        "name": "Granny Smith / Golden Delicious Pollinizer Tree",
        "category": "Rootstocks & Trees",
        "size": "1-Year Knip Tree (Feathered)",
        "price": 380.0,
        "image_url": "https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?auto=format&fit=crop&w=600&q=80",
        "description": "Essential cross-pollination companion for high-density Gala and Delicious blocks. Staggered bloom matches King Roat and Red Velox perfectly.",
        "stock_quantity": 300,
        "in_stock": True,
        "badge": "Pollinizer Match",
    },
    {
        "name": "Hot-Dip Galvanized Steel Trellis Support Posts",
        "category": "Trellis & Support",
        "size": "3.5m Length (50x50mm, 2.5mm heavy wall)",
        "price": 750.0,
        "image_url": "https://images.unsplash.com/photo-1590486803833-1c5dc8ddd4c8?auto=format&fit=crop&w=600&q=80",
        "description": "Heavy-duty structural posts designed to carry full high-density crop load (40-60 MT/ha). Corrosion-proof hot-dip zinc coating with 20+ year field lifespan.",
        "stock_quantity": 1200,
        "in_stock": True,
        "badge": "Hot-Dip Galvanized",
    },
    {
        "name": "High-Tensile Galvanized Trellis Wire (12-Gauge)",
        "category": "Trellis & Support",
        "size": "500m Coil (2.5mm diameter, Class 3 Zinc)",
        "price": 4850.0,
        "image_url": "https://images.unsplash.com/photo-1504917599217-d4dc5ebe6122?auto=format&fit=crop&w=600&q=80",
        "description": "Ultra high-tensile trellis line wire with minimal stretch under snow or wind load. Rated for 4-tier training systems (0.8m, 1.6m, 2.4m, 3.2m).",
        "stock_quantity": 140,
        "in_stock": True,
        "badge": "High Tensile 12G",
    },
    {
        "name": "Gripple Plus Wire Joiner & Dynamic Tensioner",
        "category": "Trellis & Support",
        "size": "Medium Size (Fits 2.00mm to 3.25mm wire)",
        "price": 180.0,
        "image_url": "https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=600&q=80",
        "description": "Self-locking ceramic roller wire connector. Allows tensioning and retensioning season after season without knotting or cutting high-tensile wire.",
        "stock_quantity": 2500,
        "in_stock": True,
        "badge": "Quick-Locking",
    },
    {
        "name": "Heavy-Duty Orchard Earth Anchor with Drive Rod",
        "category": "Trellis & Support",
        "size": "850mm Length, 120mm Solid Steel Helix",
        "price": 420.0,
        "image_url": "https://images.unsplash.com/photo-1581092335397-9583fe92d232?auto=format&fit=crop&w=600&q=80",
        "description": "High holding strength screw-in ground anchor for end posts. Prevents end-assembly heave or collapse under severe winter gales and heavy fruit loads.",
        "stock_quantity": 450,
        "in_stock": True,
        "badge": "Storm Anchor",
    },
    {
        "name": "Pressure Compensating (PC) Drip Lateral Line",
        "category": "Drip Irrigation",
        "size": "16mm Diameter x 500m Roll (0.4m spacing, 2.0 LPH)",
        "price": 3600.0,
        "image_url": "https://images.unsplash.com/photo-1527842891421-42eec6e703ea?auto=format&fit=crop&w=600&q=80",
        "description": "Uniform emission on sloping Kashmir terrains from 0.8 to 3.5 bar pressure. Built-in labyrinth self-flushing design prevents silt and fertilizer blockage.",
        "stock_quantity": 90,
        "in_stock": True,
        "badge": "PC Anti-Clog",
    },
    {
        "name": "Venturi Fertilizer Injector Unit with Suction Assembly",
        "category": "Drip Irrigation",
        "size": "1-Inch BSP Male Inlet/Outlet with Rotameter",
        "price": 1450.0,
        "image_url": "https://images.unsplash.com/photo-1585314062340-f1a5a7c9328d?auto=format&fit=crop&w=600&q=80",
        "description": "Differential pressure suction injector for automated fertigation. Delivers soluble NPK and micro-nutrients directly to the root zone with pinpoint dosing.",
        "stock_quantity": 180,
        "in_stock": True,
        "badge": "High Precision",
    },
    {
        "name": "UV-Stabilized Crystal Anti-Hail Net",
        "category": "Hail Protection",
        "size": "4m Width x 100m Roll (4-Thread Cross Stitch)",
        "price": 8200.0,
        "image_url": "https://images.unsplash.com/photo-1530595467537-0b5996c41f2d?auto=format&fit=crop&w=600&q=80",
        "description": "High-density polyethylene (HDPE) crystal hail net. 85% light transmission prevents fruit sunburn while stopping stone hail up to 30mm diameter.",
        "stock_quantity": 75,
        "in_stock": True,
        "badge": "8-Year UV Shield",
    },
    {
        "name": "Max Tapener HT-R High-Density Tree Tying Gun",
        "category": "Tools & Nutrition",
        "size": "Light-Touch 420g Handheld Tool",
        "price": 2650.0,
        "image_url": "https://images.unsplash.com/photo-1530587191325-3db32d826c18?auto=format&fit=crop&w=600&q=80",
        "description": "Industry gold standard for tying central leaders and lateral branches to bamboo/trellis wire. 3x faster than manual knotting without girdling stems.",
        "stock_quantity": 110,
        "in_stock": True,
        "badge": "Leader Training",
    },
    {
        "name": "Felco No. 8 Professional Swiss Bypass Pruner",
        "category": "Tools & Nutrition",
        "size": "210mm (1-Inch Cutting Capacity)",
        "price": 4200.0,
        "image_url": "https://images.unsplash.com/photo-1589939705384-5185137a7f0f?auto=format&fit=crop&w=600&q=80",
        "description": "Angled cutting head for precision pruning in high-density spindle systems. Hardened Swiss steel blade ensures clean cuts that heal rapidly without disease ingress.",
        "stock_quantity": 60,
        "in_stock": True,
        "badge": "Swiss Made",
    },
    {
        "name": "Spring Steel High-Density Branch Spreaders (Pack of 50)",
        "category": "Tools & Nutrition",
        "size": "Pack of 50 (Mixed 20cm & 30cm lengths)",
        "price": 850.0,
        "image_url": "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?auto=format&fit=crop&w=600&q=80",
        "description": "Sharp notch spring wire spreaders to establish ideal 60-70 degree crotch angles on young high-density limbs for early floral bud differentiation.",
        "stock_quantity": 350,
        "in_stock": True,
        "badge": "Crotch Spreader",
    },
    {
        "name": "SKUAST-K Calcium-Boron High-Density Foliar Nutrition",
        "category": "Tools & Nutrition",
        "size": "5-Litre Can (11% Ca + 0.6% B Chelate)",
        "price": 1850.0,
        "image_url": "https://images.unsplash.com/photo-1628352081506-83c43123ed6d?auto=format&fit=crop&w=600&q=80",
        "description": "Formulated specifically for high-yielding M9/MM106 orchards to maximize cell density, stop bitter pit breakdown, and extend cold storage shelf-life to 8+ months.",
        "stock_quantity": 220,
        "in_stock": True,
        "badge": "Cell Wall Shield",
    },
]


async def seed_default_products(db: AsyncSession) -> None:
    """Pre-seeds the store products if table is currently empty."""
    existing_count = await db.scalar(select(func.count(StoreProduct.id)))
    if existing_count == 0:
        LOGGER.info("Seeding initial high-density orchard catalog...")
        for item in INITIAL_HD_PRODUCTS:
            prod = StoreProduct(**item)
            db.add(prod)
        await db.commit()
        LOGGER.info("Seeded %d high-density orchard products.", len(INITIAL_HD_PRODUCTS))


def admin_token_for(email: str) -> str:
    settings = get_settings()
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    return jwt.encode(
        {"sub": email, "role": "admin", "exp": expires},
        settings.jwt_secret,
        algorithm="HS256",
    )


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Verifies that the incoming token possesses the admin role."""
    settings = get_settings()
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=["HS256"])
        role = payload.get("role")
        sub = payload.get("sub")
        if role != "admin" and sub != settings.admin_email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Administrative privileges required",
            )
        return str(sub or "admin")
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired admin authorization token",
        ) from exc


# -------------------------------------------------------------------------
# Customer Endpoints
# -------------------------------------------------------------------------

@router.get("/products", response_model=List[ProductResponse])
async def list_products(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    in_stock_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
) -> List[StoreProduct]:
    """Retrieves all high-density orchard products with optional filtering."""
    query = select(StoreProduct)
    if category and category.lower() != "all":
        query = query.where(StoreProduct.category == category)
    if in_stock_only:
        query = query.where(StoreProduct.in_stock.is_(True))
    if search:
        pattern = f"%{search.strip()}%"
        query = query.where(
            (StoreProduct.name.ilike(pattern))
            | (StoreProduct.size.ilike(pattern))
            | (StoreProduct.description.ilike(pattern))
            | (StoreProduct.category.ilike(pattern))
        )
    query = query.order_by(StoreProduct.category, StoreProduct.name)
    result = await db.scalars(query)
    return list(result.all())


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: UUID, db: AsyncSession = Depends(get_db)) -> StoreProduct:
    """Retrieves a single product by UUID."""
    prod = await db.get(StoreProduct, product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    return prod


@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: OrderCreateRequest,
    db: AsyncSession = Depends(get_db),
) -> StoreOrder:
    """Customer places an order for high-density orchard products."""
    if not payload.items:
        raise HTTPException(status_code=400, detail="Order must contain at least one item")

    # Compute total and validate quantities
    total = 0.0
    items_dump = []
    for it in payload.items:
        line_total = round(it.price * it.quantity, 2)
        total += line_total
        items_dump.append({
            "product_id": str(it.product_id) if it.product_id else None,
            "name": it.name,
            "category": it.category,
            "size": it.size,
            "price": it.price,
            "quantity": it.quantity,
            "image_url": it.image_url,
            "total": line_total,
        })

    total = round(total, 2)
    # Generate unique human-readable order tracking ID (e.g., HD-2026-89241)
    year = datetime.now().year
    suffix = f"{int(time.time()) % 100000:05d}{random.randint(10, 99)}"
    order_number = f"HD-{year}-{suffix}"

    order = StoreOrder(
        order_number=order_number,
        customer_name=payload.customer_name.strip(),
        customer_phone=payload.customer_phone.strip(),
        customer_email=payload.customer_email.strip().lower() if payload.customer_email else None,
        district=payload.district.strip(),
        delivery_address=payload.delivery_address.strip(),
        items=items_dump,
        total_amount=total,
        payment_method=payload.payment_method or "Cash on Delivery",
        status="received",
        notes=payload.notes.strip() if payload.notes else None,
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    LOGGER.info("Customer created order %s for ₹%.2f (%s)", order_number, total, payload.district)
    return order


@router.get("/orders/track", response_model=List[OrderResponse])
async def track_orders(
    phone: Optional[str] = Query(None),
    order_number: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> List[StoreOrder]:
    """Allows customers to track their orders using their phone number or order tracking ID."""
    if not phone and not order_number:
        raise HTTPException(status_code=400, detail="Provide a phone number or order number to track")

    query = select(StoreOrder)
    if order_number:
        query = query.where(StoreOrder.order_number == order_number.strip().upper())
    elif phone:
        # Match by phone digits
        cleaned_phone = phone.strip()
        query = query.where(StoreOrder.customer_phone.ilike(f"%{cleaned_phone}%"))

    query = query.order_by(StoreOrder.created_at.desc())
    result = await db.scalars(query)
    return list(result.all())


# -------------------------------------------------------------------------
# Admin Endpoints (Separate Admin Portal)
# -------------------------------------------------------------------------

@router.post("/admin/login", response_model=AdminLoginResponse)
async def admin_login(payload: LoginRequest) -> AdminLoginResponse:
    """Authenticates the administrator for the separate high-density admin dashboard."""
    settings = get_settings()
    is_valid_email = payload.email.strip().lower() == settings.admin_email.lower()
    is_valid_pass = payload.password == settings.admin_password

    # Also allow standard admin username "admin" or email match
    if (payload.email.strip().lower() == "admin" or is_valid_email) and is_valid_pass:
        token = admin_token_for(settings.admin_email)
        LOGGER.info("Admin login successful for %s", settings.admin_email)
        return AdminLoginResponse(
            access_token=token,
            token_type="bearer",
            role="admin",
            email=settings.admin_email,
        )

    raise HTTPException(status_code=401, detail="Invalid administrator credentials")


@router.get("/admin/stats", response_model=AdminStatsResponse)
async def admin_stats(
    _: str = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Returns overview KPI metrics for the Admin Dashboard."""
    total_orders = await db.scalar(select(func.count(StoreOrder.id))) or 0
    received_orders = await db.scalar(select(func.count(StoreOrder.id)).where(StoreOrder.status == "received")) or 0
    confirmed_orders = await db.scalar(select(func.count(StoreOrder.id)).where(StoreOrder.status == "confirmed")) or 0
    dispatched_orders = await db.scalar(select(func.count(StoreOrder.id)).where(StoreOrder.status == "dispatched")) or 0
    delivered_orders = await db.scalar(select(func.count(StoreOrder.id)).where(StoreOrder.status == "delivered")) or 0
    cancelled_orders = await db.scalar(select(func.count(StoreOrder.id)).where(StoreOrder.status == "cancelled")) or 0

    # Total revenue (active non-cancelled orders)
    revenue_res = await db.scalar(
        select(func.sum(StoreOrder.total_amount)).where(StoreOrder.status != "cancelled")
    )
    total_revenue = round(float(revenue_res or 0.0), 2)

    total_prods = await db.scalar(select(func.count(StoreProduct.id))) or 0
    in_stock_prods = await db.scalar(select(func.count(StoreProduct.id)).where(StoreProduct.in_stock.is_(True))) or 0

    return {
        "total_orders": total_orders,
        "received_orders": received_orders,
        "confirmed_orders": confirmed_orders,
        "dispatched_orders": dispatched_orders,
        "delivered_orders": delivered_orders,
        "cancelled_orders": cancelled_orders,
        "total_revenue": total_revenue,
        "total_products": total_prods,
        "in_stock_products": in_stock_prods,
    }


@router.get("/admin/orders", response_model=List[OrderResponse])
async def admin_list_orders(
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    _: str = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> List[StoreOrder]:
    """Admin retrieves all customer orders, with optional status and customer filter."""
    query = select(StoreOrder)
    if status_filter and status_filter.lower() != "all":
        query = query.where(StoreOrder.status == status_filter.lower())
    if search:
        pat = f"%{search.strip()}%"
        query = query.where(
            (StoreOrder.order_number.ilike(pat))
            | (StoreOrder.customer_name.ilike(pat))
            | (StoreOrder.customer_phone.ilike(pat))
            | (StoreOrder.district.ilike(pat))
        )
    query = query.order_by(StoreOrder.created_at.desc())
    result = await db.scalars(query)
    return list(result.all())


@router.patch("/admin/orders/{order_id}/status", response_model=OrderResponse)
async def admin_update_order_status(
    order_id: UUID,
    payload: OrderStatusUpdateRequest,
    _: str = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> StoreOrder:
    """Admin updates the status of an order (received -> confirmed -> dispatched -> delivered -> cancelled)."""
    order = await db.get(StoreOrder, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = payload.status
    if payload.notes is not None:
        order.notes = payload.notes
    await db.commit()
    await db.refresh(order)
    LOGGER.info("Admin updated order %s status to '%s'", order.order_number, payload.status)
    return order


@router.post("/admin/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def admin_create_product(
    payload: ProductCreate,
    _: str = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> StoreProduct:
    """Admin adds a new high-density orchard product with type, size, photo, and price."""
    product = StoreProduct(
        name=payload.name.strip(),
        category=payload.category.strip(),
        size=payload.size.strip(),
        price=round(float(payload.price), 2),
        image_url=payload.image_url.strip(),
        description=payload.description.strip(),
        stock_quantity=payload.stock_quantity,
        in_stock=payload.in_stock,
        badge=payload.badge.strip() if payload.badge else None,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    LOGGER.info("Admin created new product '%s' (%s, %s, ₹%.2f)", product.name, product.category, product.size, product.price)
    return product


@router.put("/admin/products/{product_id}", response_model=ProductResponse)
async def admin_update_product(
    product_id: UUID,
    payload: ProductUpdate,
    _: str = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> StoreProduct:
    """Admin updates an existing product."""
    product = await db.get(StoreProduct, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if payload.name is not None:
        product.name = payload.name.strip()
    if payload.category is not None:
        product.category = payload.category.strip()
    if payload.size is not None:
        product.size = payload.size.strip()
    if payload.price is not None:
        product.price = round(float(payload.price), 2)
    if payload.image_url is not None:
        product.image_url = payload.image_url.strip()
    if payload.description is not None:
        product.description = payload.description.strip()
    if payload.stock_quantity is not None:
        product.stock_quantity = payload.stock_quantity
    if payload.in_stock is not None:
        product.in_stock = payload.in_stock
    if payload.badge is not None:
        product.badge = payload.badge.strip() if payload.badge else None

    await db.commit()
    await db.refresh(product)
    LOGGER.info("Admin updated product '%s' (ID: %s)", product.name, product.id)
    return product


@router.delete("/admin/products/{product_id}")
async def admin_delete_product(
    product_id: UUID,
    _: str = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Admin removes a product from the catalog."""
    product = await db.get(StoreProduct, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    await db.delete(product)
    await db.commit()
    LOGGER.info("Admin deleted product ID %s", product_id)
    return {"status": "deleted", "id": str(product_id), "name": product.name}


@router.post("/admin/products/upload-photo")
async def admin_upload_product_photo(
    file: UploadFile = File(...),
    _: str = Depends(get_current_admin),
) -> Dict[str, str]:
    """Admin uploads an image for a product. Returns an inline data URL or storage reference."""
    if file.content_type not in {"image/jpeg", "image/png", "image/webp", "image/jpg"}:
        raise HTTPException(status_code=415, detail="Only JPG, PNG, and WebP images are supported")

    content = await file.read(5 * 1024 * 1024 + 1)
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image must be under 5MB")

    # Encode as Base64 Data URL so it is fully standalone and portable across environments
    b64 = base64.b64encode(content).decode("ascii")
    data_url = f"data:{file.content_type};base64,{b64}"
    return {"url": data_url, "filename": file.filename or "product.jpg"}
