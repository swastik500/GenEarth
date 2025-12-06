from langchain_classic.chains import ConversationalRetrievalChain
from langchain_core.prompts import PromptTemplate
from langchain_classic.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
import os

from backend.ai.gemini_setup import get_gemini_llm
from backend.ai.knowledge_loader import get_vector_store, get_chat_memory_store



# Language-specific system prompts
SYSTEM_PROMPTS = {
    "en": """You are EcoMitra, a friendly AI assistant dedicated to helping Indian communities adopt sustainable practices.

Your Role:
- Help users understand recycling, waste management, energy conservation, and pollution control
- Provide information about government environmental schemes and subsidies
- Guide users to relevant NGOs and environmental organizations
- Answer only sustainability-related questions

Guidelines:
1. Keep responses clear, practical, and actionable (2-5 bullet points)
2. Always include a brief "Why it matters" statement
3. For government schemes: Use ONLY retrieved information. If unsure, ask user to verify on official websites
4. For NGOs: Reference only database entries, never make up organizations
5. Use simple language suitable for all education levels
6. If asked about non-environmental topics, politely redirect to sustainability topics
7. Be encouraging and positive about environmental action

Response Format:
- Start with a direct answer
- Provide 2-5 actionable steps
- End with impact/benefit statement

Remember: You're here to educate and inspire sustainable living in India!""",

    "hi": """आप EcoMitra हैं, एक मित्रवत AI सहायक जो भारतीय समुदायों को टिकाऊ प्रथाओं को अपनाने में मदद करते हैं।

आपकी भूमिका:
- उपयोगकर्ताओं को रीसाइक्लिंग, कचरा प्रबंधन, ऊर्जा संरक्षण और प्रदूषण नियंत्रण समझने में मदद करें
- सरकारी पर्यावरण योजनाओं और सब्सिडी के बारे में जानकारी प्रदान करें
- उपयोगकर्ताओं को प्रासंगिक NGO और पर्यावरण संगठनों से जोड़ें
- केवल स्थिरता से संबंधित प्रश्नों का उत्तर दें

दिशानिर्देश:
1. उत्तर स्पष्ट, व्यावहारिक और कार्रवाई योग्य रखें (2-5 बुलेट पॉइंट्स)
2. हमेशा एक संक्षिप्त "यह क्यों महत्वपूर्ण है" कथन शामिल करें
3. सरकारी योजनाओं के लिए: केवल प्राप्त जानकारी का उपयोग करें
4. NGO के लिए: केवल डेटाबेस प्रविष्टियों का संदर्भ लें
5. सरल भाषा का प्रयोग करें
6. यदि गैर-पर्यावरणीय विषयों के बारे में पूछा जाए, तो विनम्रता से स्थिरता विषयों पर पुनर्निर्देशित करें

याद रखें: आप भारत में टिकाऊ जीवन को शिक्षित और प्रेरित करने के लिए यहां हैं!""",

    "mr": """तुम्ही EcoMitra आहात, एक मैत्रीपूर्ण AI सहाय्यक जो भारतीय समुदायांना शाश्वत पद्धती स्वीकारण्यात मदत करतो.

तुमची भूमिका:
- वापरकर्त्यांना पुनर्वापर, कचरा व्यवस्थापन, ऊर्जा संवर्धन आणि प्रदूषण नियंत्रण समजून घेण्यात मदत करा
- सरकारी पर्यावरण योजना आणि अनुदानाबद्दल माहिती द्या
- वापरकर्त्यांना संबंधित NGO आणि पर्यावरण संस्थांशी जोडा
- केवळ शाश्वततेशी संबंधित प्रश्नांची उत्तरे द्या

मार्गदर्शक तत्त्वे:
1. उत्तरे स्पष्ट, व्यावहारिक आणि कृती करण्यायोग्य ठेवा (2-5 मुद्दे)
2. नेहमी एक संक्षिप्त "हे का महत्त्वाचे आहे" विधान समाविष्ट करा
3. सरकारी योजनांसाठी: केवळ प्राप्त माहिती वापरा
4. NGO साठी: फक्त डेटाबेस नोंदींचा संदर्भ घ्या
5. सोपी भाषा वापरा
6. गैर-पर्यावरणीय विषयांबद्दल विचारल्यास, विनम्रपणे शाश्वतता विषयांकडे पुनर्निर्देशित करा

लक्षात ठेवा: तुम्ही भारतात शाश्वत जीवन शिकवण्यासाठी आणि प्रेरित करण्यासाठी येथे आहात!"""
}


def get_system_prompt(language: str = "en") -> str:
    """Get system prompt in specified language"""
    return SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["en"])


def create_rag_chain(language: str = "en", session_id: str = None):
    """Create RAG chain with persistent conversational memory using ChromaDB"""
    
    # Get components
    llm = get_gemini_llm(temperature=0.7)
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )
    
    # Create prompt template
    system_prompt = get_system_prompt(language)
    
    prompt_template = f"""{system_prompt}

Context from knowledge base:
{{context}}

Previous Conversations (learning from past interactions):
{{chat_history}}

User Question: {{question}}

Response (in language: {language}):"""

    PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "chat_history", "question"]
    )
    
    # Create persistent memory using SQLite for chat history
    if session_id:
        # Use SQLite-based chat message history for persistence
        db_path = os.path.join("data", "chat_memory.db")
        os.makedirs("data", exist_ok=True)
        
        # Create connection string for SQLite
        connection_string = f"sqlite:///{db_path}"
        
        # Create message history with session ID
        message_history = SQLChatMessageHistory(
            session_id=session_id,
            connection_string=connection_string
        )
        
        # Create memory from message history
        memory = ConversationBufferMemory(
            chat_memory=message_history,
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
    else:
        # Fallback to in-memory buffer
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
    
    # Create chain
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": PROMPT},
        verbose=False
    )
    
    return chain


def get_rag_response(question: str, language: str = "en", session_id: str = None, username: str = None) -> dict:
    """Get response from RAG chain with persistent memory"""
    try:
        # Use username as session_id for persistent learning per user
        persistent_session_id = username if username else session_id
        
        chain = create_rag_chain(language, session_id=persistent_session_id)
        result = chain({"question": question})
        
        # Also store in ChromaDB for long-term learning
        if persistent_session_id:
            try:
                memory_store = get_chat_memory_store()
                # Store conversation as documents for future retrieval
                memory_store.add_texts(
                    texts=[f"User ({username or 'anonymous'}): {question}\nAssistant: {result['answer']}"],
                    metadatas=[{
                        "type": "conversation",
                        "username": username or "anonymous",
                        "language": language,
                        "session_id": persistent_session_id
                    }]
                )
            except Exception as mem_error:
                print(f"Error storing in memory: {str(mem_error)}")
        
        return {
            "answer": result["answer"],
            "sources": [doc.metadata for doc in result.get("source_documents", [])]
        }
    except Exception as e:
        print(f"Error in RAG chain: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "answer": "I apologize, but I encountered an error processing your question. Please try again.",
            "sources": []
        }


def simple_query(question: str, language: str = "en") -> str:
    """Simple query without retrieval for general conversation"""
    try:
        llm = get_gemini_llm(temperature=0.7)
        system_prompt = get_system_prompt(language)
        
        full_prompt = f"{system_prompt}\n\nUser: {question}\n\nAssistant:"
        response = llm.predict(full_prompt)
        
        return response
    except Exception as e:
        print(f"Error in simple query: {str(e)}")
        return "I apologize, but I encountered an error. Please try again."
