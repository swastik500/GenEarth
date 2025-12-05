# 🚀 EcoMitra - Setup Checklist

Use this checklist to ensure everything is set up correctly for your hackathon demo.

---

## ✅ Pre-Setup Checklist

- [ ] Python 3.8+ installed
  - Check: `python --version`
- [ ] Git installed (optional, for version control)

  - Check: `git --version`

- [ ] Text editor/IDE ready (VS Code, PyCharm, etc.)

- [ ] Google account (for Gemini API key)

---

## 📝 Step 1: Get Gemini API Key

- [ ] Visit: https://makersuite.google.com/app/apikey
- [ ] Sign in with Google account
- [ ] Click "Create API Key"
- [ ] Copy API key (starts with `AIza...`)
- [ ] Keep it safe (you'll need it in Step 4)

**API Key:** `____________________________________`

---

## 📦 Step 2: Install Dependencies

Open PowerShell in project directory:

- [ ] Create virtual environment

  ```powershell
  python -m venv venv
  ```

- [ ] Activate virtual environment

  ```powershell
  .\venv\Scripts\Activate.ps1
  ```

  - You should see `(venv)` in your prompt

- [ ] Install requirements

  ```powershell
  pip install -r requirements.txt
  ```

  - Wait for installation (2-3 minutes)

- [ ] Verify installation
  ```powershell
  python verify_setup.py
  ```

---

## ⚙️ Step 3: Configure Environment

- [ ] Copy environment template

  ```powershell
  copy .env.example .env
  ```

- [ ] Open `.env` file in text editor

  ```powershell
  notepad .env
  ```

- [ ] Replace `your_gemini_api_key_here` with your actual API key

  ```
  GOOGLE_API_KEY=AIzaSy...your_actual_key
  ```

- [ ] Save and close the file

- [ ] Verify API key is set
  ```powershell
  python verify_setup.py
  ```

---

## 🗄️ Step 4: Initialize Database

- [ ] Run initialization script

  ```powershell
  python backend/init_db.py
  ```

- [ ] Wait for completion (1-2 minutes)

- [ ] Verify successful completion
  - [ ] Should see "✅ Database initialized"
  - [ ] Should see "✅ Vector store initialized"
  - [ ] `ecomitra.db` file created
  - [ ] `chroma_db/` directory created

---

## 🚀 Step 5: Start the Server

- [ ] Run the server

  ```powershell
  uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
  ```

- [ ] Wait for server to start

- [ ] Look for these messages:

  - [ ] "✅ Database initialized"
  - [ ] "Application startup complete"
  - [ ] "Uvicorn running on http://0.0.0.0:8000"

- [ ] Server is running (don't close this window)

---

## 🌐 Step 6: Test in Browser

Open a new browser window:

- [ ] Navigate to: http://localhost:8000/

- [ ] Landing page loads correctly
  - [ ] Can see EcoMitra logo
  - [ ] Language selector visible
  - [ ] Topic cards displayed
  - [ ] Start Chat button present

---

## 🧪 Step 7: Test Core Features

### Landing Page

- [ ] Click on each language button (EN/HI/MR)
- [ ] Language button highlights when selected
- [ ] Sample question chips are clickable

### Chat Interface

- [ ] Click "Start Chat" button
- [ ] Chat page loads
- [ ] Welcome message appears
- [ ] Input box is functional

### Test Chat Functionality

- [ ] Type: "Tell me about recycling"
- [ ] Press Enter or click Send
- [ ] Bot responds with recycling information
- [ ] Response contains actionable steps

### Test Language Switching

- [ ] Change language to "हिंदी" in dropdown
- [ ] Type: "ऊर्जा बचाने के टिप्स"
- [ ] Bot responds in Hindi

### Test Quick Topics

- [ ] Click "♻️ Recycling" chip
- [ ] Message auto-sends
- [ ] Bot responds appropriately

### Test NGO Query

- [ ] Type: "Show me NGOs in Mumbai"
- [ ] Bot lists NGOs from database
- [ ] Contact information included

### Test Quiz Mode

- [ ] Type: "quiz"
- [ ] Quiz starts with first question
- [ ] Four options (A/B/C/D) shown
- [ ] Type answer (e.g., "A")
- [ ] Feedback received
- [ ] Next question appears
- [ ] Complete all 5 questions
- [ ] Final score displayed

### NGO Directory

- [ ] Navigate to: http://localhost:8000/ngos
- [ ] NGO cards displayed
- [ ] Select "State" filter (e.g., Maharashtra)
- [ ] Click "Apply Filters"
- [ ] Results update
- [ ] Click "Clear" button
- [ ] All NGOs displayed again

---

## 📊 Step 8: Verify API Endpoints

Open: http://localhost:8000/docs

- [ ] Swagger UI loads
- [ ] API endpoints listed:

  - [ ] POST /api/chat
  - [ ] GET /api/ngos
  - [ ] GET /api/ngos/states
  - [ ] GET /api/ngos/cities
  - [ ] GET /api/ngos/categories
  - [ ] GET /api/health

- [ ] Test health endpoint
  - [ ] Navigate to: http://localhost:8000/api/health
  - [ ] Should show: `{"status":"healthy","service":"EcoMitra"}`

---

## 🎯 Step 9: Prepare Demo

### Demo Script

- [ ] Review PROJECT_SUMMARY.md
- [ ] Note key features to highlight
- [ ] Prepare 2-3 sample questions per topic

### Sample Questions to Use

1. **Recycling**: "How do I segregate waste at home?"
2. **Energy**: "What are the benefits of LED bulbs?"
3. **Pollution**: "How can I reduce air pollution?"
4. **Schemes**: "Tell me about solar subsidy schemes"
5. **NGOs**: "Environmental NGOs in Bangalore"
6. **Quiz**: "quiz" or "start quiz"

### Technical Points to Mention

- [ ] Using Gemini AI (Google's latest model)
- [ ] RAG with ChromaDB for accurate responses
- [ ] Multilingual support (3 languages)
- [ ] Real-time intent detection
- [ ] Gamified learning with quizzes

---

## 🐛 Troubleshooting Checklist

### Server won't start?

- [ ] Virtual environment activated?
- [ ] All dependencies installed?
- [ ] Port 8000 available?
- [ ] Check terminal for error messages

### Chat not responding?

- [ ] Server running?
- [ ] API key set correctly in .env?
- [ ] Check browser console for errors (F12)
- [ ] Try refreshing the page

### Database errors?

- [ ] Delete `ecomitra.db` file
- [ ] Delete `chroma_db/` directory
- [ ] Run `python backend/init_db.py` again

### Vector store errors?

- [ ] Check that `data/` directory has .md files
- [ ] Delete `chroma_db/` directory
- [ ] Run init_db.py again

---

## 📱 Step 10: Test Responsive Design

- [ ] Resize browser window to mobile size
- [ ] Layout adapts correctly
- [ ] Chat interface remains usable
- [ ] NGO cards stack vertically
- [ ] Navigation still accessible

---

## 🎬 Final Pre-Demo Checklist

### 30 Minutes Before

- [ ] Server is running
- [ ] Database is populated
- [ ] Browser tabs ready:
  - [ ] Landing page (http://localhost:8000/)
  - [ ] Chat page (http://localhost:8000/chat)
  - [ ] NGO directory (http://localhost:8000/ngos)
  - [ ] API docs (http://localhost:8000/docs)

### 10 Minutes Before

- [ ] Test each sample question
- [ ] Verify responses are good
- [ ] Clear chat history (refresh page)
- [ ] Set language to English

### 5 Minutes Before

- [ ] Close unnecessary applications
- [ ] Turn off notifications
- [ ] Increase browser zoom if needed
- [ ] Have backup questions ready

---

## 🎉 Demo Flow Suggestion

1. **Introduction** (1 min)

   - Project name and purpose
   - Target audience (Indian communities)
   - Key features overview

2. **Landing Page** (30 sec)

   - Show language selector
   - Highlight topic coverage
   - Click "Start Chat"

3. **Chat Demo** (2 min)

   - Ask recycling question
   - Show AI response quality
   - Switch language to Hindi
   - Ask Hindi question
   - Get Hindi response

4. **Advanced Features** (1 min)

   - Query for NGOs
   - Show scheme information
   - Start quiz mode

5. **NGO Directory** (30 sec)

   - Navigate to NGO page
   - Use filters
   - Show contact information

6. **Technical Highlights** (1 min)

   - Mention Gemini AI
   - Explain RAG architecture
   - Show API documentation
   - Highlight code structure

7. **Q&A** (as needed)

**Total Time: ~6 minutes** (adjust as needed)

---

## 📋 Post-Demo Notes

After your demo, document:

- [ ] Questions asked by judges
- [ ] Feedback received
- [ ] Feature requests
- [ ] Technical issues encountered
- [ ] Suggestions for improvement

---

## 🎯 Success Criteria

You're ready when:

- ✅ All setup steps completed
- ✅ All tests passed
- ✅ Demo script prepared
- ✅ Sample questions ready
- ✅ Troubleshooting knowledge ready
- ✅ Backup plan in place

---

## 🆘 Emergency Contacts / Resources

**If something breaks during setup:**

1. Check `QUICKSTART.md` for troubleshooting
2. Review error messages in terminal
3. Check `verify_setup.py` output
4. Review `README.md` for common issues
5. Check Gemini API key is valid

**Quick Commands Reference:**

```powershell
# Activate environment
.\venv\Scripts\Activate.ps1

# Run server
uvicorn backend.main:app --reload

# Reinitialize database
python backend/init_db.py

# Verify setup
python verify_setup.py
```

---

## ✅ Final Checklist

Right before demo:

- [ ] Server running
- [ ] Browser open to landing page
- [ ] Demo script in hand
- [ ] Confident about features
- [ ] Ready to answer questions

---

**You've got this! 🚀 Good luck with your demo! 🌱**

---

## 📝 Notes Section

Use this space for your own notes:

```
___________________________________________

___________________________________________

___________________________________________

___________________________________________

___________________________________________
```
