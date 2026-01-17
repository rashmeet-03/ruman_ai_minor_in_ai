# 🚀 Complete Testing Guide - Ruman AI Platform

## Quick Start Overview

This guide will walk you through testing the entire system from scratch.

**Total Time**: ~30 minutes  
**Prerequisites**: Python 3.8+, Node.js 16+, Git

---

## Step 1: Backend Setup & Testing (15 min)

### 1.1 Install Python Dependencies

```bash
# Navigate to backend
cd backend

# Install all dependencies
pip install -r requirements.txt
```

**Expected Output**: All packages installed successfully

---

### 1.2 Configure Environment Variables

```bash
# Copy the example environment file
copy .env.example .env
```

**Now edit `.env` file and add your Gemini API key:**

```bash
# Open .env in notepad
notepad .env
```

Add this line (get API key from https://makersuite.google.com/app/apikey):
```
GEMINI_API_KEY=your_actual_api_key_here
```

**⚠️ CRITICAL**: Without a valid Gemini API key, AI features won't work!

---

### 1.3 Initialize Database

```bash
# Run database initialization script
python init_db.py
```

**Choose option 1** when prompted (fresh database with sample data)

**Expected Output**:
```
✅ Database created successfully
✅ Sample users created
✅ Sample courses created
✅ Sample data loaded
```

**Default Test Accounts Created**:
- **Admin**: `admin` / `admin123`
- **Teacher**: `teacher1` / `teacher123`  
- **Student**: `student1` / `student123`

---

### 1.4 Start Backend Server

```bash
# Start the FastAPI server
python app.py
```

**Expected Output**:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**✅ Backend is running!** Keep this terminal open.

**Test it**: Open browser to http://localhost:8000/docs - you should see Swagger UI

---

### 1.5 Test Backend API (New Terminal)

Open a **NEW** terminal/command prompt (keep backend running in the first one):

```bash
cd backend
python test_auth.py
```

**Expected Output**:
```
✅ Registration successful
✅ Login successful
✅ Token received
✅ User info retrieved
✅ All authentication tests passed!
```

**Test AI Services**:
```bash
python test_ai_services.py
```

**Expected Output**:
```
✅ RAG System tests PASSED
✅ Quiz Generation tests PASSED
✅ Answer Evaluation tests PASSED
✅ Performance Prediction tests PASSED
✅ Learning Gap Analysis tests PASSED
🎉 ALL TESTS PASSED!
```

---

## Step 2: Frontend Setup & Testing (10 min)

### 2.1 Install Frontend Dependencies

Open a **NEW** terminal (keep backend running):

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install
```

**Expected Output**: Dependencies installed (may take 2-3 minutes)

---

### 2.2 Start Frontend Dev Server

```bash
# Start Vite development server
npm run dev
```

**Expected Output**:
```
  VITE v5.0.8  ready in 500 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

**✅ Frontend is running!**

---

### 2.3 Access the Application

Open your browser to: **http://localhost:3000**

You should see the **Login Page** with:
- Ruman AI Platform title
- Username and password fields
- Demo credentials shown
- Dark/light theme toggle in top right

---

## Step 3: Manual Testing Checklist

### 3.1 Test Authentication

**Login as Student**:
1. Username: `student1`
2. Password: `student123`
3. Click **Login**

**✅ Expected**: Redirect to Student Dashboard

**What to check**:
- [ ] Dashboard shows XP, Level, Streak, Badges
- [ ] Enrolled courses listed
- [ ] Recent quiz attempts shown
- [ ] Theme toggle works (try dark/light)

**Logout**: Click **Logout** button in navbar

---

**Login as Teacher**:
1. Username: `teacher1`
2. Password: `teacher123`
3. Click **Login**

**✅ Expected**: Redirect to Teacher Dashboard

**What to check**:
- [ ] Total students count
- [ ] Number of quizzes/assignments
- [ ] Average quiz score
- [ ] Top performing students table
- [ ] Course selector dropdown

---

### 3.2 Test Student Features

Login as `student1` / `student123`

#### Test 1: View Courses
- [ ] Dashboard shows enrolled courses
- [ ] Each course shows quiz/assignment count

#### Test 2: Take a Quiz
**Using Swagger UI** (easier for testing):
1. Go to http://localhost:8000/docs
2. Click **Authorize** button (🔒)
3. Login to get token:
   - POST `/api/auth/login`
   - Form data: `username=student1`, `password=student123`
   - Copy the `access_token`
4. Click **Authorize**, paste token as: `Bearer YOUR_TOKEN`
5. Try GET `/api/student/dashboard` - should work!

#### Test 3: AI Chatbot (Backend Direct)
**In Swagger UI**:
1. Find POST `/api/student/chatbots/{chatbot_id}/query`
2. chatbot_id: 1
3. question: "What is this course about?"
4. Execute

**✅ Expected**: AI response based on uploaded documents

#### Test 4: Quiz Taking
**In Swagger UI**:
1. GET `/api/student/courses/1/quizzes` - List quizzes
2. POST `/api/student/quizzes/1/attempt` - Start quiz
3. Copy the `attempt_id`
4. POST `/api/student/quiz-attempts/{attempt_id}/submit`
   - Body: `{"answers": {"1": "Answer A", "2": "Answer B"}}`

**✅ Expected**: Auto-grading results with score and XP earned

---

### 3.3 Test Teacher Features

Login as `teacher1` / `teacher123`

#### Test 1: Create Course
**In Swagger UI**:
1. POST `/api/teacher/courses`
2. Body:
```json
{
  "name": "Python Basics",
  "description": "Learn Python programming"
}
```

**✅ Expected**: New course created

#### Test 2: Generate AI Quiz
**In Swagger UI**:
1. POST `/api/teacher/quizzes/generate`
2. Parameters:
   - course_id: 1
   - topic: "Python Functions"
   - num_questions: 3
   - difficulty: "medium"

**✅ Expected**: Quiz auto-generated with 3 questions

#### Test 3: View Analytics
**In Swagger UI**:
1. GET `/api/teacher/courses/1/analytics`

**✅ Expected**: Student performance data, quiz stats, top performers

---

## Step 4: Testing Checklist Summary

### Backend API Tests

- [x] **Authentication**
  - [x] User registration works
  - [x] Login returns JWT token
  - [x] Protected endpoints require token
  - [x] RBAC prevents unauthorized access

- [x] **AI Services**
  - [x] RAG system processes documents
  - [x] Quiz generator creates questions
  - [x] Answer evaluator grades submissions
  - [x] ML models predict performance

- [x] **Database**
  - [x] All tables created correctly
  - [x] Relationships working
  - [x] Sample data loaded

### Frontend Tests

- [ ] **Theme System**
  - [ ] Dark mode works
  - [ ] Light mode works
  - [ ] Theme persists on reload

- [ ] **Authentication Flow**
  - [ ] Login redirects correctly by role
  - [ ] Logout clears session
  - [ ] Protected routes work

- [ ] **Student Dashboard**
  - [ ] Stats display correctly
  - [ ] Courses list shows
  - [ ] Progress tracking visible

- [ ] **Teacher Dashboard**
  - [ ] Analytics display
  - [ ] Course management works
  - [ ] Student performance shown

---

## Step 5: Common Issues & Solutions

### Issue 1: "ModuleNotFoundError: No module named 'google'"
**Solution**:
```bash
pip install google-generativeai
```

### Issue 2: "Gemini API key not configured"
**Solution**: Check `.env` file has `GEMINI_API_KEY=your_actual_key`

### Issue 3: Backend won't start - "Address already in use"
**Solution**:
```bash
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID_number> /F
```

### Issue 4: Frontend shows blank page
**Solution**:
1. Check browser console for errors (F12)
2. Verify backend is running on port 8000
3. Check API proxy in `vite.config.js`

### Issue 5: Database locked error
**Solution**:
```bash
cd backend
del ruman.db
python init_db.py
```

### Issue 6: CORS errors
**Solution**: Backend already configured for CORS, but verify:
- Frontend is on `localhost:3000`
- Backend is on `localhost:8000`

---

## Step 6: Demo-Ready Verification

Before presenting, verify:

### Backend Checklist
- [ ] Server starts without errors
- [ ] Swagger UI loads at `/docs`
- [ ] Test accounts work (admin, teacher, student)
- [ ] Database has sample data
- [ ] AI services respond (test with Gemini API key)

### Frontend Checklist  
- [ ] Login page loads
- [ ] Dark/light theme toggle works
- [ ] Can login as all roles
- [ ] Dashboards render correctly
- [ ] No console errors (F12)

### Demo Flow
1. **Show Login** → Demo credentials visible
2. **Login as Student** → Show gamification (XP, level, badges)
3. **Take Quiz** → Show auto-grading and instant feedback
4. **Show AI Chatbot** → Ask a question, get RAG response
5. **Switch to Teacher** → Show analytics dashboard
6. **Generate AI Quiz** → Show automated question generation
7. **Show Theme Toggle** → Demonstrate dark/light mode

---

## Quick Reference Commands

### Backend
```bash
cd backend
pip install -r requirements.txt
python init_db.py      # Choose option 1
python app.py          # Starts server
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Testing
```bash
# Auth test
python backend/test_auth.py

# AI Services test  
python backend/test_ai_services.py
```

### Ports
- **Backend**: http://localhost:8000
- **Backend Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000

---

## Success Criteria

Your system is **demo-ready** when:

✅ Both servers start without errors  
✅ You can login as student/teacher  
✅ Dashboards display data  
✅ Theme toggle works  
✅ AI services respond (with valid Gemini key)  
✅ Swagger UI shows all endpoints  
✅ No console errors in browser  

**Total Setup Time**: ~30 minutes  
**Demo Duration**: 10-15 minutes recommended

---

## Need Help?

Common test sequence:
1. Install backend deps → Configure .env → Init DB → Start backend
2. Test backend with Swagger UI
3. Install frontend deps → Start frontend
4. Test login flows
5. Demo key features

**Remember**: Keep both terminals running (backend + frontend) during demo!
