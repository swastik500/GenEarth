from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import chat, ngos
from backend.database import init_db

# Initialize FastAPI app
app = FastAPI(
    title="EcoMitra API",
    description="AI Chatbot for Community Awareness on Sustainable Practices",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(chat.router)
app.include_router(ngos.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print("✅ Database initialized")


@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    """Render landing page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    """Render chat page"""
    return templates.TemplateResponse("chat.html", {"request": request})


@app.get("/ngos", response_class=HTMLResponse)
async def ngos_page(request: Request):
    """Render NGO directory page"""
    return templates.TemplateResponse("ngos.html", {"request": request})


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "EcoMitra"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
