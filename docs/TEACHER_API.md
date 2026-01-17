# Teacher API Documentation

## Overview

Teacher endpoints allow educators to create and manage courses, AI chatbots, quizzes, assignments, and view analytics.

**Base URL**: `/api/teacher`  
**Authentication**: Requires JWT token with `teacher` or `admin` role

---

## Course Management

### Create Course
**POST** `/api/teacher/courses`

**Request Body**:
```json
{
  "name": "Introduction to Python",
  "description": "Learn Python programming from scratch"
}
```

**Response (201 Created)**:
```json
{
  "id": 1,
  "name": "Introduction to Python",
  "description": "Learn Python programming from scratch",
  "teacher_id": 2,
  "is_active": true,
  "created_at": "2026-01-16T21:00:00"
}
```

### List My Courses
**GET** `/api/teacher/courses`

Returns all courses created by the authenticated teacher.

### Get Course Details
**GET** `/api/teacher/courses/{course_id}`

### Update Course
**PUT** `/api/teacher/courses/{course_id}`

### Delete Course
**DELETE** `/api/teacher/courses/{course_id}`

⚠️ **Warning**: Deletes all chatbots, quizzes, and assignments!

---

## Student Enrollment

### Enroll Student
**POST** `/api/teacher/courses/{course_id}/enroll/{student_id}`

### List Enrolled Students
**GET** `/api/teacher/courses/{course_id}/students`

**Response**:
```json
[
  {
    "id": 3,
    "username": "student1",
    "email": "student@example.com",
    "enrolled_at": "2026-01-16T21:05:00"
  }
]
```

---

## Chatbot Management

### Create Chatbot
**POST** `/api/teacher/courses/{course_id}/chatbots`

**Request Body**:
```json
{
  "name": "Python Tutor",
  "description": "AI assistant for Python questions",
  "system_prompt": "You are a Python programming tutor..."
}
```

**Response (201 Created)**:
```json
{
  "id": 1,
  "name": "Python Tutor",
  "description": "AI assistant for Python questions",
  "course_id": 1,
  "system_prompt": "You are a Python programming tutor...",
  "collection_name": "course_1_chatbot_1705423200.123",
  "is_active": true,
  "created_at": "2026-01-16T21:10:00"
}
```

### Upload Document to Chatbot
**POST** `/api/teacher/chatbots/{chatbot_id}/upload`

**Request**: `multipart/form-data` with file

**Allowed File Types**: PDF, TXT

**Response**:
```json
{
  "message": "Document uploaded successfully",
  "document_id": 1,
  "filename": "python_basics.pdf",
  "note": "Document will be processed and embedded for RAG (Phase 5 AI implementation)"
}
```

### List Course Chatbots
**GET** `/api/teacher/courses/{course_id}/chatbots`

---

## Quiz Management

### Create Quiz
**POST** `/api/teacher/courses/{course_id}/quizzes`

**Request Body**:
```json
{
  "title": "Python Basics Quiz",
  "description": "Test your knowledge of Python fundamentals",
  "time_limit_minutes": 30,
  "max_attempts": 2,
  "questions": [
    {
      "question_text": "What is the output of print(2+2)?",
      "question_type": "mcq",
      "options": ["3", "4", "5", "22"],
      "correct_answer": "4",
      "points": 1.0,
      "explanation": "2+2 equals 4 in Python"
    }
  ]
}
```

### Add Question to Quiz
**POST** `/api/teacher/quizzes/{quiz_id}/questions`

**Request Body**:
```json
{
  "question_text": "Is Python case-sensitive?",
  "question_type": "true_false",
  "options": ["True", "False"],
  "correct_answer": "True",
  "points": 1.0,
  "explanation": "Python is case-sensitive"
}
```

### List Course Quizzes
**GET** `/api/teacher/courses/{course_id}/quizzes`

---

## Assignment Management

### Create Assignment
**POST** `/api/teacher/courses/{course_id}/assignments`

**Request Body**:
```json
{
  "title": "Python Functions Assignment",
  "description": "Write 5 functions demonstrating different concepts",
  "max_score": 100,
  "due_date": "2026-01-25T23:59:59"
}
```

### List Course Assignments
**GET** `/api/teacher/courses/{course_id}/assignments`

### List Assignment Submissions
**GET** `/api/teacher/assignments/{assignment_id}/submissions`

