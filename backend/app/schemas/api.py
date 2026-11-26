from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterRequest(BaseModel):
    email: str
    password: str = Field(min_length=12, max_length=128)
    preferred_language: str = Field(default="en", pattern="^(en|ur)$")


class LoginRequest(BaseModel):
    email: str
    password: str


class OrchardCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    district: Optional[str] = Field(default=None, max_length=80)


class OrchardResponse(OrchardCreate):
    id: UUID

    model_config = {"from_attributes": True}


class SprayLogCreate(BaseModel):
    orchard_id: Optional[UUID] = None
    product: str = Field(min_length=1, max_length=160)
    dosage: str = Field(min_length=1, max_length=120)
    sprayed_at: datetime
    notes: Optional[str] = None


class AdvisoryRequest(BaseModel):
    disease: str
    growth_stage: str
    rain_within_12_hours: bool


class DiagnoseResponse(BaseModel):
    disease: str
    confidence: float
    uncertain: bool = False
    is_plant: bool = True
    inappropriate: bool = False
    error: Optional[str] = None
    disease_common: Optional[str] = None
    disease_scientific: Optional[str] = None
    kashmiri_name: Optional[str] = None
    variety: Optional[str] = "Red Delicious"
    root_type: Optional[str] = "Seedling (Standard Vigorous)"
    cultural_measures: list[str] = Field(default_factory=list)
    alternatives: list[dict] = Field(default_factory=list)
    heatmap: dict = Field(default_factory=dict)
    recommendations: list[dict] = Field(default_factory=list)
    guardrails: list[str] = Field(default_factory=list)
    guard_details: Optional[dict] = None
    model: Optional[str] = None
    ensemble_breakdown: Optional[dict] = None


class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    category: str = Field(min_length=1, max_length=100)
    size: str = Field(min_length=1, max_length=100)
    price: float = Field(ge=0)
    image_url: str = Field(min_length=1, max_length=500)
    description: str = Field(default="")
    stock_quantity: int = Field(default=50, ge=0)
    in_stock: bool = True
    badge: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    size: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    stock_quantity: Optional[int] = None
    in_stock: Optional[bool] = None
    badge: Optional[str] = None


class ProductResponse(ProductBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class OrderItemSchema(BaseModel):
    product_id: Optional[str] = None
    name: str
    category: Optional[str] = None
    size: Optional[str] = None
    price: float
    quantity: int = Field(default=1, ge=1)
    image_url: Optional[str] = None
    total: float


class OrderCreateRequest(BaseModel):
    customer_name: str = Field(min_length=1, max_length=160)
    customer_phone: str = Field(min_length=7, max_length=30)
    customer_email: Optional[str] = None
    district: str = Field(min_length=1, max_length=80)
    delivery_address: str = Field(min_length=3)
    items: list[OrderItemSchema] = Field(min_length=1)
    payment_method: str = Field(default="Cash on Delivery")
    notes: Optional[str] = None


class OrderResponse(BaseModel):
    id: UUID
    order_number: str
    customer_name: str
    customer_phone: str
    customer_email: Optional[str] = None
    district: str
    delivery_address: str
    items: list[dict]
    total_amount: float
    payment_method: str
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class OrderStatusUpdateRequest(BaseModel):
    status: str = Field(pattern="^(received|confirmed|dispatched|delivered|cancelled)$")
    notes: Optional[str] = None


class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str = "admin"
    email: str


class AdminStatsResponse(BaseModel):
    total_orders: int
    received_orders: int
    confirmed_orders: int
    dispatched_orders: int
    delivered_orders: int
    cancelled_orders: int
    total_revenue: float
    total_products: int
    in_stock_products: int

