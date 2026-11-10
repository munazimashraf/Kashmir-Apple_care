from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text, Uuid, JSON, func
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
    district: Mapped[str | None] = mapped_column(String(80), nullable=True)
    owner: Mapped[User] = relationship(back_populates="orchards")


class Diagnosis(Base):
    __tablename__ = "diagnoses"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    orchard_id: Mapped[UUID | None] = mapped_column(ForeignKey("orchards.id", ondelete="SET NULL"), nullable=True)
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
    orchard_id: Mapped[UUID | None] = mapped_column(ForeignKey("orchards.id", ondelete="SET NULL"), nullable=True)
    product: Mapped[str] = mapped_column(String(160))
    dosage: Mapped[str] = mapped_column(String(120))
    sprayed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class WeatherHistory(Base):
    __tablename__ = "weather_history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    orchard_id: Mapped[UUID] = mapped_column(ForeignKey("orchards.id", ondelete="CASCADE"), index=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    provider: Mapped[str] = mapped_column(String(40))
    payload: Mapped[dict] = mapped_column(JSON)


Index("ix_diagnoses_user_created", Diagnosis.user_id, Diagnosis.created_at)
Index("ix_spray_logs_orchard_date", SprayLog.orchard_id, SprayLog.sprayed_at)
