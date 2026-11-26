from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    preferred_language: Mapped[str] = mapped_column(String(8), default="en")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    orchards: Mapped[list["Orchard"]] = relationship(back_populates="owner", cascade="all, delete-orphan")


class Orchard(Base):
    __tablename__ = "orchards"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    district: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    owner: Mapped[User] = relationship(back_populates="orchards")


class Diagnosis(Base):
    __tablename__ = "diagnoses"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    orchard_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("orchards.id", ondelete="SET NULL"), nullable=True)
    disease: Mapped[str] = mapped_column(String(80), index=True)
    confidence: Mapped[float] = mapped_column(Float)
    growth_stage: Mapped[str] = mapped_column(String(40))
    image_sha256: Mapped[str] = mapped_column(String(64), index=True)
    heatmap: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SprayLog(Base):
    __tablename__ = "spray_logs"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    orchard_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("orchards.id", ondelete="SET NULL"), nullable=True)
    product: Mapped[str] = mapped_column(String(160))
    dosage: Mapped[str] = mapped_column(String(120))
    sprayed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class WeatherHistory(Base):
    __tablename__ = "weather_history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    orchard_id: Mapped[UUID] = mapped_column(ForeignKey("orchards.id", ondelete="CASCADE"), index=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    provider: Mapped[str] = mapped_column(String(40))
    payload: Mapped[dict] = mapped_column(JSON)


Index("ix_diagnoses_user_created", Diagnosis.user_id, Diagnosis.created_at)
Index("ix_spray_logs_orchard_date", SprayLog.orchard_id, SprayLog.sprayed_at)


class StoreProduct(Base):
    __tablename__ = "store_products"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(200), index=True)
    category: Mapped[str] = mapped_column(String(100), index=True)
    size: Mapped[str] = mapped_column(String(100))
    price: Mapped[float] = mapped_column(Float)
    image_url: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text)
    stock_quantity: Mapped[int] = mapped_column(Integer, default=50)
    in_stock: Mapped[bool] = mapped_column(Boolean, default=True)
    badge: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class StoreOrder(Base):
    __tablename__ = "store_orders"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    order_number: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    customer_name: Mapped[str] = mapped_column(String(160))
    customer_phone: Mapped[str] = mapped_column(String(30), index=True)
    customer_email: Mapped[Optional[str]] = mapped_column(String(320), nullable=True)
    district: Mapped[str] = mapped_column(String(80))
    delivery_address: Mapped[str] = mapped_column(Text)
    items: Mapped[list[dict]] = mapped_column(JSON)
    total_amount: Mapped[float] = mapped_column(Float)
    payment_method: Mapped[str] = mapped_column(String(40), default="Cash on Delivery")
    status: Mapped[str] = mapped_column(String(40), default="received", index=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


Index("ix_store_orders_customer_date", StoreOrder.customer_phone, StoreOrder.created_at)

