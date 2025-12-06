import os
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import Chroma
from backend.ai.gemini_setup import get_embeddings
from dotenv import load_dotenv

load_dotenv()

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
CHROMA_MEMORY_DIR = os.getenv("CHROMA_MEMORY_DIR", "./chroma_memory")
DATA_DIR = "./data"


def load_knowledge_base():
    """Load markdown files from data directory"""
    print("📚 Loading knowledge base documents...")
    
    # Create data directory if it doesn't exist
    Path(DATA_DIR).mkdir(exist_ok=True)
    
    # Check if data directory has files
    data_path = Path(DATA_DIR)
    md_files = list(data_path.glob("*.md"))
    
    if not md_files:
        print("⚠️ No markdown files found in data directory")
        return []
    
    loader = DirectoryLoader(
        DATA_DIR,
        glob="*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )
    
    documents = loader.load()
    print(f"✅ Loaded {len(documents)} documents")
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100,
        length_function=len,
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"✅ Split into {len(chunks)} chunks")
    
    return chunks


def initialize_vector_store(force_reload=False):
    """Initialize or load ChromaDB vector store"""
    persist_dir = Path(CHROMA_PERSIST_DIR)
    
    # If force reload or directory doesn't exist, create new store
    if force_reload or not persist_dir.exists():
        print("🔄 Creating new vector store...")
        
        # Load and chunk documents
        chunks = load_knowledge_base()
        
        if not chunks:
            print("⚠️ No documents to index. Creating empty vector store.")
            # Create empty store
            embeddings = get_embeddings()
            vector_store = Chroma(
                persist_directory=str(persist_dir),
                embedding_function=embeddings
            )
            return vector_store
        
        # Create vector store
        embeddings = get_embeddings()
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=str(persist_dir)
        )
        
        print(f"✅ Vector store created with {len(chunks)} chunks")
        return vector_store
    else:
        print("📂 Loading existing vector store...")
        embeddings = get_embeddings()
        vector_store = Chroma(
            persist_directory=str(persist_dir),
            embedding_function=embeddings
        )
        print("✅ Vector store loaded")
        return vector_store


def get_vector_store():
    """Get or create vector store instance"""
    return initialize_vector_store(force_reload=False)


def add_scheme_to_vector_store(scheme_data: dict):
    """Add a government scheme to the vector store"""
    from langchain.schema import Document
    
    # Format scheme as a document
    content = f"""
Government Scheme: {scheme_data['name']}
State: {scheme_data['state']}
Category: {scheme_data['category']}

Summary: {scheme_data['summary']}

Eligibility: {scheme_data['eligibility']}

How to Apply: {scheme_data['how_to_apply']}
"""
    
    doc = Document(
        page_content=content,
        metadata={
            "type": "scheme",
            "name": scheme_data['name'],
            "state": scheme_data['state'],
            "category": scheme_data['category']
        }
    )
    
    vector_store = get_vector_store()
    vector_store.add_documents([doc])
    print(f"✅ Added scheme '{scheme_data['name']}' to vector store")


def get_chat_memory_store():
    """Get or create ChromaDB vector store for chat memory/learning"""
    persist_dir = Path(CHROMA_MEMORY_DIR)
    persist_dir.mkdir(exist_ok=True)
    
    embeddings = get_embeddings()
    
    # Load or create memory store
    memory_store = Chroma(
        persist_directory=str(persist_dir),
        embedding_function=embeddings,
        collection_name="chat_memory"
    )
    
    return memory_store
