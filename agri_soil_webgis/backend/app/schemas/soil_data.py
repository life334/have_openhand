from pydantic import BaseModel, Field
from typing import Dict, Optional, Any
from datetime import datetime

class GeoJSON(BaseModel):
    type: str
    coordinates: list

class SoilDataBase(BaseModel):
    location: GeoJSON
    soil_type: str
    ph_value: float = Field(..., ge=0, le=14)
    organic_matter: float = Field(..., ge=0)
    moisture: float = Field(..., ge=0, le=1)
    nitrogen: float = Field(..., ge=0)
    phosphorus: float = Field(..., ge=0)
    potassium: float = Field(..., ge=0)

class SoilDataCreate(SoilDataBase):
    pass

class SoilDataUpdate(BaseModel):
    location: Optional[GeoJSON] = None
    soil_type: Optional[str] = None
    ph_value: Optional[float] = Field(None, ge=0, le=14)
    organic_matter: Optional[float] = Field(None, ge=0)
    moisture: Optional[float] = Field(None, ge=0, le=1)
    nitrogen: Optional[float] = Field(None, ge=0)
    phosphorus: Optional[float] = Field(None, ge=0)
    potassium: Optional[float] = Field(None, ge=0)

class SoilData(SoilDataBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True