**Response**:
```json
[
  {
    "id": 1,
    "student_id": 3,
    "student_username": "student1",
    "content": "Here are my solutions...",
    "score": 85,
    "ai_feedback": "Good work on functions 1-4...",
    "teacher_feedback": "Great job!",
    "submitted_at": "2026-01-20T15:30:00",
    "graded_at": "2026-01-21T10:00:00"
  }
]
```

### Grade Submission
**PUT** `/api/teacher/submissions/{submission_id}/grade?score=85&feedback=Great job!`

---

## Analytics Dashboard

### Get Course Analytics
**GET** `/api/teacher/courses/{course_id}/analytics`

**Response**:
```json
{
  "course_id": 1,
  "course_name": "Introduction to Python",
  "total_students": 25,
  "total_quizzes": 5,
  "total_assignments": 3,
  "quiz_statistics": {
    "total_attempts": 120,
    "average_score": 78.5
  },
  "assignment_statistics": {
    "total_submissions": 70,
    "graded_submissions": 65,
    "average_score": 82.3
  },
  "student_performance": [
    {
      "student_id": 3,
      "username": "student1",
      "quiz_average": 85.5,
      "assignment_average": 90.0,
      "overall_average": 87.75,
      "quizzes_attempted": 5,
      "assignments_submitted": 3
    }
  ]
}
```

---

## Complete API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/teacher/courses` | POST | Create course |
| `/api/teacher/courses` | GET | List my courses |
| `/api/teacher/courses/{id}` | GET | Get course details |
| `/api/teacher/courses/{id}` | PUT | Update course |
| `/api/teacher/courses/{id}` | DELETE | Delete course |
| `/api/teacher/courses/{id}/enroll/{student_id}` | POST | Enroll student |
| `/api/teacher/courses/{id}/students` | GET | List enrolled students |
| `/api/teacher/courses/{id}/chatbots` | POST | Create chatbot |
| `/api/teacher/courses/{id}/chatbots` | GET | List chatbots |
| `/api/teacher/chatbots/{id}/upload` | POST | Upload document |
| `/api/teacher/courses/{id}/quizzes` | POST | Create quiz |
| `/api/teacher/courses/{id}/quizzes` | GET | List quizzes |
| `/api/teacher/quizzes/{id}/questions` | POST | Add question |
| `/api/teacher/courses/{id}/assignments` | POST | Create assignment |
| `/api/teacher/courses/{id}/assignments` | GET | List assignments |
| `/api/teacher/assignments/{id}/submissions` | GET | List submissions |
| `/api/teacher/submissions/{id}/grade` | PUT | Grade submission |
| `/api/teacher/courses/{id}/analytics` | GET | Get analytics |

---

## Usage Example (Python)

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Login as teacher
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": "teacher1", "password": "teacher123"}
)
token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Create a course
course_data = {
    "name": "Data Structures",
    "description": "Learn about arrays, linked lists, trees"
}
course_response = requests.post(
    f"{BASE_URL}/teacher/courses",
    json=course_data,
    headers=headers
)
course_id = course_response.json()["id"]

# Create a chatbot
chatbot_data = {
    "name": "DS Tutor",
    "description": "Ask me about data structures"
}
chatbot_response = requests.post(
    f"{BASE_URL}/teacher/courses/{course_id}/chatbots",
    json=chatbot_data,
    headers=headers
)

# Upload a document
with open("algorithms.pdf", "rb") as f:
    files = {"file": f}
    upload_response = requests.post(
        f"{BASE_URL}/teacher/chatbots/1/upload",
        files=files,
        headers=headers
    )

# Create a quiz
quiz_data = {
    "title": "Arrays Quiz",
    "description": "Test your array knowledge",
    "time_limit_minutes": 20,
    "max_attempts": 1,
    "questions": [
        {
            "question_text": "What is the time complexity of accessing an element in an array?",
            "question_type": "mcq",
            "options": ["O(1)", "O(n)", "O(log n)", "O(n^2)"],
            "correct_answer": "O(1)",
            "points": 2.0
        }
    ]
}
quiz_response = requests.post(
    f"{BASE_URL}/teacher/courses/{course_id}/quizzes",
    json=quiz_data,
    headers=headers
)

# Get analytics
analytics_response = requests.get(
    f"{BASE_URL}/teacher/courses/{course_id}/analytics",
    headers=headers
)
print(analytics_response.json())
```

---

## Testing

Visit **http://localhost:8000/docs** and:

1. Login as `teacher1` / `teacher123`
2. Click "Authorize" and paste the token
3. Test all teacher endpoints interactively
