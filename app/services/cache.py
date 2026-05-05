from sqlalchemy.orm import Session
from ..models import SolarEstimate
from ..utils.distance import haversine
from typing import Optional

def get_nearby_estimate(db: Session, lat: float, lon: float, radius_meters: float = 50.0) -> Optional[SolarEstimate]:
    """
    Check if a solar estimate already exists within a specified radius.
    """
    # FUTURE: Use spatial indexing (like PostGIS or R-tree) for larger datasets.
    # FUTURE: Implement area clustering to group nearby requests.
    
    # Basic implementation: Iterate through records (fine for MVP scale)
    estimates = db.query(SolarEstimate).all()
    for est in estimates:
        dist = haversine(lat, lon, est.latitude, est.longitude)
        if dist <= radius_meters:
            return est
    return None
