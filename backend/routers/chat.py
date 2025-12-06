from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

from backend.database import get_db
from backend.models import ChatSession, ChatMessage, NGO, GovernmentScheme
from backend.ai.chain import get_rag_response, simple_query
from backend.quiz_data import get_quiz_questions
from backend.gamification import award_points

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    language: str = "en"
    session_id: Optional[str] = None
    username: Optional[str] = None  # Optional username for gamification


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    mode: str  # "normal" or "quiz"
    quiz_data: Optional[dict] = None


def detect_intent(message: str) -> dict:
    """Detect user intent from message"""
    message_lower = message.lower()
    
    intents = {
        "ngo": ["ngo", "organization", "संगठन", "संस्था"],
        "scheme": ["scheme", "yojana", "योजना", "subsidy", "सब्सिडी", "incentive"],
        "quiz": ["quiz", "test", "प्रश्नोत्तरी", "क्विज"],
        "recycling": ["recycle", "रीसाइकल", "कचरा", "waste"],
        "energy": ["energy", "ऊर्जा", "electricity", "बिजली"],
        "pollution": ["pollution", "प्रदूषण", "air quality"]
    }
    
    detected = []
    for intent, keywords in intents.items():
        if any(keyword in message_lower for keyword in keywords):
            detected.append(intent)
    
    return {
        "primary": detected[0] if detected else "general",
        "all": detected
    }


def handle_ngo_query(message: str, language: str, db: Session) -> str:
    """Handle NGO-related queries"""
    message_lower = message.lower()
    
    # Extract location if mentioned
    query = db.query(NGO)
    
    # Simple keyword matching for cities/states
    indian_states = ["maharashtra", "delhi", "karnataka", "tamil nadu", "gujarat", "rajasthan", "punjab"]
    indian_cities = ["mumbai", "pune", "delhi", "bangalore", "chennai", "hyderabad", "ahmedabad"]
    
    for state in indian_states:
        if state in message_lower:
            query = query.filter(NGO.state.ilike(f"%{state}%"))
            break
    
    for city in indian_cities:
        if city in message_lower:
            query = query.filter(NGO.city.ilike(f"%{city}%"))
            break
    
    ngos = query.limit(5).all()
    
    if not ngos:
        if language == "hi":
            return "मुझे आपकी खोज से मेल खाने वाले NGO नहीं मिले। कृपया /ngos पेज पर जाकर फ़िल्टर का उपयोग करें।"
        elif language == "mr":
            return "मला तुमच्या शोधाशी जुळणारे NGO सापडले नाहीत. कृपया /ngos पृष्ठावर जाऊन फिल्टर वापरा."
        else:
            return "I couldn't find NGOs matching your search. Please visit the /ngos page to use filters."
    
    # Format response
    if language == "hi":
        response = "यहाँ कुछ पर्यावरणीय NGO हैं:\n\n"
    elif language == "mr":
        response = "येथे काही पर्यावरणीय NGO आहेत:\n\n"
    else:
        response = "Here are some environmental NGOs:\n\n"
    
    for ngo in ngos:
        response += f"🌿 **{ngo.name}**\n"
        response += f"📍 {ngo.city}, {ngo.state}\n"
        response += f"🏷️ {ngo.category}\n"
        if ngo.contact_phone:
            response += f"📞 {ngo.contact_phone}\n"
        response += "\n"
    
    if language == "hi":
        response += "\nअधिक विकल्पों के लिए /ngos पेज देखें।"
    elif language == "mr":
        response += "\nअधिक पर्यायांसाठी /ngos पृष्ठ पहा."
    else:
        response += "\nVisit /ngos page for more options."
    
    return response


def handle_scheme_query(message: str, language: str, db: Session) -> str:
    """Handle government scheme queries"""
    message_lower = message.lower()
    
    # Search schemes
    query = db.query(GovernmentScheme)
    
    # Keyword matching
    if any(word in message_lower for word in ["solar", "सौर"]):
        query = query.filter(GovernmentScheme.category.ilike("%solar%"))
    elif any(word in message_lower for word in ["ev", "electric vehicle", "इलेक्ट्रिक"]):
        query = query.filter(GovernmentScheme.category.ilike("%vehicle%"))
    
    schemes = query.limit(3).all()
    
    if not schemes:
        # Use RAG for general scheme info
        return get_rag_response(message, language)["answer"]
    
    # Format response
    if language == "hi":
        response = "यहाँ कुछ सरकारी योजनाएं हैं:\n\n"
    elif language == "mr":
        response = "येथे काही सरकारी योजना आहेत:\n\n"
    else:
        response = "Here are some government schemes:\n\n"
    
    for scheme in schemes:
        response += f"🏛️ **{scheme.name}**\n"
        response += f"📍 {scheme.state}\n"
        response += f"📝 {scheme.summary[:150]}...\n"
        if scheme.official_url:
            response += f"🔗 {scheme.official_url}\n"
        response += "\n"
    
    if language == "hi":
        response += "\n⚠️ कृपया आधिकारिक वेबसाइट पर विवरण सत्यापित करें।"
    elif language == "mr":
        response += "\n⚠️ कृपया अधिकृत वेबसाइटवर तपशील सत्यापित करा."
    else:
        response += "\n⚠️ Please verify details on official websites."
    
    return response


