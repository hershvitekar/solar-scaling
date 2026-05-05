# Solar Rooftop Pre-Screening API (Production MVP)

A high-fidelity solar potential estimation engine designed for dense Indian urban environments like Chhatrapati Sambhajinagar. It uses a combination of geocoding, satellite image computer vision (CV), and generalized urban heuristics to provide realistic, conservative estimates.

## 🔄 Logic Flow

```text
[POST /estimate]
       |
       v
[Address Geocoding] ----(Fail)----> [400 Bad Request]
       |
    (Success)
       |
[Nearby Cache Check] ---(Hit)-----> [Return Cached Result]
       |
    (Miss)
       |
[Satellite Image Fetch]
       |
[CV Analysis Layer] (Green Ratio + Edge Density)
       |
[Generalized Heuristic Model] (Smooth Scaling)
       |
[Financial Calculations]
       |
[Database Save]
       |
[Return Response]
```

## 🚀 Key Features

- **Satellite CV Analysis**: 
    - **Green Ratio**: Detects foliage to calculate shading penalties.
    - **Edge Density**: Detects rooftop clutter (water tanks, staircases) and urban density to adjust usable area.
- **Generalized Urban Model**: No hard thresholds. Uses continuous mathematical scaling to ensure smooth estimation across different neighborhoods.
- **Lazy Mapping (Caching)**: Reuses nearby computations (50m radius) to optimize performance and reduce API costs.
- **Financial Intelligence**: Tailored for India with ₹55k/kW cost, 1400 units/kW generation, and ₹8/unit electricity rate.
- **Dynamic Explanations**: Provides human-readable reasoning for each estimate (e.g., mentioning dense surroundings or foliage).

## 🛠️ Installation & Setup

### 1. Prerequisites
- Python 3.10+
- Google Maps API Key (Geocoding + Static Maps enabled)

### 2. Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "GOOGLE_MAPS_API_KEY=your_key_here" > .env
echo "DATABASE_URL=sqlite:///./solar_app.db" >> .env
```

### 3. Run
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📝 API Usage

### POST `/estimate`
**Request:**
```json
{
  "address": "Prozone Mall, Chhatrapati Sambhajinagar",
  "monthly_bill": 3500,
  "property_type": "independent"
}
```

**Response:**
```json
{
  "latitude": 19.8768,
  "longitude": 75.3720,
  "system_size_kw": {
    "min": 7.37,
    "max": 9.06
  },
  "annual_savings": 97104.0,
  "cost": 476850.0,
  "payback": 4.91,
  "confidence": "high",
  "explanation": "Moderate rooftop conditions with balanced sunlight exposure.",
  "source": "computed"
}
```

## 🧠 Future Roadmap (Internal Notes)
- **Alembic Migrations**: For production schema updates.
- **Seasonal Solar Variation**: Adjust generation estimates by month.
- **Sun-Angle Modeling**: Use building height approximations for precise shading.
- **Rooftop Segmentation**: Use ML for precise pixel-level roof boundary detection.