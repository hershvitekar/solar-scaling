import numpy as np
import cv2
from PIL import Image
from typing import Dict, Tuple

def analyze_rooftop_image(img: Image.Image) -> Dict[str, float]:
    """
    Analyze satellite image for green coverage and clutter using CV heuristics.
    """
    # Convert PIL image to RGB mode first (ensures 3 channels)
    img = img.convert('RGB')
    # Convert PIL image to OpenCV format (BGR)
    open_cv_image = np.array(img)
    # Convert RGB to BGR
    open_cv_image = open_cv_image[:, :, ::-1].copy()
    
    # 1. Green Coverage Detection (Tree Proxy)
    # Logic: pixels where G > R and G > B
    b, g, r = cv2.split(open_cv_image)
    green_mask = (g > r) & (g > b) & (g > 40) # Threshold to avoid dark noise
    green_pixels = np.sum(green_mask)
    total_pixels = open_cv_image.shape[0] * open_cv_image.shape[1]
    green_ratio = float(green_pixels / total_pixels)
    
    # 2. Edge Density (Clutter Proxy)
    # Convert to grayscale
    gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
    # Apply Canny edge detection
    edges = cv2.Canny(gray, 100, 200)
    edge_density = float(np.mean(edges) / 255.0)
    
    # 3. Apply Heuristics
    # Shading Score (based on green ratio)
    if green_ratio > 0.25:
        shading_score = 0.7
    elif green_ratio > 0.15:
        shading_score = 0.8
    else:
        shading_score = 0.9
        
    # Usable Area Factor (based on edge density)
    if edge_density > 0.10: # High clutter
        usable_factor = 0.5
    elif edge_density > 0.05: # Medium clutter
        usable_factor = 0.6
    else: # Low clutter
        usable_factor = 0.7
        
    return {
        "green_ratio": round(green_ratio, 3),
        "edge_density": round(edge_density, 3),
        "shading_score": shading_score,
        "usable_factor": usable_factor
    }
