from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Date, CheckConstraint
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import json

Base = declarative_base()

# ============================================
# CORE TABLES
# ============================================

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    courses_teaching = relationship("Course", back_populates="teacher", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")
    quiz_attempts = relationship("QuizAttempt", back_populates="student", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="student", cascade="all, delete-orphan")
    progress = relationship("StudentProgress", back_populates="student", uselist=False, cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("role IN ('admin', 'teacher', 'student')", name='check_user_role'),
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"


class Course(Base):
    __tablename__ = 'courses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    teacher_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    teacher = relationship("User", back_populates="courses_teaching")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    chatbot_assignments = relationship("ChatbotCourse", back_populates="course", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="course", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="course", cascade="all, delete-orphan")
    
    @property
    def chatbots(self):
        """Get all chatbots assigned to this course"""
        return [assignment.chatbot for assignment in self.chatbot_assignments]
    
    def __repr__(self):
        return f"<Course(id={self.id}, name='{self.name}')>"


class Enrollment(Base):
    __tablename__ = 'enrollments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
    
    def __repr__(self):
        return f"<Enrollment(student_id={self.student_id}, course_id={self.course_id})>"


# ============================================
# AI CHATBOT TABLES
# ============================================

# Junction table for many-to-many: Chatbot <-> Course
class ChatbotCourse(Base):
    __tablename__ = 'chatbot_courses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    chatbot_id = Column(Integer, ForeignKey('chatbots.id', ondelete='CASCADE'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    chatbot = relationship("Chatbot", back_populates="course_assignments")
    course = relationship("Course", back_populates="chatbot_assignments")


class Chatbot(Base):
    __tablename__ = 'chatbots'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    teacher_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)  # Owner
    system_prompt = Column(Text)
    collection_name = Column(String(100))  # ChromaDB collection
    
    # LLM Configuration - Teacher can choose provider and model
    llm_provider = Column(String(50), default='gemini')  # 'gemini' or 'mistral'
    llm_model = Column(String(100), default='gemini-2.0-flash')  # Specific model name
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    teacher = relationship("User", backref="chatbots_created")
    course_assignments = relationship("ChatbotCourse", back_populates="chatbot", cascade="all, delete-orphan")
    documents = relationship("ChatbotDocument", back_populates="chatbot", cascade="all, delete-orphan")
    messages = relationship("ChatMessage", back_populates="chatbot", cascade="all, delete-orphan")
    
    @property
    def courses(self):
        """Get all courses this chatbot is assigned to"""
        return [assignment.course for assignment in self.course_assignments]
    
    def __repr__(self):
        return f"<Chatbot(id={self.id}, name='{self.name}', llm='{self.llm_provider}')>"


class ChatbotDocument(Base):
    __tablename__ = 'chatbot_documents'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    chatbot_id = Column(Integer, ForeignKey('chatbots.id', ondelete='CASCADE'), nullable=False)
    filename = Column(String(255), nullable=False)
    content_type = Column(String(50))
    file_path = Column(String(500))
    chunk_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    chatbot = relationship("Chatbot", back_populates="documents")
    
    def __repr__(self):
        return f"<ChatbotDocument(id={self.id}, filename='{self.filename}')>"


class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    chatbot_id = Column(Integer, ForeignKey('chatbots.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    chatbot = relationship("Chatbot", back_populates="messages")
    user = relationship("User", back_populates="chat_messages")
    
    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant')", name='check_message_role'),
    )
    
    def __repr__(self):
        return f"<ChatMessage(id={self.id}, role='{self.role}')>"


# ============================================
# ASSESSMENT TABLES
# ============================================

class Quiz(Base):
    __tablename__ = 'quizzes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    course_id = Column(Integer, ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    time_limit_minutes = Column(Integer)
    max_attempts = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    course = relationship("Course", back_populates="quizzes")
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Quiz(id={self.id}, title='{self.title}')>"


class QuizQuestion(Base):
    __tablename__ = 'quiz_questions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    quiz_id = Column(Integer, ForeignKey('quizzes.id', ondelete='CASCADE'), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(20))  # 'mcq', 'true_false', 'short_answer'
    options = Column(Text)  # JSON string for MCQ options
    correct_answer = Column(Text, nullable=False)
    points = Column(Float, default=1.0)
    explanation = Column(Text)
    
    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    
    __table_args__ = (
        CheckConstraint("question_type IN ('mcq', 'true_false', 'short_answer')", name='check_question_type'),
    )
    
    @property
    def options_list(self):
        """Parse JSON options string to list"""
        if self.options:
            return json.loads(self.options)
        return []
    
    @options_list.setter
    def options_list(self, value):
        """Convert list to JSON string"""
        self.options = json.dumps(value)
    
    def __repr__(self):
        return f"<QuizQuestion(id={self.id}, type='{self.question_type}')>"


class QuizAttempt(Base):
    __tablename__ = 'quiz_attempts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    quiz_id = Column(Integer, ForeignKey('quizzes.id', ondelete='CASCADE'), nullable=False)
    student_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    score = Column(Float)
    max_score = Column(Float)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    answers = Column(Text)  # JSON string: {"question_id": "answer", ...}
    
    # Relationships
    quiz = relationship("Quiz", back_populates="attempts")
    student = relationship("User", back_populates="quiz_attempts")
    
    @property
    def answers_dict(self):
        """Parse JSON answers string to dict"""
        if self.answers:
            return json.loads(self.answers)
        return {}
    
    @answers_dict.setter
    def answers_dict(self, value):
        """Convert dict to JSON string"""
        self.answers = json.dumps(value)
    
    def __repr__(self):
        return f"<QuizAttempt(id={self.id}, score={self.score}/{self.max_score})>"


class Assignment(Base):
    __tablename__ = 'assignments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    course_id = Column(Integer, ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    max_score = Column(Float, default=100)
    due_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    course = relationship("Course", back_populates="assignments")
    submissions = relationship("Submission", back_populates="assignment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Assignment(id={self.id}, title='{self.title}')>"


class Submission(Base):
    __tablename__ = 'submissions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    assignment_id = Column(Integer, ForeignKey('assignments.id', ondelete='CASCADE'), nullable=False)
    student_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    content = Column(Text)
    file_path = Column(String(500))
    score = Column(Float)
    ai_feedback = Column(Text)
    teacher_feedback = Column(Text)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    graded_at = Column(DateTime)
    
    # Relationships
    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("User", back_populates="submissions")
    
    def __repr__(self):
        return f"<Submission(id={self.id}, score={self.score})>"


# ============================================
# GAMIFICATION TABLES
# ============================================

class StudentProgress(Base):
    __tablename__ = 'student_progress'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    xp_points = Column(Integer, default=0)
    level = Column(Integer, default=1)
    streak_days = Column(Integer, default=0)
    last_activity_date = Column(Date)
    badges = Column(Text, default='[]')  # JSON array of badge IDs
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("User", back_populates="progress")
    
    @property
    def badges_list(self):
        """Parse JSON badges string to list"""
        if self.badges:
            return json.loads(self.badges)
        return []
    
    @badges_list.setter
    def badges_list(self, value):
        """Convert list to JSON string"""
        self.badges = json.dumps(value)
    
    def __repr__(self):
        return f"<StudentProgress(student_id={self.student_id}, level={self.level}, xp={self.xp_points})>"


class Achievement(Base):
    __tablename__ = 'achievements'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    badge_icon = Column(String(50))
    xp_reward = Column(Integer, default=0)
    condition_type = Column(String(50))  # 'quiz_score', 'streak', 'course_complete', etc.
    condition_value = Column(Integer)
    
    def __repr__(self):
        return f"<Achievement(id={self.id}, name='{self.name}')>"


class ActivityLog(Base):
    __tablename__ = 'activity_log'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    activity_type = Column(String(50), nullable=False)  # 'quiz_start', 'quiz_complete', etc.
    entity_type = Column(String(50))  # 'quiz', 'assignment', 'chatbot'
    entity_id = Column(Integer)
    action_metadata = Column(Text)  # JSON for additional data (renamed from 'metadata' - SQLAlchemy reserved)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="activity_logs")
    
    @property
    def metadata_dict(self):
        """Parse JSON metadata string to dict"""
        if self.action_metadata:
            return json.loads(self.action_metadata)
        return {}
    
    @metadata_dict.setter
    def metadata_dict(self, value):
        """Convert dict to JSON string"""
        self.action_metadata = json.dumps(value)
    
    def __repr__(self):
        return f"<ActivityLog(id={self.id}, user_id={self.user_id}, type='{self.activity_type}')>"
