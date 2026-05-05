from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from .models import SolarEstimate
from .schemas import EstimateRequest, EstimateResponse
from .services.geocode import get_coordinates
from .services.solar import calculate_solar_estimate
from .services.cache import get_nearby_estimate
from .services.image_fetch import fetch_satellite_image
from .services.image_analysis import analyze_rooftop_image

# Create database tables
Base.metadata.create_all(bind=engine)

# In-memory cache for satellite analysis results
# Format: {(lat, lon): cv_analysis_dict}
SATELLITE_CACHE = {}

app = FastAPI(title="Solar Rooftop Pre-Screening API", version="1.0.0")

@app.post("/estimate", response_model=EstimateResponse)
def estimate_solar(request: EstimateRequest, db: Session = Depends(get_db)):
    """
    Estimate solar potential for a given address.
    Reuse previous computations if a record exists within 50 meters.
    """
    # 1. Address -> Coordinates
    lat, lon = get_coordinates(request.address)
    if lat is None or lon is None:
        raise HTTPException(status_code=400, detail="Could not geocode the provided address.")

    # 2. Nearby Cache Check
    cached_record = get_nearby_estimate(db, lat, lon, radius_meters=50.0)
    if cached_record:
        # Reconstruct range from cached single value for backward compatibility
        base_size = cached_record.system_size_kw
        return EstimateResponse(
            latitude=cached_record.latitude,
            longitude=cached_record.longitude,
            system_size_kw={
                "min": round(base_size * 0.85, 2),
                "max": round(base_size * 1.15, 2)
            },
            annual_savings=cached_record.annual_savings,
            cost=cached_record.cost,
            payback=cached_record.payback,
            confidence=cached_record.confidence or "medium",
            green_ratio=cached_record.green_ratio,
            edge_density=cached_record.edge_density,
            shading_score=cached_record.shading_score,
            explanation=cached_record.explanation,
            source="cache"
        )

    # 3. Satellite Image Analysis (CV Layer)
    coord_key = (round(lat, 5), round(lon, 5))
    cv_analysis = SATELLITE_CACHE.get(coord_key)
    
    if not cv_analysis:
        img = fetch_satellite_image(lat, lon)
        if img:
            cv_analysis = analyze_rooftop_image(img)
            SATELLITE_CACHE[coord_key] = cv_analysis

    # 4. Solar Estimation Logic
    estimate = calculate_solar_estimate(
        address=request.address,
        monthly_bill=request.monthly_bill,
        property_type=request.property_type,
        cv_analysis=cv_analysis
    )

    # 5. Store New Result
    mid_point_size = (estimate["system_size_kw"]["min"] + estimate["system_size_kw"]["max"]) / 2
    
    new_estimate = SolarEstimate(
        address=request.address,
        latitude=lat,
        longitude=lon,
        system_size_kw=round(mid_point_size, 2),
        annual_savings=estimate["annual_savings"],
        cost=estimate["cost"],
        payback=estimate["payback"],
        confidence=estimate["confidence"],
        green_ratio=estimate.get("green_ratio"),
        edge_density=estimate.get("edge_density"),
        shading_score=estimate.get("shading_score"),
        explanation=estimate.get("explanation")
    )
    db.add(new_estimate)
    db.commit()
    db.refresh(new_estimate)

    return EstimateResponse(
        latitude=new_estimate.latitude,
        longitude=new_estimate.longitude,
        system_size_kw=estimate["system_size_kw"],
        annual_savings=new_estimate.annual_savings,
        cost=new_estimate.cost,
        payback=new_estimate.payback,
        confidence=new_estimate.confidence,
        green_ratio=new_estimate.green_ratio,
        edge_density=new_estimate.edge_density,
        shading_score=new_estimate.shading_score,
        explanation=new_estimate.explanation,
        source="computed"
    )

@app.get("/")
def health_check():
    return {"status": "healthy", "service": "Solar Scaling API"}
