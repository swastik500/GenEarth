"""
Mobile API Endpoints
Comprehensive REST API for EcoMitra Mobile App
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image
from sqlalchemy.orm import Session

# Import existing functionality
from backend.ai.chain import get_rag_response
from backend.ai.waste_classifier import get_classifier
from backend.gamification import (
    award_points,
    get_user_profile,
    get_leaderboard
)
from backend.database import get_db

router = APIRouter(prefix="/api/mobile", tags=["Mobile API"])


# ============= REQUEST/RESPONSE MODELS =============

class ChatRequest(BaseModel):
    message: str
    language: str = "en"
    user_id: Optional[str] = None
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    timestamp: str
    language: str


class ImageAnalysisRequest(BaseModel):
    image_base64: str
    user_id: Optional[str] = None


class ImageAnalysisResponse(BaseModel):
    classification: str
    category: str
    disposal_method: str
    confidence: float
    environmental_impact: str
    recycling_tips: List[str]


class UserProfileRequest(BaseModel):
    username: str


class ActivityTrackRequest(BaseModel):
    username: str
    activity_type: str
    metadata: Optional[Dict[str, Any]] = None


class QuizAnswerRequest(BaseModel):
    username: str
    question_id: int
    answer: str


class MarketplaceItemRequest(BaseModel):
    title: str
    category: str
    description: str
    contact: Optional[str] = None
    user_id: str


class MarketplaceFilterRequest(BaseModel):
    category: Optional[str] = None
    search_query: Optional[str] = None
    limit: int = 20


class CarbonFootprintRequest(BaseModel):
    electricity: float
    gas: float
    fuel: float
    waste: float
    travel: float


# ============= AUTHENTICATION (Basic) =============

@router.post("/auth/login")
async def login(username: str = Form(...), device_id: Optional[str] = Form(None), db: Session = Depends(get_db)):
    """
    Basic authentication endpoint for mobile app
    Returns user profile if exists, creates new profile if not
    """
    try:
        profile = get_user_profile(db, username)
        return {
            "success": True,
            "user": profile,
            "token": f"eco_{username}_{device_id}",  # Simple token
            "message": "Login successful"
        }
    except Exception as e:
        # Create new user by tracking activity
        award_points(db, username, "profile_view", {"initial": True})
        profile = get_user_profile(db, username)
        return {
            "success": True,
            "user": profile,
            "token": f"eco_{username}_{device_id}",
            "message": "New profile created"
        }


# ============= CHAT API =============

@router.post("/chat", response_model=ChatResponse)
async def chat_with_bot(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Send message to EcoMitra chatbot
    Supports multiple languages
    """
    try:
        # Track activity if user_id provided
        if request.user_id:
            award_points(db, request.user_id, "chat_question", {"language": request.language})
        
        # Get response from chatbot
        result = get_rag_response(
            question=request.message,
            language=request.language,
            session_id=request.session_id,
            username=request.user_id
        )
        response = result.get("answer", "Sorry, I couldn't process that request.")
        
        return ChatResponse(
            response=response,
            timestamp=datetime.now().isoformat(),
            language=request.language
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.get("/chat/history/{user_id}")
async def get_chat_history(user_id: str, limit: int = 50):
    """
    Retrieve chat history for a user
    """
    # This would need to be implemented with a chat history storage
    return {
        "user_id": user_id,
        "history": [],
        "message": "Chat history storage not yet implemented"
    }


# ============= IMAGE ANALYSIS API =============

@router.post("/vision/analyze", response_model=ImageAnalysisResponse)
async def analyze_waste_image(request: ImageAnalysisRequest, db: Session = Depends(get_db)):
    """
    Analyze waste image and provide classification
    Accepts base64 encoded image
    """
    try:
        # Decode base64 image
        image_bytes = base64.b64decode(request.image_base64)
        image = Image.open(BytesIO(image_bytes))
        
        # Track activity
        if request.user_id:
            award_points(db, request.user_id, "image_analysis", {})
        
        # Classify image
        classifier = get_classifier()
        result = classifier.analyze(image)
        
        return ImageAnalysisResponse(
            classification=result.get("waste_type", "Unknown"),
            category=result.get("category", "Unknown"),
            disposal_method=result.get("disposal_method", "Consult local guidelines"),
            confidence=result.get("confidence", 0.0),
            environmental_impact=result.get("environmental_impact", ""),
            recycling_tips=result.get("recycling_tips", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image analysis error: {str(e)}")


@router.post("/vision/analyze-multipart")
async def analyze_waste_image_multipart(
    file: UploadFile = File(...),
    user_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Analyze waste image (multipart form-data)
    Alternative endpoint for file uploads
    """
    try:
        # Read image bytes
        image_bytes = await file.read()
        image = Image.open(BytesIO(image_bytes))
        
        # Track activity
        if user_id:
            award_points(db, user_id, "image_analysis", {})
        
        # Classify image
        classifier = get_classifier()
        result = classifier.analyze(image)
        
        return {
            "classification": result.get("waste_type", "Unknown"),
            "category": result.get("category", "Unknown"),
            "disposal_method": result.get("disposal_method", "Consult local guidelines"),
            "confidence": result.get("confidence", 0.0),
            "environmental_impact": result.get("environmental_impact", ""),
            "recycling_tips": result.get("recycling_tips", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image analysis error: {str(e)}")


# ============= GAMIFICATION API =============

@router.post("/profile", response_model=Dict)
async def get_profile(request: UserProfileRequest, db: Session = Depends(get_db)):
    """
    Get user profile with stats and badges
    """
    try:
        profile = get_user_profile(db, request.username)
        return profile
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Profile not found: {str(e)}")


@router.post("/activity/track")
async def track_user_activity(request: ActivityTrackRequest, db: Session = Depends(get_db)):
    """
    Track user activity for gamification
    Activity types: chat_question, image_analysis, ngo_view, scheme_view, quiz_complete
    """
    try:
        result = award_points(db, request.username, request.activity_type, request.metadata)
        return {
            "success": True,
            "message": "Activity tracked",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Activity tracking error: {str(e)}")


@router.get("/leaderboard")
async def get_leaderboard_data(limit: int = 10, db: Session = Depends(get_db)):
    """
    Get global leaderboard
    """
    try:
        leaderboard = get_leaderboard(db, limit)
        return {"leaderboard": leaderboard}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Leaderboard error: {str(e)}")


@router.post("/quiz/answer")
async def submit_quiz_answer(request: QuizAnswerRequest):
    """
    Submit quiz answer and get result
    """
    try:
        result = check_quiz_answer(request.username, request.question_id, request.answer)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quiz error: {str(e)}")


# ============= NGO & GOVERNMENT SCHEMES API =============

@router.get("/ngos")
async def get_ngos(category: Optional[str] = None, location: Optional[str] = None):
    """
    Get list of NGOs
    Optional filters: category, location
    """
    from backend.routers.ngos import get_ngos as fetch_ngos
    
    try:
        ngos = fetch_ngos()
        
        # Apply filters
        if category:
            ngos = [ngo for ngo in ngos if ngo.get("category") == category]
        if location:
            ngos = [ngo for ngo in ngos if location.lower() in ngo.get("location", "").lower()]
        
        return {
            "count": len(ngos),
            "ngos": ngos
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NGO fetch error: {str(e)}")


@router.get("/government/schemes")
async def get_government_schemes(category: Optional[str] = None, state: Optional[str] = None):
    """
    Get list of government schemes
    Optional filters: category, state
    """
    from backend.routers.government import get_schemes as fetch_schemes
    
    try:
        schemes = fetch_schemes()
        
        # Apply filters
        if category:
            schemes = [s for s in schemes if s.get("category") == category]
        if state:
            schemes = [s for s in schemes if state.lower() in s.get("states", "").lower()]
        
        return {
            "count": len(schemes),
            "schemes": schemes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schemes fetch error: {str(e)}")


# ============= MARKETPLACE API =============

@router.post("/marketplace/items")
async def create_marketplace_item(request: MarketplaceItemRequest, db: Session = Depends(get_db)):
    """
    Create new marketplace listing
    """
    try:
        from backend.models import MarketplaceItem
        
        item = MarketplaceItem(
            title=request.title,
            category=request.category,
            description=request.description,
            contact=request.contact,
            posted_by=request.user_id
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        
        return {
            "success": True,
            "item_id": item.id,
            "message": "Item posted successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Marketplace error: {str(e)}")


@router.get("/marketplace/items")
async def get_marketplace_items(
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get marketplace items with optional filters
    """
    try:
        from backend.models import MarketplaceItem
        
        query = db.query(MarketplaceItem)
        
        if category:
            query = query.filter(MarketplaceItem.category == category)
        if search:
            query = query.filter(MarketplaceItem.title.contains(search))
        
        items = query.limit(limit).all()
        
        return {
            "count": len(items),
            "items": [
                {
                    "id": item.id,
                    "title": item.title,
                    "category": item.category,
                    "description": item.description,
                    "contact": item.contact,
                    "posted_by": item.posted_by,
                    "created_at": item.created_at.isoformat() if item.created_at else None
                }
                for item in items
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Marketplace fetch error: {str(e)}")


# ============= CARBON FOOTPRINT API =============

@router.post("/carbon/calculate")
async def calculate_carbon_footprint(request: CarbonFootprintRequest):
    """
    Calculate carbon footprint based on user inputs
    Returns total carbon footprint and breakdown
    """
    try:
        # Carbon emission factors (kg CO2)
        electricity_factor = 0.92  # per kWh
        gas_factor = 5.3  # per therm
        fuel_factor = 2.31  # per liter
        waste_factor = 0.57  # per kg
        travel_factor = 0.14  # per km
        
        # Calculate emissions
        electricity_emission = request.electricity * electricity_factor
        gas_emission = request.gas * gas_factor
        fuel_emission = request.fuel * fuel_factor
        waste_emission = request.waste * waste_factor
        travel_emission = request.travel * travel_factor
        
        total = electricity_emission + gas_emission + fuel_emission + waste_emission + travel_emission
        
        # Generate recommendations
        recommendations = []
        if electricity_emission > 100:
            recommendations.append("Switch to LED bulbs and energy-efficient appliances")
        if fuel_emission > 50:
            recommendations.append("Consider carpooling or using public transport")
        if waste_emission > 30:
            recommendations.append("Reduce waste by composting and recycling")
        
        return {
            "total_carbon_kg": round(total, 2),
            "breakdown": {
                "electricity": round(electricity_emission, 2),
                "gas": round(gas_emission, 2),
                "fuel": round(fuel_emission, 2),
                "waste": round(waste_emission, 2),
                "travel": round(travel_emission, 2)
            },
            "recommendations": recommendations,
            "rating": "Good" if total < 500 else "Moderate" if total < 1000 else "High"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Carbon calculation error: {str(e)}")


# ============= APP CONFIG API =============

@router.get("/config")
async def get_app_config():
    """
    Get app configuration for mobile
    Returns supported languages, categories, etc.
    """
    return {
        "languages": [
            {"code": "en", "name": "English"},
            {"code": "hi", "name": "हिंदी (Hindi)"},
            {"code": "mr", "name": "मराठी (Marathi)"},
            {"code": "bn", "name": "বাংলা (Bengali)"},
            {"code": "ta", "name": "தமிழ் (Tamil)"},
            {"code": "te", "name": "తెలుగు (Telugu)"},
            {"code": "gu", "name": "ગુજરાતી (Gujarati)"},
            {"code": "kn", "name": "ಕನ್ನಡ (Kannada)"},
            {"code": "ml", "name": "മലയാളം (Malayalam)"},
            {"code": "pa", "name": "ਪੰਜਾਬੀ (Punjabi)"},
        ],
        "marketplace_categories": [
            "cardboard", "scrap", "clothing", "electronics",
            "plastic", "paper", "metal", "glass"
        ],
        "ngo_categories": [
            "waste_management", "water_conservation", "tree_plantation",
            "renewable_energy", "wildlife_protection", "education"
        ],
        "waste_categories": [
            "biodegradable", "recyclable", "hazardous", "e-waste",
            "plastic", "paper", "metal", "glass"
        ],
        "api_version": "1.0.0",
        "features": [
            "chat", "image_analysis", "gamification", "marketplace",
            "ngos", "government_schemes", "carbon_calculator"
        ]
    }


# ============= DOCUMENTATION =============

@router.get("/docs/endpoints")
async def get_api_documentation():
    """
    Get comprehensive API documentation for mobile developers
    """
    return {
        "base_url": "/api/mobile",
        "authentication": "Basic token-based (eco_{username}_{device_id})",
        "endpoints": {
            "Authentication": {
                "POST /auth/login": "Login or create user profile",
            },
            "Chat": {
                "POST /chat": "Send message to chatbot",
                "GET /chat/history/{user_id}": "Get chat history"
            },
            "Image Analysis": {
                "POST /vision/analyze": "Analyze waste image (base64)",
                "POST /vision/analyze-multipart": "Analyze waste image (file upload)"
            },
            "Gamification": {
                "POST /profile": "Get user profile",
                "POST /activity/track": "Track user activity",
                "GET /leaderboard": "Get leaderboard",
                "POST /quiz/answer": "Submit quiz answer"
            },
            "NGOs & Government": {
                "GET /ngos": "Get NGO list",
                "GET /government/schemes": "Get government schemes"
            },
            "Marketplace": {
                "POST /marketplace/items": "Create listing",
                "GET /marketplace/items": "Get listings"
            },
            "Carbon": {
                "POST /carbon/calculate": "Calculate carbon footprint"
            },
            "Config": {
                "GET /config": "Get app configuration"
            }
        }
    }
