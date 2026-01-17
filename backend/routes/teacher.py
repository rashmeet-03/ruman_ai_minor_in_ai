"""
Teacher routes for course management, chatbot creation, quizzes, assignments, and analytics
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
import os
import json

from database import get_db
from models import (
    User, Course, Enrollment, Chatbot, ChatbotDocument, ChatbotCourse,
    Quiz, QuizQuestion, Assignment, Submission, QuizAttempt, StudentProgress
)
from schemas import (
    CourseCreate, CourseResponse,
    ChatbotCreate, ChatbotResponse,
    QuizCreate, QuizResponse, QuizQuestionCreate,
    AssignmentCreate, AssignmentResponse
)
from routes.auth import get_current_teacher
from config import settings

router = APIRouter()


# ============================================
# COURSE MANAGEMENT
# ============================================

@router.post("/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    course_data: CourseCreate,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    Create a new course
    
    Teachers can create courses they will teach.
    """
    new_course = Course(
        name=course_data.name,
        description=course_data.description,
        teacher_id=current_teacher.id,
        is_active=True
    )
    
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    
    return new_course


@router.get("/courses")
def list_my_courses(
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    List all courses created by the current teacher with chatbots, quizzes, assignments
    """
    courses = db.query(Course).filter(Course.teacher_id == current_teacher.id).all()
    
    result = []
    for course in courses:
        # Get chatbots assigned to this course via junction table
        chatbots = db.query(Chatbot).join(ChatbotCourse).filter(
            ChatbotCourse.course_id == course.id
        ).all()
        
        chatbot_list = []
        for bot in chatbots:
            doc_count = db.query(ChatbotDocument).filter(ChatbotDocument.chatbot_id == bot.id).count()
            # Get all courses this chatbot is assigned to
            assigned_courses = db.query(Course).join(ChatbotCourse).filter(
                ChatbotCourse.chatbot_id == bot.id
            ).all()
            chatbot_list.append({
                "id": bot.id,
                "name": bot.name,
                "description": bot.description,
                "system_prompt": bot.system_prompt,
                "llm_provider": bot.llm_provider,
                "llm_model": bot.llm_model,
                "is_active": bot.is_active,
                "document_count": doc_count,
                "assigned_courses": [{"id": c.id, "name": c.name} for c in assigned_courses]
            })
        
        result.append({
            "id": course.id,
            "name": course.name,
            "description": course.description,
            "teacher_id": course.teacher_id,
            "is_active": course.is_active,
            "created_at": course.created_at,
            "chatbots": chatbot_list,
            "quizzes": course.quizzes,
            "assignments": course.assignments
        })
    
    return result


@router.get("/courses/{course_id}", response_model=CourseResponse)
def get_course(
    course_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific course
    """
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.teacher_id == current_teacher.id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or you don't have access"
        )
    
    return course


@router.put("/courses/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: int,
    course_data: CourseCreate,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    Update a course
    """
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.teacher_id == current_teacher.id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or you don't have access"
        )
    
    course.name = course_data.name
    course.description = course_data.description
    
    db.commit()
    db.refresh(course)
    
    return course


@router.delete("/courses/{course_id}")
def delete_course(
    course_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    Delete a course
    
    WARNING: This will delete all associated chatbots, quizzes, and assignments!
    """
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.teacher_id == current_teacher.id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or you don't have access"
        )
    
    course_name = course.name
    db.delete(course)
    db.commit()
    
    return {"message": f"Course '{course_name}' deleted successfully"}


# ============================================
# STUDENT ENROLLMENT MANAGEMENT
# ============================================

@router.post("/courses/{course_id}/enroll/{student_id}")
def enroll_student(
    course_id: int,
    student_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    Enroll a student in the course
    """
    # Verify course ownership
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.teacher_id == current_teacher.id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or you don't have access"
        )
    
    # Verify student exists
    student = db.query(User).filter(User.id == student_id, User.role == "student").first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Check if already enrolled
    existing = db.query(Enrollment).filter(
        Enrollment.course_id == course_id,
        Enrollment.student_id == student_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student already enrolled"
        )
    
    # Create enrollment
    enrollment = Enrollment(
        course_id=course_id,
        student_id=student_id
    )
    
    db.add(enrollment)
    db.commit()
    
    return {"message": f"Student {student.username} enrolled in {course.name}"}


@router.get("/courses/{course_id}/students")
def list_enrolled_students(
    course_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    List all students enrolled in a course
    """
    # Verify course ownership
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.teacher_id == current_teacher.id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or you don't have access"
        )
    
    enrollments = db.query(Enrollment).filter(Enrollment.course_id == course_id).all()
    
    students = []
    for enrollment in enrollments:
        student = enrollment.student
        students.append({
            "id": student.id,
            "username": student.username,
            "email": student.email,
            "enrolled_at": enrollment.enrolled_at
        })
    
    return students


# ============================================
# CHATBOT MANAGEMENT
# ============================================

