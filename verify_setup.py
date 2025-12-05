"""
EcoMitra - Installation Verification Script
Run this after installation to verify everything is set up correctly
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8+"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print("✅ Python version:", f"{version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print("❌ Python 3.8+ required. Current:", f"{version.major}.{version.minor}.{version.micro}")
        return False

def check_env_file():
    """Check if .env file exists"""
    if Path(".env").exists():
        print("✅ .env file exists")
        
        # Check if API key is set
        with open(".env", "r") as f:
            content = f.read()
            if "GOOGLE_API_KEY=AIza" in content or "GOOGLE_API_KEY=your" in content:
                if "your_gemini_api_key_here" in content:
                    print("⚠️  Warning: GOOGLE_API_KEY not set in .env file")
                    return False
                else:
                    print("✅ GOOGLE_API_KEY appears to be set")
                    return True
            else:
                print("⚠️  Warning: GOOGLE_API_KEY not found in .env file")
                return False
    else:
        print("❌ .env file not found. Copy from .env.example")
        return False

def check_dependencies():
    """Check if key dependencies are installed"""
    dependencies = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "langchain",
        "langchain_google_genai",
        "chromadb",
        "google.generativeai"
    ]
    
    all_installed = True
    for dep in dependencies:
        try:
            __import__(dep.replace("-", "_"))
            print(f"✅ {dep} installed")
        except ImportError:
            print(f"❌ {dep} not installed")
            all_installed = False
    
    return all_installed

def check_directories():
    """Check if all required directories exist"""
    required_dirs = [
        "backend",
        "backend/ai",
        "backend/routers",
        "templates",
        "static",
        "static/css",
        "static/js",
        "data"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path}/ exists")
        else:
            print(f"❌ {dir_path}/ not found")
            all_exist = False
    
    return all_exist

def check_knowledge_base():
    """Check if knowledge base files exist"""
    kb_files = [
        "data/recycling_basics.md",
        "data/energy_tips.md",
        "data/pollution_control.md"
    ]
    
    all_exist = True
    for file_path in kb_files:
        if Path(file_path).exists():
            size = Path(file_path).stat().st_size
            print(f"✅ {file_path} ({size} bytes)")
        else:
            print(f"❌ {file_path} not found")
            all_exist = False
    
    return all_exist

def check_database():
    """Check if database needs to be initialized"""
    if Path("ecomitra.db").exists():
        print("✅ Database file exists")
        return True
    else:
        print("⚠️  Database not initialized. Run: python backend/init_db.py")
        return False

def main():
    """Run all checks"""
    print("=" * 60)
    print("EcoMitra - Installation Verification")
    print("=" * 60)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Environment File", check_env_file),
        ("Dependencies", check_dependencies),
        ("Directory Structure", check_directories),
        ("Knowledge Base Files", check_knowledge_base),
        ("Database", check_database)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n--- Checking {name} ---")
        results.append(check_func())
        print()
    
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    if all(results):
        print("✅ All checks passed! You're ready to run EcoMitra.")
        print("\nNext steps:")
        print("1. Make sure GOOGLE_API_KEY is set in .env file")
        print("2. Initialize database: python backend/init_db.py")
        print("3. Run server: uvicorn backend.main:app --reload")
        print("4. Open browser: http://localhost:8000/")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\nQuick fixes:")
        if not results[1]:  # env file
            print("- Copy .env.example to .env and add your Gemini API key")
        if not results[2]:  # dependencies
            print("- Run: pip install -r requirements.txt")
        if not results[5]:  # database
            print("- Run: python backend/init_db.py")
    
    print()

if __name__ == "__main__":
    main()
