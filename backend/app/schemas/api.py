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
    cultural_measures: list[str] = Field(default_factory=list)
    alternatives: list[dict] = Field(default_factory=list)
    heatmap: dict = Field(default_factory=dict)
    recommendations: list[dict] = Field(default_factory=list)
    guardrails: list[str] = Field(default_factory=list)
    guard_details: Optional[dict] = None
