from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from .database import Base

class SolarEstimate(Base):
    __tablename__ = "solar_estimates"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    system_size_kw = Column(Float)
    annual_savings = Column(Float)
    cost = Column(Float)
    payback = Column(Float)
    confidence = Column(String)
    green_ratio = Column(Float, nullable=True)
    edge_density = Column(Float, nullable=True)
    shading_score = Column(Float, nullable=True)
    explanation = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
