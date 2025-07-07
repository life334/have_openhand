from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class Geometry(BaseModel):
    type: str
    coordinates: List[float] | List[List[float]] | List[List[List[float]]]

class Feature(BaseModel):
    type: str = "Feature"
    geometry: Geometry
    properties: Dict[str, Any]
    id: Optional[str | int] = None

class FeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[Feature]