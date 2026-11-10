from datetime import datetime
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
    district: str | None = Field(default=None, max_length=80)


class OrchardResponse(OrchardCreate):
    id: UUID

    model_config = {"from_attributes": True}


class SprayLogCreate(BaseModel):
    orchard_id: UUID | None = None
    product: str = Field(min_length=1, max_length=160)
    dosage: str = Field(min_length=1, max_length=120)
    sprayed_at: datetime
    notes: str | None = None


class AdvisoryRequest(BaseModel):
    disease: str
    growth_stage: str
    rain_within_12_hours: bool


class DiagnoseResponse(BaseModel):
    disease: str
    confidence: float
    heatmap: dict
    recommendations: list[dict]
    guardrails: list[str]


class ImageDiagnoseResponse(BaseModel):
    ai_engine: str | None = None
    crop: str | None = None
    crop_name: str | None = None
    image_subject: str
    disease: str
    disease_name: str
    kashmiri_name: str | None = None
    category: str
    pathogen: str | None = None
    urgency: str | None = None
    confidence: float
    scab_percent: float
    severity_grade: str | None = None
    details: str
    scab_details: str
    hotspots: list[dict] = Field(default_factory=list)
    top_predictions: list[dict] = Field(default_factory=list)
    other_findings: list[dict] = Field(default_factory=list)
    recommendations: list[dict] = Field(default_factory=list)
    guardrails: list[str] = Field(default_factory=list)


class AppleDiseaseDetectResponse(BaseModel):
    disease: str
    scientific_name: str
    confidence: str  # "high" | "medium" | "low" | "uncertain"
    severity: str    # "none" | "mild" | "moderate" | "severe"
    symptoms: list[str] = Field(default_factory=list)
    visual_observations: list[str] = Field(default_factory=list)
    treatment: list[str] = Field(default_factory=list)
    prevention: list[str] = Field(default_factory=list)
    expert_consultation: bool = True
    ai_engine: str | None = None
    hotspots: list[dict] = Field(default_factory=list)
    confidence_numeric: float | None = None
    scab_percent: float | None = None
