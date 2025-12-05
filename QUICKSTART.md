# EcoMitra - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Get Your Gemini API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key (starts with `AIza...`)

### Step 2: Set Up Environment

Open PowerShell in the project directory and run:

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

```powershell
# Copy the example env file
copy .env.example .env

# Edit .env file and add your API key
notepad .env
```

In the `.env` file, replace `your_gemini_api_key_here` with your actual API key:

```
GOOGLE_API_KEY=AIzaSy...your_actual_key
```

### Step 4: Initialize Database

```powershell
python backend/init_db.py
```

This will:

- ✅ Create SQLite database
- ✅ Add sample NGOs and government schemes
- ✅ Initialize ChromaDB with knowledge base
- ✅ Set up vector embeddings

### Step 5: Run the Application

```powershell
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 6: Open Your Browser

Navigate to: **http://localhost:8000/**

🎉 **You're all set!**

---

## 📁 Project Structure Overview

```
ReGen/
├── backend/
│   ├── ai/                      # AI/RAG components
│   │   ├── chain.py             # LangChain RAG logic
│   │   ├── gemini_setup.py      # Gemini AI configuration
│   │   └── knowledge_loader.py  # ChromaDB vector store
│   ├── routers/
│   │   ├── chat.py              # Chat API endpoints
│   │   └── ngos.py              # NGO listing endpoints
│   ├── main.py                  # FastAPI application
│   ├── models.py                # Database models
│   ├── database.py              # Database configuration
│   ├── quiz_data.py             # Quiz questions
│   └── init_db.py               # Database initialization
├── templates/                   # HTML templates
│   ├── base.html
│   ├── index.html               # Landing page
│   ├── chat.html                # Chat interface
│   └── ngos.html                # NGO directory
├── static/
│   ├── css/
│   │   └── style.css            # Styling
│   └── js/
│       └── chat.js              # Chat functionality
├── data/                        # Knowledge base
│   ├── recycling_basics.md
│   ├── energy_tips.md
│   └── pollution_control.md
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🎯 Features Overview

### 1. Landing Page (`/`)

- Language selection (English/Hindi/Marathi)
- Topic preview
- Sample questions
- Feature highlights

### 2. Chat Interface (`/chat`)

- WhatsApp-like UI
- AI-powered responses using Gemini & RAG
- Quick topic chips
- Multilingual support
- Real-time typing indicators

### 3. NGO Directory (`/ngos`)

- Searchable database
- Filters by state, city, category
- Contact information
- Direct links to websites

### 4. Quiz Mode

- Trigger by typing "quiz" or clicking Quiz chip
- 5 questions per session
- Instant feedback
- Score tracking
- Available in all languages

---

## 💬 Chat Topics

Ask about:

- ♻️ **Recycling**: "How do I segregate waste?"
- ⚡ **Energy Saving**: "Tips to reduce electricity bill"
- 🌫️ **Pollution**: "How to check air quality?"
- 🏛️ **Government Schemes**: "Solar subsidy schemes"
- 🤝 **NGOs**: "Environmental NGOs in Mumbai"
- ❓ **Quiz**: Type "quiz" to start

---

## 🔧 Troubleshooting

### Issue: "GOOGLE_API_KEY not found"

**Solution**: Make sure you've created the `.env` file and added your API key.

```powershell
# Check if .env exists
Get-Content .env

# If not, copy from example
copy .env.example .env
```

### Issue: ChromaDB errors

**Solution**: Delete and reinitialize the vector database.

```powershell
Remove-Item -Recurse -Force chroma_db
python backend/init_db.py
```

### Issue: "Module not found"

**Solution**: Make sure virtual environment is activated and dependencies are installed.

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Issue: Port 8000 already in use

**Solution**: Use a different port.

```powershell
uvicorn backend.main:app --reload --port 8080
```

Then open: http://localhost:8080/

### Issue: Database locked error

**Solution**: Close any other processes using the database and restart.

```powershell
# Stop the server (Ctrl+C)
# Delete database file
Remove-Item ecomitra.db
# Reinitialize
python backend/init_db.py
```

---

## 🧪 Testing the Application

