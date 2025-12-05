from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import base64
import os
import requests

from backend.database import get_db

router = APIRouter(prefix="/api/trash", tags=["carbon-footprint"])

def _get_api_key(provided_key: Optional[str] = None) -> str:
    key = provided_key or os.getenv("ROBOFLOW_API_KEY")
    if not key:
        raise HTTPException(status_code=400, detail="ROBOFLOW_API_KEY not set. Provide via env or request.")
    return key

def _infer_with_roboflow_bytes(image_bytes: bytes, mime: str, api_key: str) -> Dict[str, Any]:
    # Use direct HTTP multipart to Roboflow serverless endpoint
    model_id = "garbage_detection-wvzwv/9"
    url = f"https://detect.roboflow.com/{model_id}?api_key={api_key}&format=json"
    files = {"file": ("image", image_bytes, mime)}
    resp = requests.post(url, files=files, timeout=30)
    try:
        resp.raise_for_status()
    except Exception:
        raise HTTPException(status_code=502, detail=f"Roboflow API error: {resp.status_code} {resp.text}")
    return resp.json()

# Simple CO2e factors (kg CO2e per item approximation). These are illustrative, not authoritative.
CO2E_FACTORS = {
    "plastic": 0.06,    # small plastic item
    "paper": 0.02,
    "cardboard": 0.03,
    "metal": 0.1,       # can or similar
    "glass": 0.04,
    "organic": 0.5,     # methane potential (if landfilled)
    "battery": 1.0,
    "electronics": 2.0,
}

RECYCLE_REDUCTION = {
    "plastic": 0.3,     # 30% emissions avoided via recycling vs virgin production
    "paper": 0.6,
    "cardboard": 0.6,
    "metal": 0.9,
    "glass": 0.3,
    # Organic composting vs landfill methane
    "organic": 0.7,
    "battery": 0.8,
    "electronics": 0.6,
}

def _class_to_category(label: str) -> str:
    l = label.lower()
    if any(k in l for k in ["plastic"]):
        return "plastic"
    if any(k in l for k in ["paper", "cardboard"]):
        return "paper" if "paper" in l else "cardboard"
    if any(k in l for k in ["metal", "can"]):
        return "metal"
    if "glass" in l:
        return "glass"
    if any(k in l for k in ["banana", "food", "organic", "leaf", "vegetable", "fruit"]):
        return "organic"
    if any(k in l for k in ["battery"]):
        return "battery"
    if any(k in l for k in ["phone", "electronics", "charger", "cable", "laptop"]):
        return "electronics"
    return "unknown"

def _estimate_carbon(items: list) -> Dict[str, Any]:
    total = 0.0
    potential_reduction = 0.0
    breakdown = []
    for it in items:
        cat = _class_to_category(it.get("label", ""))
        base = CO2E_FACTORS.get(cat, 0.01)  # nominal default
        reduce_ratio = RECYCLE_REDUCTION.get(cat, 0.2)
        total += base
        potential_reduction += base * reduce_ratio
        breakdown.append({
            "label": it.get("label"),
            "category": cat,
            "estimated_co2e_kg": round(base, 4),
            "reduction_if_recycled_kg": round(base * reduce_ratio, 4),
        })
    return {
        "estimated_total_co2e_kg": round(total, 4),
        "potential_reduction_kg": round(potential_reduction, 4),
        "items": breakdown,
    }

# Trash detection is intentionally disabled for now; carbon estimator is available as a standalone API.

@router.post("/estimate-carbon")
async def estimate_carbon(
    items: Optional[list] = Body(default=None, description="List of item labels or dicts with 'label'"),
):
    """Estimate carbon footprint directly from provided items without detection.

    Example body:
    { "items": ["plastic bottle", "paper", {"label": "metal can"}] }
    """
    if items is None:
        raise HTTPException(status_code=400, detail="Provide 'items' as a list of labels or objects.")

    normalized = []
    for it in items:
        if isinstance(it, str):
            normalized.append({"label": it})
        elif isinstance(it, dict):
            lab = it.get("label") or it.get("name") or "unknown"
            normalized.append({"label": lab})
        else:
            normalized.append({"label": "unknown"})

    carbon = _estimate_carbon(normalized)
    return JSONResponse({
        "items": normalized,
        "carbon_footprint": carbon,
        "message": "Carbon estimates are indicative; actual impact varies by weight, material, and processing."
    })
