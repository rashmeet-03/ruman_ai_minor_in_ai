from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# ============================================
# USER SCHEMAS
# ============================================

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role: str = Field(..., pattern="^(admin|teacher|student)$")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None


# ============================================
# COURSE SCHEMAS
# ============================================

class CourseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class CourseCreate(CourseBase):
    pass


class CourseResponse(CourseBase):
    id: int
    teacher_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# CHATBOT SCHEMAS
# ============================================

class ChatbotBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    llm_provider: str = Field(default="gemini", pattern="^(gemini|mistral)$")
    llm_model: Optional[str] = None


class ChatbotCreate(ChatbotBase):
    pass  # course_id comes from URL path


class ChatbotResponse(ChatbotBase):
    id: int
    course_id: int
    collection_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    document_count: Optional[int] = 0
    
    class Config:
        from_attributes = True


class ChatMessageCreate(BaseModel):
    chatbot_id: int
    content: str


class ChatMessageResponse(BaseModel):
    id: int
    chatbot_id: int
    user_id: int
    role: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# QUIZ SCHEMAS
# ============================================

class QuizQuestionBase(BaseModel):
    question_text: str
    question_type: str = Field(..., pattern="^(mcq|true_false|short_answer)$")
    options: Optional[List[str]] = None
    correct_answer: str
    points: float = 1.0
    explanation: Optional[str] = None


class QuizQuestionCreate(QuizQuestionBase):
    pass


class QuizQuestionResponse(QuizQuestionBase):
    id: int
    quiz_id: int
    
    class Config:
        from_attributes = True


class QuizBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    time_limit_minutes: Optional[int] = None
    max_attempts: int = 1


class QuizCreate(QuizBase):
    course_id: int
    questions: Optional[List[QuizQuestionCreate]] = None


class QuizResponse(QuizBase):
    id: int
    course_id: int
    is_active: bool
    created_at: datetime
    questions: Optional[List[QuizQuestionResponse]] = None
    
    class Config:
        from_attributes = True


class QuizAttemptCreate(BaseModel):
    quiz_id: int


class QuizAttemptSubmit(BaseModel):
    answers: dict  # {question_id: answer}


class QuizAttemptResponse(BaseModel):
    id: int
    quiz_id: int
    student_id: int
    score: Optional[float] = None
    max_score: Optional[float] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================
# ASSIGNMENT SCHEMAS
# ============================================

class AssignmentBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    max_score: float = 100
    due_date: Optional[datetime] = None


class AssignmentCreate(AssignmentBase):
    course_id: int


class AssignmentResponse(AssignmentBase):
    id: int
    course_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class SubmissionCreate(BaseModel):
    assignment_id: int
    content: str


class SubmissionResponse(BaseModel):
    id: int
    assignment_id: int
    student_id: int
    content: Optional[str] = None
    score: Optional[float] = None
    ai_feedback: Optional[str] = None
    teacher_feedback: Optional[str] = None
    submitted_at: datetime
    graded_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================
# GAMIFICATION SCHEMAS
# ============================================

class StudentProgressResponse(BaseModel):
    student_id: int
    xp_points: int
    level: int
    streak_days: int
    badges: List[int]
    
    class Config:
        from_attributes = True


class AchievementResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    badge_icon: Optional[str] = None
    xp_reward: int
    
    class Config:
        from_attributes = True