@router.post("/courses/{course_id}/chatbots", status_code=status.HTTP_201_CREATED)
def create_chatbot(
    course_id: int,
    chatbot_data: ChatbotCreate,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    Create a new AI chatbot and assign to the course
    
    The chatbot will use RAG to answer student questions based on uploaded documents.
    """
    # Verify course ownership
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.teacher_id == current_teacher.id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or you don't have access"
        )
    
    # Generate unique collection name for ChromaDB
    collection_name = f"teacher_{current_teacher.id}_chatbot_{datetime.utcnow().timestamp()}"
    
    # Create chatbot owned by teacher
    new_chatbot = Chatbot(
        name=chatbot_data.name,
        description=chatbot_data.description,
        teacher_id=current_teacher.id,
        system_prompt=chatbot_data.system_prompt or "You are a helpful AI tutor. Answer student questions based on the provided course materials.",
        collection_name=collection_name,
        llm_provider=chatbot_data.llm_provider or "gemini",
        llm_model=chatbot_data.llm_model or "gemini-2.0-flash",
        is_active=True
    )
    
    db.add(new_chatbot)
    db.flush()  # Get the ID
    
    # Assign chatbot to the course
    assignment = ChatbotCourse(
        chatbot_id=new_chatbot.id,
        course_id=course_id
    )
    db.add(assignment)
    db.commit()
    db.refresh(new_chatbot)
    
    return {
        "id": new_chatbot.id,
        "name": new_chatbot.name,
        "description": new_chatbot.description,
        "llm_provider": new_chatbot.llm_provider,
        "llm_model": new_chatbot.llm_model,
        "collection_name": new_chatbot.collection_name,
        "is_active": new_chatbot.is_active,
        "created_at": new_chatbot.created_at,
        "courses": [{"id": course.id, "name": course.name}]
    }


@router.post("/chatbots/{chatbot_id}/upload")
async def upload_document_to_chatbot(
    chatbot_id: int,
    file: UploadFile = File(...),
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    Upload a document (PDF/TXT) to a chatbot for RAG
    
    The document will be processed, chunked, and embedded for retrieval.
    """
    # Verify chatbot ownership (teacher_id)
    chatbot = db.query(Chatbot).filter(
        Chatbot.id == chatbot_id,
        Chatbot.teacher_id == current_teacher.id
    ).first()
    
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbot not found or you don't have access"
        )
    
    # Validate file type
    allowed_types = ["application/pdf", "text/plain"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and TXT files are allowed"
        )
    
    # Save file
    os.makedirs(settings.UPLOAD_DIRECTORY, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIRECTORY, f"chatbot_{chatbot_id}_{file.filename}")
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Create document record first
    doc = ChatbotDocument(
        chatbot_id=chatbot_id,
        filename=file.filename,
        content_type=file.content_type,
        file_path=file_path,
        chunk_count=0
    )
    
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    # Process document immediately for RAG (Create Embeddings)
    try:
        from ai_services import get_rag_system
        rag_system = get_rag_system()
        
        chunks = rag_system.process_and_store_document(
            file_path,
            chatbot.collection_name
        )
        
        # Update chunk count
        doc.chunk_count = chunks
        db.commit()
        
        note = f"Processed {chunks} chunks and added to knowledge base."
    except Exception as e:
        print(f"Error processing document: {e}")
        note = "Uploaded, but failed to process embeddings. Please try 'Process Documents' button."
    
    return {
        "message": "Document uploaded and processed successfully",
        "document_id": doc.id,
        "filename": file.filename,
        "note": note,
        "chunk_count": doc.chunk_count
    }


@router.post("/chatbots/{chatbot_id}/assign/{course_id}")
def assign_chatbot_to_course(
    chatbot_id: int,
    course_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    Assign an existing chatbot to another course
    
    Allows the same chatbot to be used in multiple courses.
    """
    # Verify chatbot ownership
    chatbot = db.query(Chatbot).filter(
        Chatbot.id == chatbot_id,
        Chatbot.teacher_id == current_teacher.id
    ).first()
    
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbot not found or you don't have access"
        )
    
    # Verify course ownership
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.teacher_id == current_teacher.id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or you don't have access"
        )
    
    # Check if already assigned
    existing = db.query(ChatbotCourse).filter(
        ChatbotCourse.chatbot_id == chatbot_id,
        ChatbotCourse.course_id == course_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chatbot is already assigned to this course"
        )
    
    # Create assignment
    assignment = ChatbotCourse(
        chatbot_id=chatbot_id,
        course_id=course_id
    )
    db.add(assignment)
    db.commit()
    
    return {
        "message": f"Chatbot '{chatbot.name}' assigned to '{course.name}'",
        "chatbot_id": chatbot_id,
        "course_id": course_id
    }


@router.delete("/chatbots/{chatbot_id}/unassign/{course_id}")
def unassign_chatbot_from_course(
    chatbot_id: int,
    course_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Remove a chatbot from a course"""
    # Verify chatbot ownership
    chatbot = db.query(Chatbot).filter(
        Chatbot.id == chatbot_id,
        Chatbot.teacher_id == current_teacher.id
    ).first()
    
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbot not found or you don't have access"
        )
    
    # Find and delete assignment
    assignment = db.query(ChatbotCourse).filter(
        ChatbotCourse.chatbot_id == chatbot_id,
        ChatbotCourse.course_id == course_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbot is not assigned to this course"
        )
    
    db.delete(assignment)
    db.commit()
    
    return {"message": "Chatbot removed from course"}


