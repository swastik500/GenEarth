from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from fastapi import Body
from fastapi.responses import JSONResponse
import logging
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import base64
import os

from backend.database import get_db
from backend.ai.waste_classifier import get_classifier
from backend.waste_database import get_disposal_info
from backend.gamification import award_points

# We will use Google Generative AI SDK directly for vision
try:
    import google.generativeai as genai
except Exception:
    genai = None

router = APIRouter(prefix="/api/vision", tags=["vision"]) 

# Use Gemini for fallback when local classification is uncertain
SUPPORTED_MODEL = "gemini-1.5-flash"
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# Enable/disable local classification
USE_LOCAL_CLASSIFIER = os.environ.get("USE_LOCAL_CLASSIFIER", "true").lower() == "true"


def ensure_gemini_configured():
    if genai is None:
        raise HTTPException(status_code=500, detail="Gemini SDK not available. Install google-generativeai.")
    if not GOOGLE_API_KEY:
        raise HTTPException(status_code=400, detail="GOOGLE_API_KEY not set in environment.")
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to configure Gemini SDK: {e}")


def categorize_items(labels: List[str]) -> Dict[str, List[str]]:
    categories = {
        "organic": [],
        "dry_recyclables": [],
        "e_waste": [],
        "hazardous": [],
        "unknown": []
    }
    for l in labels:
        low = l.lower()
        if any(k in low for k in ["food", "leaf", "vegetable", "fruit", "organic", "wet"]):
            categories["organic"].append(l)
        elif any(k in low for k in ["paper", "plastic", "metal", "glass", "cardboard", "recyclable", "dry"]):
            categories["dry_recyclables"].append(l)
        elif any(k in low for k in ["battery", "electronics", "phone", "cable", "charger", "e-waste", "device"]):
            categories["e_waste"].append(l)
        elif any(k in low for k in ["medical", "chemical", "paint", "hazardous", "toxic"]):
            categories["hazardous"].append(l)
        else:
            categories["unknown"].append(l)
    return categories


def build_guidelines() -> Dict[str, Any]:
    return {
        "do": [
            "Segregate waste at source: organic vs recyclables vs e-waste vs hazardous",
            "Rinse recyclable containers to avoid contamination",
            "Use local e-waste collection centers for electronics and batteries",
            "Follow municipal guidelines for hazardous waste disposal"
        ],
        "dont": [
            "Do not mix batteries/electronics with regular trash",
            "Do not burn plastic or mixed waste",
            "Do not dump hazardous liquids into drains"
        ]
    }


