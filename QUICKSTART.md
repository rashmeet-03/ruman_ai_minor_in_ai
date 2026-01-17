# 🎯 Quick Start - Run Everything in 5 Minutes

## Prerequisites Check
```bash
python --version   # Should be 3.8+
node --version     # Should be 16+
npm --version      # Should be 8+
```

---

## Backend Setup (2 minutes)

### Terminal 1 - Backend
```bash
cd d:\minor_in_ai\ruman\backend

# Install dependencies
pip install -r requirements.txt

# Configure Gemini API (REQUIRED!)
copy .env.example .env
# Edit .env and add: GEMINI_API_KEY=your_key_here

# Initialize database with sample data
python init_db.py
# Type: 1 (for fresh database

# Start backend
python app.py
```

**✅ Backend running on http://localhost:8000**

---

## Frontend Setup (2 minutes)

### Terminal 2 - Frontend
```bash
cd d:\minor_in_ai\ruman\frontend

# Install dependencies (first time only)
npm install

# Start frontend
npm run dev
```

**✅ Frontend running on http://localhost:3000**

---

## Access & Test (1 minute)

### Open Browser
Go to: **http://localhost:3000**

### Login with Demo Accounts
**Student**:
- Username: `student1`
- Password: `student123`

**Teacher**:
- Username: `teacher1`  
- Password: `teacher123`

**Admin**:
- Username: `admin`
- Password: `admin123`

---

## Test Backend API Directly

Open: **http://localhost:8000/docs**

This opens Swagger UI where you can:
1. Click "Authorize" button
2. Login to get token
3. Test all API endpoints interactively

---

## Run Automated Tests

### Terminal 3 - Tests
```bash
cd d:\minor_in_ai\ruman\backend

# Test authentication
python test_auth.py

# Test AI services (requires Gemini API key)
python test_ai_services.py
```

---

## That's It! 🎉

**You now have**:
- ✅ Backend API running with sample data
- ✅ Frontend UI with dark/light themes
- ✅ Demo accounts ready to use
- ✅ All features functional

**For detailed testing**: See `TESTING_GUIDE.md`

---

## Common Issues

**Backend won't start?**
```bash
pip install google-generativeai langchain chromadb scikit-learn
```

**Frontend blank page?**
- Make sure backend is running first
- Check browser console (F12) for errors

**AI features not working?**
- Add Gemini API key to `.env` file
- Get key from: https://makersuite.google.com/app/apikey
