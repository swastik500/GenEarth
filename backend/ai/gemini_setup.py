import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
USE_GEMINI_EMBEDDINGS = os.getenv("USE_GEMINI_EMBEDDINGS", "false").lower() in ("1", "true", "yes")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")


def get_gemini_llm(temperature=0.7):
    """Initialize Gemini LLM for chat"""
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        google_api_key=GOOGLE_API_KEY,
        temperature=temperature,
        convert_system_message_to_human=True
    )


def get_embeddings():
    """Return an embeddings implementation with safe fallback.

    Defaults to local HuggingFace embeddings to avoid Gemini quota issues.
    Set env `USE_GEMINI_EMBEDDINGS=true` to force Gemini embeddings.
    """
    if USE_GEMINI_EMBEDDINGS:
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        return GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=GOOGLE_API_KEY
        )

    # Local, free embeddings (no API calls)
    # Model: sentence-transformers/all-MiniLM-L6-v2
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