# Prefer multipart file upload; base64 kept for compatibility
@router.post("/analyze")
async def analyze_image(
    image_base64: Optional[str] = Body(None),
    file: Optional[UploadFile] = File(None),
    notes: Optional[str] = Body(None),
    username: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Analyze uploaded waste image using local classifier + Gemini fallback."""
    
    if not image_base64 and not file:
        raise HTTPException(status_code=400, detail="Provide image_base64 or file upload")

    try:
        # Prepare image bytes and mime type
        if file is not None:
            content = await file.read()
            if not content:
                raise HTTPException(status_code=400, detail="Empty file upload")
            mime = (file.content_type or "image/jpeg").lower()
            raw = content
        else:
            if not image_base64:
                raise HTTPException(status_code=400, detail="No image provided")
            raw = base64.b64decode(image_base64)
            # Default mime if not provided via multipart
            mime = "image/jpeg"

        # Only allow common image types
        allowed_mimes = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
        if mime not in allowed_mimes:
            # Try to sniff basic header for PNG/JPEG/WEBP
            head = raw[:12]
            if head.startswith(b"\xff\xd8\xff"):
                mime = "image/jpeg"
            elif head.startswith(b"\x89PNG\r\n\x1a\n"):
                mime = "image/png"
            elif head[0:4] == b"RIFF" and head[8:12] == b"WEBP":
                mime = "image/webp"
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported image type: {mime}")

        # Convert to PIL Image
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(raw))
        
        # Step 1: Try local classification first (if enabled)
        use_gemini = True
        local_result = None
        
        if USE_LOCAL_CLASSIFIER:
            try:
                classifier = get_classifier()
                local_result = classifier.analyze(img, confidence_threshold=0.65)
                logging.info(f"Local classification result: {local_result.get('should_use_gemini', True)}")
                
                # If local classifier is confident, return its result
                if not local_result.get("should_use_gemini", True):
                    disposal_info = local_result.get("disposal_info", {})
                    item_data = local_result.get("item", {})
                    
                    result = {
                        "model": f"local-mobilenet (confidence: {local_result['confidence']:.2f})",
                        "probable_items": [local_result["predicted_label"]],
                        "categorized_items": {
                            local_result["waste_category"]: [local_result["predicted_label"]]
                        },
                        "environmental_guidance": [
                            f"Impact: {disposal_info.get('impact', 'N/A')}",
                            f"Disposal: {disposal_info.get('disposal', 'N/A')}"
                        ],
                        "do_dont": get_disposal_info(local_result["waste_category"]),
                        "local_classification": True
                    }
                    return JSONResponse(result)
            except Exception as e:
                logging.warning(f"Local classification failed: {e}")
                use_gemini = True
        
        # Step 2: Fall back to Gemini for detailed analysis
        ensure_gemini_configured()
        
        # Ask for clear, parseable output
        prompt = (
            "Analyze this waste/trash image. Identify all visible items and classify them. "
            "List each item clearly (e.g., 'plastic bottle', 'banana peel', 'battery'). "
            "Then explain: 1) environmental impact if mismanaged, 2) proper disposal/recycling methods. "
            "Be specific and concise."
        )
        if notes:
            prompt += f" User notes: {notes}"

        model = genai.GenerativeModel(SUPPORTED_MODEL)
        logging.info(f"Sending image to Gemini model={SUPPORTED_MODEL}, mime={mime}, size={len(raw)} bytes")
        
        response = model.generate_content([prompt, img])
        # Extract text safely across SDK versions
        text = ""
        try:
            text = getattr(response, "text", "") or ""
            if not text and hasattr(response, "candidates"):
                for cand in response.candidates or []:
                    content = getattr(cand, "content", None)
                    if content:
                        parts = getattr(content, "parts", [])
                        for part in parts:
                            if hasattr(part, "text") and part.text:
                                text += part.text
        except Exception as e:
            logging.warning(f"Error extracting text: {e}")
            text = ""
        
        if not text:
            raise HTTPException(status_code=502, detail="No content returned by Gemini. Try another image or check API quota.")

        # Parse the response into structured format
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        
        # Extract items (look for short phrases that look like item names)
        items: List[str] = []
        guidance_lines: List[str] = []
        in_guidance = False
        
        for ln in lines:
            lower = ln.lower()
            # Check if this line is about guidance/impact/disposal
            if any(keyword in lower for keyword in ["impact", "disposal", "recycling", "suggestion", "manage", "proper", "method"]):
                in_guidance = True
            
            if in_guidance:
                guidance_lines.append(ln)
            else:
                # Extract item names (short labels, remove numbering/bullets)
                clean = ln.lstrip("•-*0123456789. ")
                if 3 < len(clean) <= 80 and not clean.endswith(":"):
                    items.append(clean)
        
        # Categorize items
        categorized = categorize_items(items)
        guidelines = build_guidelines()

        result = {
            "model": SUPPORTED_MODEL,
            "probable_items": items,
            "categorized_items": categorized,
            "environmental_guidance": guidance_lines,
            "do_dont": guidelines
        }
        
        # Award points for image analysis (gamification)
        if username:
            try:
                award_points(
                    db=db,
                    username=username,
                    activity_type="image_analysis",
                    metadata={"items_count": len(items)}
                )
            except Exception as e:
                logging.error(f"Gamification error: {str(e)}")
        
        return JSONResponse(result)

    except HTTPException:
        raise
    except Exception as e:
        # Provide more actionable error message
        err = str(e)
        if "rate" in err.lower() or "quota" in err.lower():
            raise HTTPException(status_code=429, detail="Gemini rate limit/quota exceeded.")
        logging.exception("Vision analysis failed")
        raise HTTPException(status_code=500, detail=f"Vision analysis failed: {err}")
