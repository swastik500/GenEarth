# EcoMitra – AI Chatbot for Community Awareness on Sustainable Practices

🌱 An intelligent chatbot built with FastAPI, LangChain, and Gemini AI to educate citizens about sustainability, recycling, energy saving, and government environmental schemes.

## 🚀 Features

- **🤖 AI-Powered Chat**: RAG-based responses using Gemini AI and ChromaDB
- **🌍 Multilingual Support**: English, Hindi, and Marathi
- **♻️ Sustainability Topics**: Recycling, energy-saving, pollution control
- **🏛️ Government Schemes**: Information about subsidies and environmental programs
- **🤝 NGO Directory**: Searchable database with filters
- **🎮 Quiz Mode**: Gamified learning with MCQs
- **💬 WhatsApp-like UI**: Clean, modern chat interface

## 📋 Prerequisites

- Python 3.8+
- Google Gemini API Key ([Get it here](https://makersuite.google.com/app/apikey))

## 🛠️ Installation & Setup

### 1️⃣ Clone or Navigate to Project

```bash
cd "c:\Users\Swastik\PycharmProjects\ReGen"
```

### 2️⃣ Create Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3️⃣ Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4️⃣ Set Up Environment Variables

```powershell
# Copy example env file
copy .env.example .env

# Edit .env and add your Gemini API key
# GOOGLE_API_KEY=your_actual_api_key_here
```

### 5️⃣ Initialize Database & Knowledge Base

```powershell
python backend/init_db.py
```

This will:

- Create SQLite database with sample NGOs and government schemes
- Load knowledge base into ChromaDB
- Set up vector embeddings

### 6️⃣ Run the Application

```powershell
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 7️⃣ Open Browser

Navigate to: **http://localhost:8000/**

## 📁 Project Structure

```
ecomitra/
 ┣ backend/
 ┃ ┣ main.py              # FastAPI app entry point
 ┃ ┣ models.py            # SQLAlchemy database models
 ┃ ┣ database.py          # Database configuration
 ┃ ┣ init_db.py           # Database initialization script
 ┃ ┣ quiz_data.py         # Quiz questions data
 ┃ ┣ routers/
 ┃ ┃ ┣ chat.py            # Chat API endpoints
 ┃ ┃ ┣ ngos.py            # NGO listing endpoints
 ┃ ┣ ai/
 ┃ ┃ ┣ chain.py           # LangChain RAG logic
 ┃ ┃ ┣ gemini_setup.py    # Gemini AI configuration
 ┃ ┃ ┣ knowledge_loader.py # Vector DB ingestion
 ┣ templates/
 ┃ ┣ base.html            # Base template
 ┃ ┣ index.html           # Landing page
 ┃ ┣ chat.html            # Chat interface
 ┃ ┣ ngos.html            # NGO directory
 ┣ static/
 ┃ ┣ css/
 ┃ ┃ ┣ style.css          # Main stylesheet
 ┃ ┣ js/
 ┃ ┃ ┣ chat.js            # Chat functionality
 ┣ data/
 ┃ ┣ recycling_basics.md  # Recycling guide
 ┃ ┣ energy_tips.md       # Energy saving tips
 ┃ ┣ pollution_control.md # Pollution control guide
 ┣ requirements.txt
 ┣ .env.example
 ┣ README.md
```

## 🎯 API Endpoints

### Frontend Routes

- `GET /` - Landing page
- `GET /chat` - Chat interface
- `GET /ngos` - NGO directory

### API Routes

- `POST /api/chat` - Send message to chatbot
- `GET /api/ngos` - Get filtered NGO list
- `GET /api/health` - Health check

## 💬 Chat Features

### Topic Chips

- ♻️ Recycling
- ⚡ Energy Saving
- 🌫️ Pollution Control
- 🏛️ Government Schemes
- 🤝 NGOs Near Me
- ❓ Quiz Mode

### Quiz Mode

Type "quiz" or click the Quiz button to start a 5-question environmental quiz with instant scoring.

## 🌐 Multilingual Support

The chatbot responds in your selected language:

- **English** (en)
- **हिंदी** (hi)
- **मराठी** (mr)

## 🏛️ Government Schemes Database

Includes information about:

- PM KUSUM (Solar Pump Scheme)
- FAME India (EV Incentives)
- National Clean Air Programme
- And more...

## 🤝 NGO Directory

Search and filter environmental NGOs by:

- State
- City
- Category (Waste Management, Energy, Water Conservation, etc.)

## 🔧 Troubleshooting

### ChromaDB Issues

If you encounter ChromaDB errors, delete the `chroma_db/` folder and reinitialize:

```powershell
Remove-Item -Recurse -Force chroma_db
python backend/init_db.py
```

### API Key Errors

Ensure your `.env` file has a valid `GOOGLE_API_KEY`:

```
GOOGLE_API_KEY=AIzaSy...
```

## 📝 License

MIT License - Built for Hackathon Purpose

## 👥 Contributing

This is a hackathon project. Feel free to fork and enhance!

---

**Made with 💚 for a sustainable future**