### Test Chat Functionality

1. Go to http://localhost:8000/chat
2. Try these questions:

```
"Tell me about recycling plastic bottles"
"How can I save electricity at home?"
"Show me solar schemes in Maharashtra"
"Find NGOs in Pune"
"Start quiz"
```

### Test Language Switching

1. Select Hindi or Marathi from the dropdown
2. Ask questions in that language
3. Bot should respond in the selected language

### Test NGO Directory

1. Go to http://localhost:8000/ngos
2. Apply filters (State, City, Category)
3. Click "Apply Filters"
4. Verify results match filters

---

## 📊 Database Overview

### Tables Created

1. **ngos** - Environmental NGO information

   - 10 sample NGOs across India

2. **government_schemes** - Government environmental schemes

   - 8 sample schemes (National and State-level)

3. **chat_sessions** - User chat sessions

   - Tracks language, quiz state

4. **chat_messages** - Chat history
   - Stores user and bot messages

### View Database Content

```powershell
# Install SQLite browser (optional)
# Or use Python

python
>>> from backend.database import SessionLocal
>>> from backend.models import NGO
>>> db = SessionLocal()
>>> ngos = db.query(NGO).all()
>>> for ngo in ngos:
...     print(ngo.name, ngo.city)
>>> exit()
```

---

## 🎨 Customization Tips

### Change Color Theme

Edit `static/css/style.css`:

```css
:root {
  --primary-color: #10b981; /* Change to your color */
  --primary-dark: #059669;
  /* ... */
}
```

### Add More Quiz Questions

Edit `backend/quiz_data.py` and add questions to the `QUIZ_QUESTIONS` dictionary.

### Add More NGOs

Run:

```python
python
>>> from backend.database import SessionLocal
>>> from backend.models import NGO
>>> db = SessionLocal()
>>> ngo = NGO(
...     name="Your NGO Name",
...     state="State",
...     city="City",
...     category="Category",
...     # ... more fields
... )
>>> db.add(ngo)
>>> db.commit()
>>> exit()
```

### Add More Knowledge Base Content

Create new `.md` files in the `data/` directory, then run:

```powershell
python backend/init_db.py
```

Select "yes" when asked to reset and reseed.

---

## 📱 Making it Production-Ready

### 1. Security

```powershell
# Create a secure secret key
python -c "import secrets; print(secrets.token_hex(32))"
```

Add to `.env`:

```
SECRET_KEY=your_generated_secret_key
```

### 2. Database

For production, use PostgreSQL instead of SQLite:

```
DATABASE_URL=postgresql://user:password@localhost/ecomitra
```

### 3. Deployment

**Option A: Railway/Render/Fly.io**

- Add `Procfile`:
  ```
  web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
  ```

**Option B: Docker**

- Create `Dockerfile`:
  ```dockerfile
  FROM python:3.11
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install -r requirements.txt
  COPY . .
  CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
  ```

### 4. Environment Variables

On deployment platform, set:

- `GOOGLE_API_KEY`
- `DATABASE_URL` (if using PostgreSQL)
- `CHROMA_PERSIST_DIR`

---

## 🤝 Support

### API Documentation

Once running, visit:

- **Interactive API docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

### Health Check

Test if server is running:

```powershell
curl http://localhost:8000/api/health
```

Should return:

```json
{ "status": "healthy", "service": "EcoMitra" }
```

---

## 🎓 Learning Resources

### Understanding the Tech Stack

- **FastAPI**: https://fastapi.tiangolo.com/
- **LangChain**: https://python.langchain.com/
- **Gemini AI**: https://ai.google.dev/
- **ChromaDB**: https://www.trychroma.com/

### Extending the Project

Ideas for enhancement:

1. Add user authentication
2. Save chat history permanently
3. Add more languages (Tamil, Telugu, Bengali)
4. Implement voice input/output
5. Add image upload for waste identification
6. Create mobile app version
7. Add real-time AQI data integration
8. Implement chatbot analytics dashboard

---

## 📝 License

MIT License - Free to use for hackathons and educational purposes

---

**Happy Coding! 🚀**

For issues or questions, check the main README.md file.
