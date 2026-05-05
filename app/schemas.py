from pydantic import BaseModel
from typing import Optional, Dict, Literal

class EstimateRequest(BaseModel):
    address: str
    monthly_bill: Optional[float] = None
    property_type: Optional[Literal["independent", "apartment"]] = "independent"

class SystemSizeRange(BaseModel):
    min: float
    max: float

class EstimateResponse(BaseModel):
    latitude: float
    longitude: float
    system_size_kw: SystemSizeRange
    annual_savings: float
    cost: float
    payback: float
    confidence: Literal["low", "medium", "high"]
    green_ratio: Optional[float] = None
    edge_density: Optional[float] = None
    shading_score: Optional[float] = None
    explanation: Optional[str] = None
    source: str

    class Config:
        from_attributes = True
