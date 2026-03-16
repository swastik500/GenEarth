@echo off
REM ================================================================
REM EcoMitra - Optimized Project Runner
REM ================================================================
REM Recommended Python Version: 3.10.x or 3.11.x
REM Compatible with: TensorFlow 2.15.0, LangChain, FastAPI
REM ================================================================

title EcoMitra - Project Runner (Python 3.10/3.11)

color 0A
echo.
echo ========================================
echo    EcoMitra - Project Runner
echo    Recommended: Python 3.10 or 3.11
echo ========================================
echo.

REM ================================================================
REM Step 1: Check for Recommended Python Version
REM ================================================================
echo [Step 1/6] Checking for recommended Python version...

REM Try Python 3.11 first (best compatibility)
py -3.11 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py -3.11
    echo Found Python 3.11 - OPTIMAL! ^(Best compatibility^)
    goto :python_found
)

REM Try Python 3.10 (also excellent)
py -3.10 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py -3.10
    echo Found Python 3.10 - EXCELLENT! ^(Recommended^)
    goto :python_found
)

REM Try default Python
python --version >nul 2>&1
if not errorlevel 1 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo Found Python %PYTHON_VERSION%
    
    REM Check if it's 3.10 or 3.11
    echo %PYTHON_VERSION% | findstr "3.10" >nul
    if not errorlevel 1 (
        set PYTHON_CMD=python
        echo This version is RECOMMENDED!
        goto :python_found
    )
    
    echo %PYTHON_VERSION% | findstr "3.11" >nul
    if not errorlevel 1 (
        set PYTHON_CMD=python
        echo This version is OPTIMAL!
        goto :python_found
    )
    
    REM Other versions
    echo.
    echo [WARNING] Python %PYTHON_VERSION% detected.
    echo Recommended versions: 3.10.x or 3.11.x
    echo.
    echo Reasons:
    echo   - TensorFlow 2.15.0 works best with Python 3.10-3.11
    echo   - All dependencies are tested on these versions
    echo   - Better stability and performance
    echo.
    echo You can continue, but may encounter compatibility issues.
    echo.
    echo Press any key to continue with Python %PYTHON_VERSION% or Ctrl+C to exit...
    pause >nul
    set PYTHON_CMD=python
    goto :python_found
)

REM No Python found
echo [ERROR] Python is not installed or not in PATH!
echo.
echo Please install Python 3.10 or 3.11 from:
echo https://www.python.org/downloads/
echo.
echo Recommended downloads:
echo   Python 3.11: https://www.python.org/downloads/release/python-3110/
echo   Python 3.10: https://www.python.org/downloads/release/python-31011/
echo.
echo Make sure to check "Add Python to PATH" during installation.
pause
exit /b 1

:python_found
%PYTHON_CMD% --version
echo.

REM ================================================================
REM Step 2: Setup Virtual Environment
REM ================================================================
echo [Step 2/6] Setting up virtual environment...
if exist "venv\Scripts\activate.bat" (
    echo Virtual environment already exists.
) else (
    echo Creating new virtual environment with %PYTHON_CMD%...
    %PYTHON_CMD% -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment!
        echo Try running: %PYTHON_CMD% -m pip install --upgrade pip
        pause
        exit /b 1
    )
    echo Virtual environment created successfully!
)
echo.

REM ================================================================
REM Step 3: Activate Virtual Environment
REM ================================================================
echo [Step 3/6] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment!
    pause
    exit /b 1
)
echo Virtual environment activated.
echo.

REM ================================================================
REM Step 4: Install/Update Dependencies
REM ================================================================
echo [Step 4/6] Installing dependencies...
if exist "requirements.txt" (
    echo This may take 3-5 minutes on first run...
    echo Installing core packages...
    
    REM Upgrade pip first
    python -m pip install --upgrade pip setuptools wheel --quiet
    
    REM Install packages
    echo Installing FastAPI, LangChain, and ML libraries...
    pip install -r requirements.txt
    
    if errorlevel 1 (
        echo.
        echo [WARNING] Some packages failed to install.
        echo.
        echo Common issues:
        echo   - TensorFlow: Requires Visual C++ Redistributable
        echo   - ChromaDB: May need SQLite3
        echo.
        echo The server may still work for basic features.
        echo Press any key to continue...
        pause >nul
    ) else (
        echo.
        echo All dependencies installed successfully!
    )
) else (
    echo [WARNING] requirements.txt not found!
)
echo.

REM ================================================================
REM Step 5: Environment Configuration Check
REM ================================================================
echo [Step 5/6] Checking environment configuration...
if exist ".env" (
    echo .env file found.
    
    findstr /C:"GOOGLE_API_KEY=" .env | findstr /V "your_" >nul 2>&1
    if errorlevel 1 (
        echo.
        echo [WARNING] GOOGLE_API_KEY not configured in .env!
        echo The AI chatbot requires a Gemini API key.
        echo.
        echo Get your free key at: https://makersuite.google.com/app/apikey
        echo Then add it to .env file: GOOGLE_API_KEY=your_key_here
        echo.
    ) else (
        echo Google API Key configured.
    )
) else (
    echo [WARNING] .env file not found!
    if exist ".env.example" (
        copy .env.example .env >nul
        echo Created .env from example.
    )
    echo.
    echo [REQUIRED] Please configure .env file:
    echo   1. GOOGLE_API_KEY=your_gemini_key (Required for AI chat)
    echo   2. ROBOFLOW_API_KEY=your_key (Optional for vision)
    echo.
    echo Get Gemini API: https://makersuite.google.com/app/apikey
    echo.
    choice /C YN /M "Do you want to continue without API keys (limited functionality)"
    if errorlevel 2 exit /b 1
)
echo.

REM ================================================================
REM Step 6: Initialize Database
REM ================================================================
echo [Step 6/6] Initializing database...
python -c "from backend.database import init_db; init_db(); print('Database ready!')" 2>nul
if errorlevel 1 (
    echo Database initialization completed (may already exist).
)
echo.

REM ================================================================
REM All Checks Complete - Start Server
REM ================================================================
cls
color 0A
echo.
echo ========================================
echo    EcoMitra Server Starting
echo ========================================
echo.
echo Python Version: 
%PYTHON_CMD% --version
echo.
echo ========================================
echo   SERVER URLS
echo ========================================
echo.
echo   Main URL:    http://localhost:8000
echo   API Docs:    http://localhost:8000/docs
echo   ReDoc:       http://localhost:8000/redoc
echo.
echo ========================================
echo   WEB PAGES
echo ========================================
echo   🏠 Home:        http://localhost:8000/
echo   💬 AI Chat:     http://localhost:8000/chat
echo   📊 Carbon:      http://localhost:8000/carbon
echo   📸 Vision:      http://localhost:8000/vision
echo   👤 Profile:     http://localhost:8000/profile
echo   🛒 Marketplace: http://localhost:8000/marketplace
echo   🤝 NGOs:        http://localhost:8000/ngos
echo   🏛️  Government:  http://localhost:8000/government
echo.
echo ========================================
echo   MOBILE API
echo ========================================
echo   Base:        http://localhost:8000/api/mobile
echo   Endpoints:   15+ endpoints available
echo   Docs:        See MOBILE_API_GUIDE.md
echo.
echo ========================================
echo   Press Ctrl+C to stop the server
echo ========================================
echo.

REM Start FastAPI server with auto-reload
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

REM Server stopped
echo.
echo.
color 0C
echo ========================================
echo   Server Stopped
echo ========================================
echo.
color 07
pause
