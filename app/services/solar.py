from typing import Dict, Any, Optional, Literal

AREA_PROFILES = {
    "cidco": 1200,
    "garkheda": 1400,
    "ulkanagari": 1600,
    "shreya nagar": 1800,
    "osmanpura": 900,
    "shahgunj": 700,
    "samarth nagar": 1000,
    "default": 1000
}

def get_area_from_address(address: str) -> float:
    """
    Match address against predefined area profiles to estimate roof size.
    """
    addr_lower = address.lower()
    for area, size in AREA_PROFILES.items():
        if area in addr_lower:
            return float(size)
    return float(AREA_PROFILES["default"])

def calculate_solar_estimate(
    address: str, 
    monthly_bill: Optional[float] = None,
    property_type: str = "independent",
    cv_analysis: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Generalized solar estimation model for Indian urban environments.
    Uses continuous mathematical scaling instead of hard thresholds for 
    improved reliability across different urban densities.
    """
    # 1. Base area detection
    roof_area_sqft = get_area_from_address(address)
    
    # 2. Normalize and Extract Signals
    # Signals are expected in range [0, 1]
    green_ratio = cv_analysis.get("green_ratio", 0.0) if cv_analysis else 0.0
    edge_density = cv_analysis.get("edge_density", 0.0) if cv_analysis else 0.0
    
    # 3. Smooth Scaling Logic (Signal Processing)
    
    # Urban Density Factor: Gradually reduces base roof area as density increases
    density_factor = 1.0 - (edge_density * 1.0) # Calibrated for higher sensitivity
    density_factor = max(0.7, min(density_factor, 1.0))
    
    # Usable Area Factor: Gradually reduces usable roof percentage as clutter increases
    usable_factor = 0.65 - (edge_density * 0.3) # Calibrated for more aggressive penalty
    usable_factor = max(0.45, min(usable_factor, 0.65))
    
    # Blended Shading Model: Combines tree and urban effects smoothly
    tree_component = 1.0 - green_ratio
    urban_component = 1.0 - (edge_density * 0.7) # Calibrated building shading
    
    shading_score = (0.5 * tree_component) + (0.5 * urban_component) # Balanced blend
    shading_score = max(0.65, min(shading_score, 0.82)) # Reduced max for realism

    # 4. Core Calculations
    adjusted_roof_area = roof_area_sqft * density_factor
    
    # Property Type Adjustment (Discrete but necessary)
    if property_type == "apartment":
        adjusted_roof_area *= 0.4
    
    usable_area = adjusted_roof_area * usable_factor
    system_size_kw = usable_area / 90.0
    
    # 5. Soft Constraints (Monthly Bill)
    if monthly_bill is not None:
        if monthly_bill < 1000:
            system_size_kw = min(system_size_kw, 2.5)
        elif monthly_bill > 5000:
            system_size_kw = max(system_size_kw, 3.0)

    # Realistic Bounds: 1 kW to 10 kW
    system_size_kw = max(1.0, min(10.0, round(system_size_kw, 2)))
    
    # 6. Financials
    annual_generation = system_size_kw * 1400 * shading_score
    annual_savings = annual_generation * 8
    total_cost = system_size_kw * 55000
    payback_years = total_cost / annual_savings if annual_savings > 0 else 0
    
    # 7. Refined Confidence Model
    # Calibrated to be more sensitive to high building density
    confidence_score = (edge_density * 0.7) + (green_ratio * 0.3)
    confidence = "medium" if confidence_score > 0.12 else "high"
        
    # 8. Explanation Generator
    if edge_density > 0.12:
        explanation = "Dense surroundings may reduce usable rooftop area and sunlight."
    elif green_ratio > 0.15:
        explanation = "Nearby trees may reduce solar generation."
    else:
        explanation = "Moderate rooftop conditions with balanced sunlight exposure."
    
    # 9. Return Conservative Ranges
    result = {
        "system_size_kw": {
            "min": round(system_size_kw * 0.85, 2),
            "max": round(system_size_kw * 1.05, 2) # Tightened for conservative output
        },
        "annual_savings": round(annual_savings, 2),
        "cost": round(total_cost, 2),
        "payback": round(payback_years, 2),
        "confidence": confidence,
        "explanation": explanation
    }

    if cv_analysis:
        result.update({
            "green_ratio": green_ratio,
            "edge_density": edge_density,
            "shading_score": round(shading_score, 2)
        })

    return result
