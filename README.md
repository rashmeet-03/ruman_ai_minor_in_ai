<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React">
  <img src="https://img.shields.io/badge/Google%20Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Gemini">
  <img src="https://img.shields.io/badge/Mistral%20AI-5E17EB?style=for-the-badge&logo=openai&logoColor=white" alt="Mistral">
</p>

<h1 align="center">RUMAN AI Learning Platform</h1>

<p align="center">
  <strong>An AI-Powered Personalized Education System</strong>
</p>

<p align="center">
  <em>Transforming education through intelligent tutoring, automated assessment, and predictive analytics</em>
</p>

---

## Overview

**RUMAN AI** is a comprehensive learning management system that leverages cutting-edge AI/ML technologies to deliver personalized education experiences. The platform features RAG-powered AI chatbots (supporting **Gemini** and **Mistral**), automated quiz generation, intelligent answer evaluation, and student performance prediction.

### Key Features

| Feature | Description |
|---------|-------------|
| **Multi-LLM Chatbots** | RAG-powered tutors using **Gemini** or **Mistral** |
| **Smart Quizzes** | AI-generated questions with automatic grading |
| **Performance Prediction** | ML models to identify at-risk students |
| **Learning Analytics** | Clustering to identify learning gaps |
| **Adaptive Difficulty** | Questions adjust to student ability |

---

## Technology Stack

```
+------------------+-------------------+------------------------+
|     BACKEND      |       AI/ML       |       FRONTEND         |
+------------------+-------------------+------------------------+
| FastAPI          | Google Gemini API | React + Vite           |
| SQLAlchemy       | Mistral AI        | Axios                  |
| SQLite           | Scikit-learn      | Modern CSS             |
| JWT Auth         | ChromaDB          | Responsive Design      |
| bcrypt           | LangChain         |                        |
+------------------+-------------------+------------------------+
```

---

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Node.js 18+ (for frontend)
- API Keys: Google Gemini and/or Mistral AI

### 1. Clone the Repository

```bash
git clone https://github.com/rashmeet-03/ruman-ai-learning-platform.git
cd ruman-ai-learning-platform
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv myenv

# Activate virtual environment
# Windows:
myenv\Scripts\activate
# macOS/Linux:
source myenv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux

# Edit .env and add your API keys:
# GEMINI_API_KEY=your_key
# MISTRAL_API_KEY=your_key

# Initialize database
python init_db.py

# Start the server
python app.py
```

The API will be available at: **http://localhost:8000**

API Documentation: **http://localhost:8000/docs**

### 3. Frontend Setup (Optional)

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at: **http://localhost:5173**

---

## Default Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Teacher | `teacher1` | `teacher123` |
| Student | `student1` | `student123` |

---

## Jupyter Notebooks

This project includes a comprehensive Jupyter notebook for demonstration and documentation:

### Available Notebook

| Notebook | Description |
|----------|-------------|
| `RUMAN_AI_Project_Notebook.ipynb` | **Main Project Notebook** - Complete demonstration with 8 sections covering ML models, RAG system, and evaluation metrics |

### Running the Notebook

#### Option 1: Using Jupyter Lab/Notebook

```bash
# Install Jupyter (if not installed)
pip install jupyter

# Launch Jupyter
jupyter notebook

# Or use Jupyter Lab
pip install jupyterlab
jupyter lab
```

#### Option 2: Using VS Code

1. Install the "Jupyter" extension in VS Code
2. Open the `.ipynb` file
3. Click "Run All" to execute all cells

### Notebook Contents

The notebook covers:

1. **Problem Definition & Objective** - Educational challenges and project goals
2. **Selected Project Track** - AI/ML techniques and technology stack
3. **Data Understanding & Preparation** - Data generation and visualization
4. **Model/System Design** - Architecture and ML model design
5. **Core Implementation** - Random Forest, K-Means, RAG system (Gemini/Mistral), Answer evaluation
6. **Evaluation & Analysis** - Performance metrics and results
7. **Ethical Considerations** - Privacy, fairness, and responsible AI
8. **Conclusion & Future Scope** - Summary and roadmap

---

## Project Structure

```
ruman-ai-learning-platform/
|
|-- backend/                 # FastAPI backend
|   |-- ai_services/         # AI/ML modules
|   |   |-- ai_assessment.py    # Quiz generation & answer evaluation
|   |   |-- ml_models.py        # Performance prediction & clustering
|   |   |-- rag_system.py       # RAG chatbot system
|   |   |-- llm_providers.py    # Gemini/Mistral integration
|   |   |-- ml_scoring.py       # Hybrid ML scoring
|   |-- routes/              # API endpoints
|   |-- models.py            # SQLAlchemy database models
|   |-- app.py               # FastAPI application
|   |-- config.py            # Configuration settings
|   |-- requirements.txt     # Python dependencies
|
|-- frontend/                # React frontend
|   |-- src/
|   |   |-- pages/           # Dashboard components
|   |   |-- components/      # Reusable UI components
|
|-- database/                # SQL schemas
|-- docs/                    # API documentation
|
|-- RUMAN_AI_Project_Notebook.ipynb    # Main Jupyter notebook
```

---

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login

### Teacher APIs
- `POST /api/teacher/courses` - Create course
- `POST /api/teacher/courses/{id}/chatbots` - Create AI chatbot
- `POST /api/teacher/chatbots/{id}/upload` - Upload course materials
- `POST /api/teacher/courses/{id}/quizzes` - Create quiz

### Student APIs
- `GET /api/student/courses` - View enrolled courses
- `POST /api/student/chatbots/{id}/chat` - Chat with AI tutor
- `POST /api/student/quizzes/{id}/attempt` - Take quiz

For complete API documentation, visit: **http://localhost:8000/docs**

---

## AI/ML Features

### 1. Multi-LLM RAG Chatbot
- **Providers:** Google Gemini & Mistral AI
- **Context:** RAG-based context injection from course documents
- **Vector DB:** ChromaDB for semantic search

### 2. Performance Prediction
- Random Forest classifier
- ~90% accuracy in risk prediction
- Features: quiz scores, engagement, activity

### 3. Learning Gap Analysis
- K-Means clustering
- Student segmentation
- Targeted intervention recommendations

### 4. Automated Assessment
- AI-powered quiz generation
- Hybrid ML answer scoring
- TF-IDF + semantic similarity

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