def handle_quiz_mode(session: ChatSession, message: str, language: str, db: Session, username: Optional[str] = None) -> dict:
    """Handle quiz mode interaction"""
    questions = get_quiz_questions(language)
    
    # Check if answering a question
    if session.quiz_index > 0 and session.quiz_index <= len(questions):
        # Process answer (expect A, B, C, D or 1, 2, 3, 4)
        answer_map = {"a": 0, "b": 1, "c": 2, "d": 3, "1": 0, "2": 1, "3": 2, "4": 3}
        user_answer = message.strip().lower()
        
        if user_answer in answer_map:
            prev_question = questions[session.quiz_index - 1]
            is_correct = answer_map[user_answer] == prev_question["correct"]
            
            if is_correct:
                session.quiz_score += 1
            
            # Prepare feedback
            if language == "hi":
                feedback = "✅ सही!" if is_correct else "❌ गलत"
                feedback += f"\n\n💡 {prev_question['explanation']}\n\n"
            elif language == "mr":
                feedback = "✅ बरोबर!" if is_correct else "❌ चूक"
                feedback += f"\n\n💡 {prev_question['explanation']}\n\n"
            else:
                feedback = "✅ Correct!" if is_correct else "❌ Incorrect"
                feedback += f"\n\n💡 {prev_question['explanation']}\n\n"
        else:
            if language == "hi":
                feedback = "⚠️ कृपया A, B, C, या D चुनें।\n\n"
            elif language == "mr":
                feedback = "⚠️ कृपया A, B, C, किंवा D निवडा.\n\n"
            else:
                feedback = "⚠️ Please choose A, B, C, or D.\n\n"
            
            # Don't advance quiz
            current_question = questions[session.quiz_index - 1]
            return {
                "reply": feedback,
                "mode": "quiz",
                "quiz_data": {
                    "question_num": session.quiz_index,
                    "total": len(questions),
                    "question": current_question["question"],
                    "options": current_question["options"],
                    "score": session.quiz_score
                }
            }
    else:
        feedback = ""
    
    # Check if quiz finished
    if session.quiz_index >= len(questions):
        session.active_mode = "normal"
        session.quiz_index = 0
        score = session.quiz_score
        total = len(questions)
        session.quiz_score = 0
        db.commit()
        
        # Award points for quiz completion (only if passed with 60%+)
        if score >= total * 0.6 and username:
            try:
                award_points(
                    db=db,
                    username=username,
                    activity_type="quiz_complete",
                    metadata={"score": score, "total": total}
                )
                feedback += "\n\n🏆 +10 EcoScore points for completing the quiz!\n"
            except Exception as e:
                print(f"Gamification error: {str(e)}")
        
        if language == "hi":
            summary = f"{feedback}🎉 क्विज पूरी हुई!\n\n📊 आपका स्कोर: {score}/{total}\n\n"
            if score == total:
                summary += "🌟 उत्कृष्ट! सभी उत्तर सही हैं!"
            elif score >= total * 0.6:
                summary += "👏 बहुत अच्छा! आप पर्यावरण के बारे में अच्छी जानकारी रखते हैं।"
            else:
                summary += "💪 कोशिश जारी रखें! और अधिक सीखने के लिए मुझसे प्रश्न पूछें।"
        elif language == "mr":
            summary = f"{feedback}🎉 क्विझ पूर्ण झाली!\n\n📊 तुमचा स्कोअर: {score}/{total}\n\n"
            if score == total:
                summary += "🌟 उत्कृष्ट! सर्व उत्तरे बरोबर आहेत!"
            elif score >= total * 0.6:
                summary += "👏 खूप चांगले! तुम्हाला पर्यावरणाविषयी चांगली माहिती आहे."
            else:
                summary += "💪 प्रयत्न सुरू ठेवा! अधिक शिकण्यासाठी मला प्रश्न विचारा."
        else:
            summary = f"{feedback}🎉 Quiz Complete!\n\n📊 Your Score: {score}/{total}\n\n"
            if score == total:
                summary += "🌟 Excellent! Perfect score!"
            elif score >= total * 0.6:
                summary += "👏 Great job! You have good environmental knowledge."
            else:
                summary += "💪 Keep learning! Ask me more questions to improve."
        
        return {
            "reply": summary,
            "mode": "normal",
            "quiz_data": None
        }
    
    # Show next question
    current_question = questions[session.quiz_index]
    session.quiz_index += 1
    db.commit()
    
    options_text = "\n".join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(current_question["options"])])
    
    if language == "hi":
        question_text = f"{feedback}❓ प्रश्न {session.quiz_index}/{len(questions)}\n\n{current_question['question']}\n\n{options_text}\n\nअपना उत्तर भेजें (A/B/C/D):"
    elif language == "mr":
        question_text = f"{feedback}❓ प्रश्न {session.quiz_index}/{len(questions)}\n\n{current_question['question']}\n\n{options_text}\n\nतुमचे उत्तर पाठवा (A/B/C/D):"
    else:
        question_text = f"{feedback}❓ Question {session.quiz_index}/{len(questions)}\n\n{current_question['question']}\n\n{options_text}\n\nSend your answer (A/B/C/D):"
    
    return {
        "reply": question_text,
        "mode": "quiz",
        "quiz_data": {
            "question_num": session.quiz_index,
            "total": len(questions),
            "question": current_question["question"],
            "options": current_question["options"],
            "score": session.quiz_score
        }
    }


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    """Main chat endpoint"""
    try:
        # Get or create session
        if request.session_id:
            session = db.query(ChatSession).filter(ChatSession.id == request.session_id).first()
            if not session:
                session = ChatSession(id=request.session_id, language=request.language)
                db.add(session)
                db.commit()
        else:
            session = ChatSession(id=str(uuid.uuid4()), language=request.language)
            db.add(session)
            db.commit()
        
        # Update language if changed
        if session.language != request.language:
            session.language = request.language
            db.commit()
        
        # Save user message
        user_msg = ChatMessage(session_id=session.id, sender="user", message=request.message)
        db.add(user_msg)
        db.commit()
        
        # Handle quiz mode
        if session.active_mode == "quiz":
            result = handle_quiz_mode(session, request.message, request.language, db, request.username)
            
            # Save bot response
            bot_msg = ChatMessage(session_id=session.id, sender="bot", message=result["reply"])
            db.add(bot_msg)
            db.commit()
            
            return ChatResponse(
                reply=result["reply"],
                session_id=session.id,
                mode=result["mode"],
                quiz_data=result.get("quiz_data")
            )
        
        # Detect intent
        intent = detect_intent(request.message)
        
        # Handle quiz trigger
        if intent["primary"] == "quiz":
            session.active_mode = "quiz"
            session.quiz_index = 0
            session.quiz_score = 0
            db.commit()
            
            result = handle_quiz_mode(session, "", request.language, db, request.username)
            
            # Save bot response
            bot_msg = ChatMessage(session_id=session.id, sender="bot", message=result["reply"])
            db.add(bot_msg)
            db.commit()
            
            return ChatResponse(
                reply=result["reply"],
                session_id=session.id,
                mode="quiz",
                quiz_data=result.get("quiz_data")
            )
        
        # Handle NGO queries
        if intent["primary"] == "ngo":
            reply = handle_ngo_query(request.message, request.language, db)
        # Handle scheme queries
        elif intent["primary"] == "scheme":
            reply = handle_scheme_query(request.message, request.language, db)
        # General sustainability query - use RAG with persistent memory
        else:
            rag_result = get_rag_response(
                request.message, 
                request.language, 
                session_id=session.id,
                username=request.username
            )
            reply = rag_result["answer"]
        
        # Save bot response
        bot_msg = ChatMessage(session_id=session.id, sender="bot", message=reply)
        db.add(bot_msg)
        db.commit()
        
        # Award points for chat question (gamification)
        if request.username:
            try:
                award_points(
                    db=db,
                    username=request.username,
                    activity_type="chat_question",
                    metadata={"question": request.message[:100]}
                )
            except Exception as e:
                print(f"Gamification error: {str(e)}")
        
        return ChatResponse(
            reply=reply,
            session_id=session.id,
            mode="normal"
        )
        
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/history")
async def get_chat_history(
    session_id: Optional[str] = None,
    username: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get chat history for a session or username"""
    try:
        if session_id:
            # Get specific session history
            messages = db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).order_by(ChatMessage.created_at.desc()).limit(limit).all()
            
            return {
                "session_id": session_id,
                "messages": [
                    {
                        "sender": msg.sender,
                        "message": msg.message,
                        "timestamp": msg.created_at.isoformat()
                    }
                    for msg in reversed(messages)
                ]
            }
        elif username:
            # Get all sessions for username (if we stored username in session)
            # For now, return recent sessions
            sessions = db.query(ChatSession).order_by(
                ChatSession.created_at.desc()
            ).limit(10).all()
            
            history = []
            for session in sessions:
                messages = db.query(ChatMessage).filter(
                    ChatMessage.session_id == session.id
                ).order_by(ChatMessage.created_at).all()
                
                if messages:
                    history.append({
                        "session_id": session.id,
                        "date": session.created_at.isoformat(),
                        "language": session.language,
                        "message_count": len(messages),
                        "messages": [
                            {
                                "sender": msg.sender,
                                "message": msg.message,
                                "timestamp": msg.created_at.isoformat()
                            }
                            for msg in messages
                        ]
                    })
            
            return {"sessions": history}
        else:
            # Return recent sessions
            sessions = db.query(ChatSession).order_by(
                ChatSession.created_at.desc()
            ).limit(10).all()
            
            return {
                "sessions": [
                    {
                        "session_id": s.id,
                        "date": s.created_at.isoformat(),
                        "language": s.language
                    }
                    for s in sessions
                ]
            }
    except Exception as e:
        print(f"Error fetching chat history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

