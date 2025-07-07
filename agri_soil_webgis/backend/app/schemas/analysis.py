from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.schemas.soil_data import GeoJSON

class SoilAnalysisResult(BaseModel):
    location: GeoJSON
    quality_index: float = Field(..., ge=0, le=100)
    fertility_level: str
    recommendations: List[str]
    analysis_date: datetime

class CropSuitabilityResult(BaseModel):
    crop_name: str
    suitability_score: float = Field(..., ge=0, le=100)
    suitability_level: str
    limiting_factors: List[str]
    recommended_varieties: List[str]

class ErosionRiskResult(BaseModel):
    location: GeoJSON
    risk_level: str
    risk_score: float = Field(..., ge=0, le=100)
    annual_soil_loss: float  # tons per hectare per year
    contributing_factors: List[str]
    mitigation_strategies: List[str]