@router.get("/courses/{course_id}/chatbots")
def list_course_chatbots(
    course_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    List all chatbots assigned to a course
    """
    # Verify course ownership
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.teacher_id == current_teacher.id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or you don't have access"
        )
    
    # Get chatbots via junction table
    chatbots = db.query(Chatbot).join(ChatbotCourse).filter(
        ChatbotCourse.course_id == course_id
    ).all()
    
    # Return with document count
    result = []
    for bot in chatbots:
        doc_count = db.query(ChatbotDocument).filter(ChatbotDocument.chatbot_id == bot.id).count()
        result.append({
            "id": bot.id,
            "name": bot.name,
            "description": bot.description,
            "system_prompt": bot.system_prompt,
            "llm_provider": bot.llm_provider,
            "llm_model": bot.llm_model,
            "collection_name": bot.collection_name,
            "is_active": bot.is_active,
            "created_at": bot.created_at,
            "document_count": doc_count
        })
    
    return result


@router.get("/chatbots/{chatbot_id}")
def get_chatbot(
    chatbot_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get chatbot details with courses and documents"""
    chatbot = db.query(Chatbot).filter(
        Chatbot.id == chatbot_id,
        Chatbot.teacher_id == current_teacher.id
    ).first()
    
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    
    # Get assigned courses
    courses = db.query(Course).join(ChatbotCourse).filter(
        ChatbotCourse.chatbot_id == chatbot_id
    ).all()
    
    # Get documents
    docs = db.query(ChatbotDocument).filter(ChatbotDocument.chatbot_id == chatbot_id).all()
    
    return {
        "id": chatbot.id,
        "name": chatbot.name,
        "description": chatbot.description,
        "system_prompt": chatbot.system_prompt,
        "llm_provider": chatbot.llm_provider,
        "llm_model": chatbot.llm_model,
        "is_active": chatbot.is_active,
        "courses": [{"id": c.id, "name": c.name} for c in courses],
        "documents": [{"id": d.id, "filename": d.filename, "created_at": d.created_at} for d in docs]
    }


@router.put("/chatbots/{chatbot_id}")
def update_chatbot(
    chatbot_id: int,
    name: str = None,
    description: str = None,
    system_prompt: str = None,
    llm_provider: str = None,
    llm_model: str = None,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Update chatbot settings"""
    chatbot = db.query(Chatbot).filter(
        Chatbot.id == chatbot_id,
        Chatbot.teacher_id == current_teacher.id
    ).first()
    
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    
    if name:
        chatbot.name = name
    if description is not None:
        chatbot.description = description
    if system_prompt is not None:
        chatbot.system_prompt = system_prompt
    if llm_provider:
        chatbot.llm_provider = llm_provider
    if llm_model:
        chatbot.llm_model = llm_model
    
    db.commit()
    return {"message": "Chatbot updated successfully"}


@router.get("/chatbots/{chatbot_id}/documents")
def list_chatbot_documents(
    chatbot_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """List all documents for a chatbot"""
    chatbot = db.query(Chatbot).filter(
        Chatbot.id == chatbot_id,
        Chatbot.teacher_id == current_teacher.id
    ).first()
    
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    
    docs = db.query(ChatbotDocument).filter(ChatbotDocument.chatbot_id == chatbot_id).all()
    return [{"id": d.id, "filename": d.filename, "created_at": d.created_at, "chunk_count": d.chunk_count} for d in docs]


@router.delete("/chatbots/{chatbot_id}/documents/{document_id}")
def delete_chatbot_document(
    chatbot_id: int,
    document_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Delete a document from chatbot knowledge base"""
    chatbot = db.query(Chatbot).filter(
        Chatbot.id == chatbot_id,
        Chatbot.teacher_id == current_teacher.id
    ).first()
    
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    
    doc = db.query(ChatbotDocument).filter(
        ChatbotDocument.id == document_id,
        ChatbotDocument.chatbot_id == chatbot_id
    ).first()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete file from disk if exists
    if doc.file_path and os.path.exists(doc.file_path):
        os.remove(doc.file_path)
    
    db.delete(doc)
    db.commit()
    return {"message": "Document deleted"}


@router.delete("/chatbots/{chatbot_id}")
def delete_chatbot(
    chatbot_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Delete a chatbot"""
    chatbot = db.query(Chatbot).filter(
        Chatbot.id == chatbot_id,
        Chatbot.teacher_id == current_teacher.id
    ).first()
    
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    
    db.delete(chatbot)
    db.commit()
    return {"message": "Chatbot deleted"}


@router.post("/chatbots/{chatbot_id}/publish")
def publish_chatbot(
    chatbot_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Publish chatbot to students"""
    chatbot = db.query(Chatbot).filter(
        Chatbot.id == chatbot_id,
        Chatbot.teacher_id == current_teacher.id
    ).first()
    
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    
    chatbot.is_active = True
    db.commit()
    
    return {"message": "Chatbot published", "is_active": True}


@router.post("/chatbots/{chatbot_id}/unpublish")
def unpublish_chatbot(
    chatbot_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Unpublish chatbot from students"""
    chatbot = db.query(Chatbot).filter(
        Chatbot.id == chatbot_id,
        Chatbot.teacher_id == current_teacher.id
    ).first()
    
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    
    chatbot.is_active = False
    db.commit()
    
    return {"message": "Chatbot unpublished", "is_active": False}


@router.post("/chatbots/{chatbot_id}/test")
def test_chatbot(
    chatbot_id: int,
    question: str,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    Test chatbot without saving to chat history
    For teacher preview before publishing
    """
    from ai_services import get_rag_system
    
    chatbot = db.query(Chatbot).filter(
        Chatbot.id == chatbot_id,
        Chatbot.teacher_id == current_teacher.id
    ).first()
    
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    
    try:
        rag_system = get_rag_system()
        
        result = rag_system.query(
            question=question,
            collection_name=chatbot.collection_name,
            system_prompt=chatbot.system_prompt,
            llm_provider=chatbot.llm_provider,
            llm_model=chatbot.llm_model
        )
        
        return {
            "answer": result["answer"],
            "sources": result.get("sources", []),
            "context_used": result.get("context_used", False),
            "test_mode": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# QUIZ MANAGEMENT
# ============================================

@router.post("/courses/{course_id}/quizzes", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
def create_quiz(
    course_id: int,
    quiz_data: QuizCreate,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    Create a new quiz for the course
    
    Can include questions or add them later.
    """
    # Verify course ownership
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.teacher_id == current_teacher.id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or you don't have access"
        )
    
    # Create quiz (inactive by default - must be forwarded to students)
    new_quiz = Quiz(
        title=quiz_data.title,
        description=quiz_data.description,
        course_id=course_id,
        time_limit_minutes=quiz_data.time_limit_minutes,
        max_attempts=quiz_data.max_attempts,
        is_active=False
    )
    
    db.add(new_quiz)
    db.commit()
    db.refresh(new_quiz)
    
    # Add questions if provided
    if quiz_data.questions:
        for q_data in quiz_data.questions:
            question = QuizQuestion(
                quiz_id=new_quiz.id,
                question_text=q_data.question_text,
                question_type=q_data.question_type,
                options=json.dumps(q_data.options) if q_data.options else None,
                correct_answer=q_data.correct_answer,
                points=q_data.points,
                explanation=q_data.explanation
            )
            db.add(question)
        
        db.commit()
        db.refresh(new_quiz)
    
    return new_quiz


@router.post("/quizzes/{quiz_id}/questions", status_code=status.HTTP_201_CREATED)
def add_quiz_question(
    quiz_id: int,
    question_data: QuizQuestionCreate,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    Add a question to an existing quiz
    """
    # Verify quiz ownership
    quiz = db.query(Quiz).join(Course).filter(
        Quiz.id == quiz_id,
        Course.teacher_id == current_teacher.id
    ).first()
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found or you don't have access"
        )
    
    question = QuizQuestion(
        quiz_id=quiz_id,
        question_text=question_data.question_text,
        question_type=question_data.question_type,
        options=json.dumps(question_data.options) if question_data.options else None,
        correct_answer=question_data.correct_answer,
        points=question_data.points,
        explanation=question_data.explanation
    )
    
    db.add(question)
    db.commit()
    db.refresh(question)
    
    return {
        "message": "Question added successfully",
        "question_id": question.id
    }


@router.get("/courses/{course_id}/quizzes")
def list_course_quizzes(
    course_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    List all quizzes for a course
    """
    # Verify course ownership
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.teacher_id == current_teacher.id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or you don't have access"
        )
    
    quizzes = db.query(Quiz).filter(Quiz.course_id == course_id).all()
    return quizzes


@router.post("/quizzes/{quiz_id}/publish")
def publish_quiz(
    quiz_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    Publish (forward) quiz to students
    Makes quiz visible and accessible to students
    """
    quiz = db.query(Quiz).join(Course).filter(
        Quiz.id == quiz_id,
        Course.teacher_id == current_teacher.id
    ).first()
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found or you don't have access"
        )
    
    quiz.is_active = True
    db.commit()
    
    return {
        "message": "Quiz published successfully",
        "quiz_id": quiz_id,
        "is_active": True
    }


@router.post("/quizzes/{quiz_id}/unpublish")
def unpublish_quiz(
    quiz_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    Unpublish (unforward) quiz from students
    Hides quiz from students (moves back to draft)
    """
    quiz = db.query(Quiz).join(Course).filter(
        Quiz.id == quiz_id,
        Course.teacher_id == current_teacher.id
    ).first()
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found or you don't have access"
        )
    
    quiz.is_active = False
    db.commit()
    
    return {
        "message": "Quiz unpublished successfully",
        "quiz_id": quiz_id,
        "is_active": False
    }


@router.get("/quizzes/{quiz_id}")
def get_quiz_details(
    quiz_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    Get quiz details with all questions
    For teacher review before publishing
    """
    quiz = db.query(Quiz).join(Course).filter(
        Quiz.id == quiz_id,
        Course.teacher_id == current_teacher.id
    ).first()
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found or you don't have access"
        )
    
    # Get all questions
    questions = db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz_id).all()
    
    return {
        "id": quiz.id,
        "title": quiz.title,
        "description": quiz.description,
        "course_id": quiz.course_id,
        "time_limit_minutes": quiz.time_limit_minutes,
        "max_attempts": quiz.max_attempts,
        "is_active": quiz.is_active,
        "created_at": quiz.created_at,
        "questions": [{
            "id": q.id,
            "question_text": q.question_text,
            "question_type": q.question_type,
            "options": json.loads(q.options) if q.options else None,
            "correct_answer": q.correct_answer,
            "points": q.points,
            "explanation": q.explanation
        } for q in questions]
    }


# ============================================
# ASSIGNMENT MANAGEMENT
# ============================================

@router.post("/courses/{course_id}/assignments", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
def create_assignment(
    course_id: int,
    assignment_data: AssignmentCreate,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    Create a new assignment for the course
    """
    # Verify course ownership
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.teacher_id == current_teacher.id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or you don't have access"
        )
    
    # Create assignment (inactive by default - must be forwarded to students)
    new_assignment = Assignment(
        title=assignment_data.title,
        description=assignment_data.description,
        course_id=course_id,
        max_score=assignment_data.max_score,
        due_date=assignment_data.due_date,
        is_active=False
    )
    
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    
    return new_assignment


@router.get("/courses/{course_id}/assignments")
def list_course_assignments(
    course_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    List all assignments for a course
    """
    # Verify course ownership
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.teacher_id == current_teacher.id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or you don't have access"
        )
    
    assignments = db.query(Assignment).filter(Assignment.course_id == course_id).all()
    return assignments


@router.post("/assignments/{assignment_id}/publish")
def publish_assignment(
    assignment_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Publish assignment to students"""
    assignment = db.query(Assignment).join(Course).filter(
        Assignment.id == assignment_id,
        Course.teacher_id == current_teacher.id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    assignment.is_active = True
    db.commit()
    
    return {"message": "Assignment published", "is_active": True}


@router.post("/assignments/{assignment_id}/unpublish")
def unpublish_assignment(
    assignment_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Unpublish assignment from students"""
    assignment = db.query(Assignment).join(Course).filter(
        Assignment.id == assignment_id,
        Course.teacher_id == current_teacher.id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    assignment.is_active = False
    db.commit()
    
    return {"message": "Assignment unpublished", "is_active": False}


@router.get("/assignments/{assignment_id}")
def get_assignment_details(
    assignment_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get assignment details for review"""
    assignment = db.query(Assignment).join(Course).filter(
        Assignment.id == assignment_id,
        Course.teacher_id == current_teacher.id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    submissions = db.query(Submission).filter(Submission.assignment_id == assignment_id).all()
    
    return {
        "id": assignment.id,
        "title": assignment.title,
        "description": assignment.description,
        "course_id": assignment.course_id,
        "max_score": assignment.max_score,
        "due_date": assignment.due_date,
        "is_active": assignment.is_active,
        "created_at": assignment.created_at,
        "submission_count": len(submissions)
    }


@router.get("/assignments/{assignment_id}/submissions")
def list_assignment_submissions(
    assignment_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    List all submissions for an assignment
    """
    # Verify assignment ownership
    assignment = db.query(Assignment).join(Course).filter(
        Assignment.id == assignment_id,
        Course.teacher_id == current_teacher.id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found or you don't have access"
        )
    
    submissions = db.query(Submission).filter(Submission.assignment_id == assignment_id).all()
    
    results = []
    for sub in submissions:
        results.append({
            "id": sub.id,
            "student_id": sub.student_id,
            "student_username": sub.student.username,
            "content": sub.content,
            "score": sub.score,
            "ai_feedback": sub.ai_feedback,
            "teacher_feedback": sub.teacher_feedback,
            "submitted_at": sub.submitted_at,
            "graded_at": sub.graded_at
        })
    
    return results


@router.put("/submissions/{submission_id}/grade")
def grade_submission(
    submission_id: int,
    score: float,
    feedback: Optional[str] = None,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    Grade a student submission
    """
    # Verify submission ownership
    submission = db.query(Submission).join(Assignment).join(Course).filter(
        Submission.id == submission_id,
        Course.teacher_id == current_teacher.id
    ).first()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found or you don't have access"
        )
    
    submission.score = score
    submission.teacher_feedback = feedback
    submission.graded_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": "Submission graded successfully",
        "score": score
    }


# ============================================
# ANALYTICS & PERFORMANCE
# ============================================

@router.get("/courses/{course_id}/analytics")
def get_course_analytics(
    course_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive analytics for a course
    
    Returns:
    - Total students enrolled
    - Quiz statistics
    - Assignment statistics  
    - Student performance overview
    """
    # Verify course ownership
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.teacher_id == current_teacher.id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or you don't have access"
        )
    
    # Total students
    total_students = db.query(Enrollment).filter(Enrollment.course_id == course_id).count()
    
    # Quiz stats
    quizzes = db.query(Quiz).filter(Quiz.course_id == course_id).all()
    quiz_attempts = db.query(QuizAttempt).join(Quiz).filter(Quiz.course_id == course_id).all()
    
    avg_quiz_score = 0
    if quiz_attempts:
        total_score = sum(attempt.score for attempt in quiz_attempts if attempt.score)
        avg_quiz_score = total_score / len(quiz_attempts) if quiz_attempts else 0
    
    # Assignment stats
    assignments = db.query(Assignment).filter(Assignment.course_id == course_id).all()
    submissions = db.query(Submission).join(Assignment).filter(Assignment.course_id == course_id).all()
    
    graded_submissions = [s for s in submissions if s.score is not None]
    avg_assignment_score = 0
    if graded_submissions:
        total_score = sum(s.score for s in graded_submissions)
        avg_assignment_score = total_score / len(graded_submissions)
    
    # Student performance breakdown
    student_performance = []
    enrollments = db.query(Enrollment).filter(Enrollment.course_id == course_id).all()
    
    for enrollment in enrollments:
        student = enrollment.student
        
        # Get student's quiz attempts for this course
        student_quizzes = db.query(QuizAttempt).join(Quiz).filter(
            Quiz.course_id == course_id,
            QuizAttempt.student_id == student.id
        ).all()
        
        # Get student's submissions for this course
        student_submissions = db.query(Submission).join(Assignment).filter(
            Assignment.course_id == course_id,
            Submission.student_id == student.id
        ).all()
        
        quiz_avg = 0
        if student_quizzes:
            scores = [q.score for q in student_quizzes if q.score]
            quiz_avg = sum(scores) / len(scores) if scores else 0
        
        assignment_avg = 0
        graded = [s for s in student_submissions if s.score is not None]
        if graded:
            assignment_avg = sum(s.score for s in graded) / len(graded)
        
        student_performance.append({
            "student_id": student.id,
            "username": student.username,
            "quiz_average": round(quiz_avg, 2),
            "assignment_average": round(assignment_avg, 2),
            "overall_average": round((quiz_avg + assignment_avg) / 2, 2) if (quiz_avg or assignment_avg) else 0,
            "quizzes_attempted": len(student_quizzes),
            "assignments_submitted": len(student_submissions)
        })
    
    # Sort by overall average (descending)
    student_performance.sort(key=lambda x: x["overall_average"], reverse=True)
    
    return {
        "course_id": course_id,
        "course_name": course.name,
        "total_students": total_students,
        "total_quizzes": len(quizzes),
        "total_assignments": len(assignments),
        "quiz_statistics": {
            "total_attempts": len(quiz_attempts),
            "average_score": round(avg_quiz_score, 2)
        },
        "assignment_statistics": {
            "total_submissions": len(submissions),
            "graded_submissions": len(graded_submissions),
            "average_score": round(avg_assignment_score, 2)
        },
        "student_performance": student_performance
    }


# ============================================
# AI-POWERED FEATURES
# ============================================

@router.post("/chatbots/{chatbot_id}/process-documents")
def process_chatbot_documents(
    chatbot_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    Process all uploaded documents for a chatbot
    
    Chunks, embeds, and stores in ChromaDB for RAG
    """
    from ai_services import get_rag_system
    
    # Verify chatbot ownership
    chatbot = db.query(Chatbot).filter(
        Chatbot.id == chatbot_id,
        Chatbot.teacher_id == current_teacher.id
    ).first()
    
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbot not found or you don't have access"
        )
    
    # Get all documents for this chatbot
    documents = db.query(ChatbotDocument).filter(
        ChatbotDocument.chatbot_id == chatbot_id
    ).all()
    
    if not documents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No documents uploaded for this chatbot"
        )
    
    rag_system = get_rag_system()
    processed_count = 0
    total_chunks = 0
    
    for doc in documents:
        try:
            # Process and store document
            chunks = rag_system.process_and_store_document(
                doc.file_path,
                chatbot.collection_name
            )
            
            # Update document record
            doc.chunk_count = chunks
            total_chunks += chunks
            processed_count += 1
            
        except Exception as e:
            print(f"Error processing {doc.filename}: {e}")
            continue
    
    db.commit()
    
    return {
        "message": "Documents processed successfully",
        "documents_processed": processed_count,
        "total_documents": len(documents),
        "total_chunks_created": total_chunks,
        "chatbot_ready": processed_count > 0
    }

@router.post("/chatbots/{chatbot_id}/test")
def test_chatbot(
    chatbot_id: int,
    question: str,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    Test the chatbot response ( Teacher view)
    """
    from ai_services import get_rag_system
    
    chatbot = db.query(Chatbot).join(Course).filter(
        Chatbot.id == chatbot_id,
        Course.teacher_id == current_teacher.id
    ).first()
    
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
        
    # Save teacher's question (using Teacher's ID)
    user_message = ChatMessage(
        chatbot_id=chatbot_id,
        user_id=current_teacher.id,
        role="user",
        content=question
    )
    db.add(user_message)
    db.commit()
    
    # Get RAG response
    rag_system = get_rag_system()
    result = rag_system.query(
        collection_name=chatbot.collection_name,
        question=question,
        system_prompt=chatbot.system_prompt,
        llm_provider=chatbot.llm_provider or "gemini",
        llm_model=chatbot.llm_model
    )
    
    # Save assistant response
    ai_message = ChatMessage(
        chatbot_id=chatbot_id,
        user_id=current_teacher.id,
        role="assistant",
        content=result["answer"]
    )
    db.add(ai_message)
    db.commit()
    
    return {
        "answer": result["answer"],
        "sources": result.get("sources", []),
        "context_used": result["context_used"]
    }


@router.get("/chatbots/{chatbot_id}/test-history")
def get_test_chat_history(
    chatbot_id: int,
    limit: int = 20,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    Get chat history for the teacher (testing mode)
    """
    chatbot = db.query(Chatbot).join(Course).filter(
        Chatbot.id == chatbot_id,
        Course.teacher_id == current_teacher.id
    ).first()
    
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
        
    messages = db.query(ChatMessage).filter(
        ChatMessage.chatbot_id == chatbot_id,
        ChatMessage.user_id == current_teacher.id
    ).order_by(ChatMessage.created_at.desc()).limit(limit).all()
    
    return [
        {
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at
        }
        for msg in reversed(messages)
    ]
@router.post("/quizzes/generate")
def generate_quiz_with_ai(
    course_id: int,
    topic: str,
    num_questions: int = 5,
    difficulty: str = "medium",
    llm_provider: str = "gemini",
    llm_model: Optional[str] = None,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    Generate quiz questions using AI
    
    Args:
        course_id: Course to create quiz for
        topic: Topic/subject for questions
        num_questions: Number of questions
        difficulty: easy, medium, or hard
        llm_provider: 'gemini' or 'mistral'
        llm_model: Specific model name (optional)
    """
    from ai_services import get_quiz_generator
    
    # Verify course ownership
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.teacher_id == current_teacher.id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or you don't have access"
        )
    
    quiz_gen = get_quiz_generator(llm_provider, llm_model)
    
    # Generate questions
    questions = quiz_gen.generate_quiz_questions(
        topic=topic,
        num_questions=num_questions,
        difficulty=difficulty
    )
    
    if questions and "error" in questions[0]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=questions[0].get("message", "Failed to generate questions")
        )
    
    # Create quiz
    new_quiz = Quiz(
        title=f"{topic} Quiz (AI-Generated)",
        description=f"Auto-generated {difficulty} quiz about {topic}",
        course_id=course_id,
        time_limit_minutes=num_questions * 2,  # 2 mins per question
        max_attempts=2,
        is_active=True
    )
    
    db.add(new_quiz)
    db.commit()
    db.refresh(new_quiz)
    
    # Add generated questions
    for q in questions:
        question = QuizQuestion(
            quiz_id=new_quiz.id,
            question_text=q.get("question_text"),
            question_type=q.get("question_type"),
            options=json.dumps(q.get("options")) if q.get("options") else None,
            correct_answer=q.get("correct_answer"),
            points=q.get("points", 1.0),
            explanation=q.get("explanation")
        )
        db.add(question)
    
    db.commit()
    db.refresh(new_quiz)
    
    return {
        "message": "Quiz generated successfully",
        "quiz_id": new_quiz.id,
        "quiz_title": new_quiz.title,
        "questions_generated": len(questions),
        "llm_provider": llm_provider,
        "llm_model": llm_model
    }


@router.post("/quizzes/generate-from-rag")
def generate_quiz_from_rag(
    course_id: int,
    chatbot_id: int,
    topic: Optional[str] = None,
    num_questions: int = 5,
    difficulty: str = "medium",
    llm_provider: str = "gemini",
    llm_model: Optional[str] = None,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    Generate quiz questions from chatbot's RAG knowledge base
    
    Questions are generated ONLY from uploaded course documents.
    This ensures quiz content aligns with the actual course materials.
    
    Args:
        course_id: Course to create quiz for
        chatbot_id: Chatbot whose documents to use for content
        topic: Optional topic to focus questions on
        num_questions: Number of questions to generate
        difficulty: easy, medium, or hard
        llm_provider: 'gemini' or 'mistral'
        llm_model: Specific model name (optional)
    """
    from ai_services import get_quiz_generator
    
    # Verify course ownership
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.teacher_id == current_teacher.id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or you don't have access"
        )
    
    # Verify chatbot ownership
    chatbot = db.query(Chatbot).filter(
        Chatbot.id == chatbot_id,
        Chatbot.teacher_id == current_teacher.id
    ).first()
    
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbot not found or you don't have access"
        )
    
    quiz_gen = get_quiz_generator(llm_provider, llm_model)
    
    # Generate questions from RAG
    result = quiz_gen.generate_from_rag(
        collection_name=chatbot.collection_name,
        topic=topic,
        num_questions=num_questions,
        difficulty=difficulty
    )
    
    if result.get("error"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Failed to generate questions from course materials")
        )
    
    questions = result.get("questions", [])
    
    if not questions or (questions and "error" in questions[0]):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate valid questions from course materials"
        )
    
    # Create quiz
    quiz_title = f"{topic or 'Course Content'} Quiz (RAG-Generated)"
    new_quiz = Quiz(
        title=quiz_title,
        description=f"AI-generated from course materials: {difficulty} difficulty",
        course_id=course_id,
        time_limit_minutes=num_questions * 2,
        max_attempts=2,
        is_active=False  # Draft by default - teacher must forward
    )
    
    db.add(new_quiz)
    db.commit()
    db.refresh(new_quiz)
    
    # Add generated questions
    for q in questions:
        question = QuizQuestion(
            quiz_id=new_quiz.id,
            question_text=q.get("question_text"),
            question_type=q.get("question_type"),
            options=json.dumps(q.get("options")) if q.get("options") else None,
            correct_answer=q.get("correct_answer"),
            points=q.get("points", 1.0),
            explanation=q.get("explanation")
        )
        db.add(question)
    
    db.commit()
    db.refresh(new_quiz)
    
    return {
        "message": "Quiz generated from course materials",
        "quiz_id": new_quiz.id,
        "quiz_title": new_quiz.title,
        "questions_generated": len(questions),
        "source": "rag",
        "chatbot_used": chatbot.name,
        "chunks_used": result.get("chunks_used", 0),
        "llm_provider": llm_provider
    }


@router.post("/assignments/generate-from-rag")
def generate_assignment_from_rag(
    course_id: int,
    chatbot_id: int,
    topic: Optional[str] = None,
    max_score: int = 100,
    num_questions: int = 5,
    llm_provider: str = "gemini",
    llm_model: str = None,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Generate assignment from RAG knowledge base"""
    from ai_services import get_quiz_generator
    
    # Verify course
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.teacher_id == current_teacher.id
    ).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Verify chatbot
    chatbot = db.query(Chatbot).filter(
        Chatbot.id == chatbot_id,
        Chatbot.teacher_id == current_teacher.id
    ).first()
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    
    try:
        # Initialize generator with selected provider
        # Note: We use a default model if not specified, usually defined in the provider class
        generator = get_quiz_generator(llm_provider=llm_provider, llm_model=llm_model)
        
        result = generator.generate_from_rag(
            collection_name=chatbot.collection_name,
            topic=topic or "general course content",
            num_questions=num_questions,  # Use user-requested number of questions
            difficulty="medium"
        )
        
        # Check for errors in result
        if result.get("error"):
            raise HTTPException(status_code=400, detail=result.get("message"))
            
        questions = result.get("questions", [])
        
        # Check for error in questions list
        if questions and "error" in questions[0]:
             raise HTTPException(status_code=500, detail=questions[0].get("message", "Failed to generate assignment"))
        
        # Format questions into the assignment description
        if questions:
            formatted_questions = "\n\n".join([f"{i+1}. {q.get('question_text')}" for i, q in enumerate(questions)])
            description = f"Please complete the following questions based on the course materials:\n\n{formatted_questions}"
        else:
            description = "Complete the assignment based on course materials."
        
        # Create assignment
        new_assignment = Assignment(
            title=f"{topic or 'Course'} Assignment (RAG)",
            description=f"Based on course materials:\n\n{description}",
            course_id=course_id,
            max_score=max_score,
            due_date=None,
            is_active=False
        )
        
        db.add(new_assignment)
        db.commit()
        db.refresh(new_assignment)
        
        return {
            "message": "Assignment created from course materials",
            "assignment_id": new_assignment.id,
            "assignment_title": new_assignment.title,
            "chatbot_used": chatbot.name,
            "chunks_used": result.get("chunks_used", 0)
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating assignment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Error: {str(e)}")


@router.get("/ai/llm-providers")
def list_llm_providers(
    current_teacher: User = Depends(get_current_teacher)
):
    """
    List available LLM providers and their models
    
    Returns which providers are configured and available for use.
    """
    from ai_services import get_available_providers, get_all_models
    
    providers = get_available_providers()
    models = get_all_models()
    
    return {
        "providers": providers,
        "models": models,
        "default": "gemini"
    }


@router.post("/ai/predict-difficulty")
def predict_quiz_difficulty(
    student_id: int,
    course_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    Predict optimal quiz difficulty for a student using ML
    
    Uses student's performance history to recommend difficulty level
    that maximizes learning while maintaining engagement.
    """
    from ai_services import get_difficulty_selector
    
    # Verify course ownership
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.teacher_id == current_teacher.id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or you don't have access"
        )
    
    # Get student's quiz history
    quiz_attempts = db.query(QuizAttempt).join(Quiz).filter(
        Quiz.course_id == course_id,
        QuizAttempt.student_id == student_id
    ).order_by(QuizAttempt.started_at.desc()).all()
    
    # Get assignment scores
    submissions = db.query(Submission).join(Assignment).filter(
        Assignment.course_id == course_id,
        Submission.student_id == student_id,
        Submission.score.isnot(None)
    ).all()
    
    # Prepare history for ML model
    quiz_scores = [attempt.score for attempt in quiz_attempts if attempt.score]
    assignment_avg = sum(s.score for s in submissions) / len(submissions) if submissions else 50.0
    
    student_history = {
        'recent_quiz_scores': quiz_scores[:10] if quiz_scores else [],
        'all_quiz_scores': quiz_scores,
        'assignment_average': assignment_avg,
        'days_since_last_quiz': 0 if quiz_attempts else 7
    }
    
    # Get prediction
    selector = get_difficulty_selector()
    prediction = selector.predict_optimal_difficulty(student_history)
    
    return {
        "student_id": student_id,
        "course_id": course_id,
        "recommended_difficulty": prediction["difficulty"],
        "confidence": prediction["confidence"],
        "method": prediction["method"],
        "reasoning": prediction["reasoning"],
        "student_stats": {
            "quiz_count": len(quiz_scores),
            "recent_average": round(sum(quiz_scores[-5:]) / len(quiz_scores[-5:]), 1) if quiz_scores else 0,
            "assignment_average": round(assignment_avg, 1)
        }
    }


@router.post("/ai/evaluate-answer")
def evaluate_answer_with_ml(
    question: str,
    student_answer: str,
    correct_answer: str,
    max_points: float = 1.0,
    use_llm_feedback: bool = True,
    llm_provider: str = "gemini",
    current_teacher: User = Depends(get_current_teacher)
):
    """
    Evaluate a student's answer using ML scoring
    
    Uses hybrid ML approach combining:
    - TF-IDF similarity (lexical matching)
    - Semantic similarity (meaning understanding)
    - Keyword matching (concept coverage)
    - Optional LLM feedback for detailed explanation
    """
    from ai_services import get_answer_evaluator
    
    evaluator = get_answer_evaluator(
        llm_provider=llm_provider,
        use_ml_scoring=True
    )
    
    result = evaluator.evaluate_short_answer(
        question=question,
        student_answer=student_answer,
        correct_answer=correct_answer,
        max_points=max_points,
        use_llm_feedback=use_llm_feedback
    )
    
    return result


@router.get("/ai/ml-scoring-demo")
def ml_scoring_demo(
    student_answer: str = "Photosynthesis is the process by which plants convert sunlight into energy",
    correct_answer: str = "Photosynthesis is the process where plants use sunlight, water, and carbon dioxide to produce glucose and oxygen",
    current_teacher: User = Depends(get_current_teacher)
):
    """
    Demo endpoint to test ML-based answer scoring
    
    Shows how the hybrid scorer evaluates answers using:
    - TF-IDF similarity
    - Semantic embeddings
    - Keyword matching
    """
    from ai_services import get_hybrid_scorer
    
    scorer = get_hybrid_scorer()
    
    result = scorer.score_answer(
        student_answer=student_answer,
        correct_answer=correct_answer,
        question="What is photosynthesis?",
        max_points=10.0
    )
    
    return {
        "student_answer": student_answer,
        "correct_answer": correct_answer,
        "evaluation": result
    }