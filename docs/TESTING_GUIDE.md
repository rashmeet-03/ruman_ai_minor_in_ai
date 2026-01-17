# Testing Guide - Ruman AI Platform

## Prerequisites

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This will install:
- **Gemini API**: `google-generativeai`
- **LangChain**: For document processing
- **ChromaDB**: Vector database
- **Sentence Transformers**: For embeddings
- **PyPDF2**: PDF processing
- **Scikit-learn**: ML models
- And all other required packages

### 2. Configure Environment

Create `.env` file in `backend/` directory:

```bash
copy .env.example .env
```

**Required**: Add your Google Gemini API key:
```
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

Get your API key from: https://makersuite.google.com/app/apikey

---

## Test Suite Overview

### Phase 3: Authentication Tests
```bash
python test_auth.py
```

Tests:
- ✅ User registration
- ✅ Login with JWT
- ✅ Token validation
- ✅ Error handling

### Phase 5: AI/ML Services Tests
```bash
python test_ai_services.py
```

Tests:
- ✅ RAG System (document processing, embedding, retrieval, generation)
- ✅ Quiz Generation (AI-powered question creation)
- ✅ Answer Evaluation (MCQ and short answer grading)
- ✅ Performance Prediction (ML risk assessment)
- ✅ Learning Gap Analysis (topic analysis and clustering)

---

## Full Application Testing

### 1. Initialize Database

```bash
python init_db.py
```

Choose option 1 for fresh database with sample data.

**Default Users:**
- Admin: `admin` / `admin123`
- Teacher: `teacher1` / `teacher123`
- Student: `student1` / `student123`

### 2. Start Server

```bash
python app.py
```

Server runs on **http://localhost:8000**

### 3. Interactive API Testing

Visit: **http://localhost:8000/docs**

This opens Swagger UI for testing all endpoints interactively.

#### Testing Workflow:

**A. Authentication:**
1. Test `POST /api/auth/register` - Create a new user
2. Test `POST /api/auth/login` - Login to get token
3. Click "Authorize" button (🔒) - Paste your token
4. Test `GET /api/auth/me` - Verify authentication

**B. Teacher Endpoints:**
1. Login as teacher (`teacher1` / `teacher123`)
2. Create a course: `POST /api/teacher/courses`
3. Create a chatbot: `POST /api/teacher/courses/{id}/chatbots`
4. Upload document: `POST /api/teacher/chatbots/{id}/upload`
5. Process documents: `POST /api/teacher/chatbots/{id}/process-documents`
6. Generate AI quiz: `POST /api/teacher/quizzes/generate`
7. View analytics: `GET /api/teacher/courses/{id}/analytics`

**C. Admin Endpoints:**
1. Login as admin (`admin` / `admin123`)
2. List users: `GET /api/admin/users`
3. Manage users: Activate/Deactivate/Delete

---

## Testing AI Features

### 1. RAG Chatbot

**Setup:**
1. Login as teacher
2. Create a course
3. Create a chatbot for the course
4. Upload a PDF or TXT document
5. Process documents: `POST /api/teacher/chatbots/{id}/process-documents`

**Test:**
- Student can now query the chatbot
- Questions answered based on uploaded documents
- Uses Gemini API for intelligent responses

### 2. AI Quiz Generation

**Test:**
```bash
POST /api/teacher/quizzes/generate
```

Parameters:
```json
{
  "course_id": 1,
  "topic": "Python Programming",
  "num_questions": 5,
  "difficulty": "medium"
}
```

Response:
- Automatically generates quiz with questions
- MCQ, true/false, short answer types
- Includes explanations and points

### 3. Performance Prediction

**Prerequisites:**
- Need at least 5 students with quiz/assignment data

**Test:**
- View course analytics: `GET /api/teacher/courses/{id}/analytics`
- Check student performance breakdown
- Risk levels: low/medium/high

### 4. Answer Evaluation

**Automatic Grading:**
- MCQ: Instant grading
- Short Answer: AI-powered evaluation with Gemini
- Assignments: AI feedback with score breakdown

---

## Manual Testing Checklist

### Phase 1-2: Core Infrastructure
- [x] Database initialization works
- [x] All tables created
- [x] Sample data loaded
- [x] Server starts without errors

### Phase 3: Authentication
- [ ] User registration (all roles)
- [ ] Login returns JWT token
- [ ] Token validation works
- [ ] Protected endpoints require auth
- [ ] Role-based access control (admin/teacher/student)
- [ ] Password hashing (bcrypt)

### Phase 4: Teacher Module
- [ ] Course CRUD operations
- [ ] Student enrollment
- [ ] Chatbot creation
- [ ] Document upload (PDF/TXT)
- [ ] Quiz creation with questions
- [ ] Assignment creation
- [ ] Submission grading
- [ ] Analytics dashboard

### Phase 5: AI/ML Services
- [ ] Document chunking and embedding
- [ ] ChromaDB vector storage
- [ ] RAG query with Gemini
- [ ] AI quiz generation
- [ ] Answer evaluation (MCQ + short answer)
- [ ] Performance prediction (ML model)
- [ ] Learning gap analysis
- [ ] Student clustering

---

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'google'"
**Solution:**
```bash
pip install google-generativeai
```

### Issue: "Gemini API key not configured"
**Solution:**
- Add `GEMINI_API_KEY` to `.env` file
- Get key from: https://makersuite.google.com/app/apikey

### Issue: "ChromaDB error"
**Solution:**
```bash
pip install chromadb
```

### Issue: "PyPDF2 not found"
**Solution:**
```bash
pip install pypdf2
```

### Issue: Database locked
**Solution:**
```bash
# Delete database and recreate
del ruman.db  # Windows
python init_db.py
```

---

## Performance Testing

### Load Testing (Optional)

```bash
pip install locust
```

Create `locustfile.py`:
```python
from locust import HttpUser, task, between

class RumanUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def login(self):
        self.client.post("/api/auth/login", data={
            "username": "teacher1",
            "password": "teacher123"
        })
```

Run:
```bash
locust -f locustfile.py
```

---

## Expected Results

When all tests pass, you should see:

✅ Authentication working with JWT  
✅ Course/Quiz/Assignment CRUD operations  
✅ Document upload and processing  
✅ RAG chatbot responses using Gemini  
✅ AI quiz generation  
✅ Automated answer evaluation  
✅ ML performance predictions  
✅ Learning gap analysis  
✅ Analytics dashboard with statistics  

---

## Next Steps

After testing Phase 1-5:
- Phase 6: Student Module (quiz taking, chatbot interaction, progress tracking)
- Phase 7: Frontend (React UI)
- Phase 8: Jupyter Notebook (demonstration for evaluation)
- Phase 9: Documentation and deployment
