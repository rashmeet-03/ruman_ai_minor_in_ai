# 📘 AI Project Report – Module E

## Student & Project Details
| Field | Details |
|-------|---------|
| **Student Name** | RASHMEET SINGH |
| **Mentor Name** | Niranjan Deshpande |
| **Project Title** | **Ruman AI - Personalized Learning Platform** |

---

## 1. Problem Statement

**Background:** Traditional education follows a "one-size-fits-all" approach where students receive the same content regardless of their individual learning pace. Teachers cannot provide personalized attention to 30-50 students, manual grading delays feedback, and students can't get help outside classroom hours.

**AI Task Definition:** Ruman AI is a multi-faceted AI learning platform combining:
- **RAG-Based Q&A** – Course-specific chatbot tutoring using Retrieval-Augmented Generation
- **Automated Assessment** – AI-powered quiz generation and answer evaluation
- **Performance Prediction** – ML-based student risk classification using Random Forest
- **Learning Gap Analysis** – K-Means clustering to identify weak topics

**Objectives:**
1. Create personalized AI tutors for each course using RAG technology
2. Automate quiz/assignment creation and evaluation using hybrid ML + LLM scoring
3. Predict at-risk students and identify learning gaps through ML models
4. Gamify learning with XP points, levels, badges, and streaks

**Constraints:** Relies on teacher-uploaded documents; LLM API rate limits; strict RAG (no hallucination); web-only platform.

---

## 2. Approach

### 2.1 System Architecture

```
┌─────────────────────────────────────────────────────┐
│       FRONTEND (React 18 + Vite)                    │
│   Teacher Dashboard │ Student Dashboard │ Admin     │
└──────────────────────────┬──────────────────────────┘
                           │ REST API
┌──────────────────────────▼──────────────────────────┐
│       BACKEND (FastAPI + SQLAlchemy)                │
│   Auth │ Teacher Routes │ Student Routes │ Admin    │
└──────────────────────────┬──────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────┐
│              AI/ML SERVICES                          │
│  RAG System │ ML Scoring │ Quiz Generator           │
│  Performance Predictor │ Learning Gap Analyzer      │
│  Multi-LLM Provider (Gemini / Mistral)              │
└──────────────────────────┬──────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────┐
│   DATA LAYER: SQLite (14 tables) │ ChromaDB │ Files │
└─────────────────────────────────────────────────────┘
```

### 2.2 AI/ML Model Design

**1. RAG System (Retrieval-Augmented Generation)**
- **Pipeline:** Document Upload → Text Extraction (PyPDF2) → Chunking (512 chars, 50 overlap) → Embedding (all-MiniLM-L6-v2) → Vector Storage (ChromaDB)
- **Query Flow:** Embed question → Retrieve top-5 chunks → Filter by relevance threshold (distance < 1.2) → Generate answer with LLM
- **Key Feature:** Strict RAG - declines off-topic questions to prevent hallucination

**2. Hybrid ML Scoring for Answer Evaluation**
| Component | Algorithm | Weight |
|-----------|-----------|--------|
| TF-IDF Scorer | TF-IDF + Cosine Similarity | 25% |
| Semantic Scorer | Sentence Transformers | 50% |
| Keyword Matcher | Keyword extraction + Set matching | 25% |

Final score = weighted combination; optional LLM feedback for scores <70%

**3. Performance Prediction (Random Forest Classifier)**
- **Features:** quiz_average, assignment_average, quizzes_attempted, assignments_submitted, engagement_score
- **Output:** Risk level (Low/Medium/High) with confidence score

**4. Learning Gap Analysis (K-Means Clustering)**
- Groups students by performance patterns (k=3)
- Identifies weak topics and generates teaching recommendations

### 2.3 Technology Stack

| Layer | Technologies |
|-------|-------------|
| Frontend | React 18, Vite, React Router, Axios, ReactMarkdown, KaTeX |
| Backend | FastAPI, SQLAlchemy, SQLite, JWT Auth, bcrypt |
| AI/ML | Gemini/Mistral APIs, ChromaDB, sentence-transformers, Scikit-learn |
| Processing | PyPDF2, TF-IDF, Random Forest, K-Means |

---

## 3. Key Results

### 3.1 Working Prototype Features

**Teacher Dashboard:** Course Management, AI Chatbot Creator with LLM selection, Document Upload, Quiz Builder (manual + AI-generated), RAG Quiz Generation, Student Analytics, At-risk Student Detection

**Student Dashboard:** Course Enrollment, AI Tutor Chat with markdown/LaTeX support, Quiz Taking with timer, Assignment Submission with AI feedback, Progress Tracking (XP, levels, badges)

### 3.2 Example Outputs

**RAG Chatbot Response:**
```
Q: "What is supervised learning?"
A: Based on course materials, supervised learning is a type of ML 
   where the model learns from labeled data with input features (X) 
   and target labels (y). Examples: Classification, Regression.
```

**ML Scoring Output:**
```json
{"score": 1.8, "max_score": 2.0, "percentage": 90.0,
 "component_scores": {"tfidf": 0.85, "semantic": 0.92, "keyword": 0.88},
 "feedback": "Excellent! Consider including: dimensionality"}
```

### 3.3 Evaluation Metrics

| Component | Metric | Result |
|-----------|--------|--------|
| RAG Relevance | Manual chunk review | >80% relevant |
| Hybrid Scorer | Overall accuracy | ~0.85 |
| Performance Predictor | Cross-validation accuracy | ~78% |
| Response Time | API latency | <3 seconds |

### 3.4 Limitations
- Cold start: ML models need minimum 5 students
- Complex math PDFs may not extract well
- English-optimized models
- LLM rate limits apply

---

## 4. Learnings

**Technical:**
- 512-token chunks with 50-char overlap balance context vs. precision
- Hybrid scoring (TF-IDF + Semantic + Keyword) more robust than single method
- Strict RAG with relevance threshold prevents hallucination
- Provider abstraction enables easy LLM switching (Gemini ↔ Mistral)

**Challenges & Solutions:**
| Challenge | Solution |
|-----------|----------|
| LLM Hallucination | Strict RAG with relevance threshold; decline off-topic questions |
| LLM JSON Parsing | Cleanup markdown blocks; fallback parsing |
| Model Loading Time | Lazy loading + singleton patterns |

**Future Improvements:** Real-time notifications (WebSocket), Mobile app, Video lecture support, Multi-language support

---

## References & AI Usage Disclosure

**Tools & APIs Used:**
- LLM: Google Gemini API, Mistral AI API
- Embeddings: sentence-transformers/all-MiniLM-L6-v2
- Vector DB: ChromaDB | ML: Scikit-learn | Backend: FastAPI
- Frontend: React 18 | Database: SQLite + SQLAlchemy

**AI Tools Used During Development:**
- GitHub Copilot (code completion)
- Claude/ChatGPT (debugging, documentation)
- Gemini (testing RAG prompts)

---

*Report for Module E - AI Project Submission*
