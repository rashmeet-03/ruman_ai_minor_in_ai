"""
Student routes for quiz taking, chatbot interaction, assignments, and gamification
"""

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, date, timedelta
import json
import os
import shutil
from ai_services import get_rag_system

from database import get_db
from models import (
    User, Course, Enrollment, Chatbot, ChatbotCourse, ChatMessage,
    Quiz, QuizQuestion, QuizAttempt, Assignment, Submission,
    StudentProgress, Achievement, ActivityLog
)
from schemas import (
    CourseResponse,
    QuizAttemptCreate, QuizAttemptSubmit, QuizAttemptResponse,
    SubmissionCreate, SubmissionResponse,
    StudentProgressResponse, AchievementResponse
)
from routes.auth import get_current_student
from config import settings

router = APIRouter()


# ============================================
# STUDENT DASHBOARD
# ============================================

@router.get("/dashboard")
def get_student_dashboard(
    current_student: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Get student dashboard with overview, progress, and recent activity
    """
    # Get student progress
    progress = db.query(StudentProgress).filter(
        StudentProgress.student_id == current_student.id
    ).first()
    
    if not progress:
        # Create progress if doesn't exist
        progress = StudentProgress(
            student_id=current_student.id,
            xp_points=0,
            level=1,
            streak_days=0,
            last_activity_date=date.today()
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)
    
    
    # Get enrolled courses
    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == current_student.id
    ).all()
    
    courses = []
    for enrollment in enrollments:
        course = enrollment.course
        
        # Count quizzes and assignments for this course
        quiz_count = db.query(Quiz).filter(Quiz.course_id == course.id, Quiz.is_active == True).count()
        assignment_count = db.query(Assignment).filter(Assignment.course_id == course.id, Assignment.is_active == True).count()
        
        # Get chatbots assigned to this course
        chatbots = db.query(Chatbot).join(ChatbotCourse).filter(
            ChatbotCourse.course_id == course.id,
            Chatbot.is_active == True
        ).all()
        
        courses.append({
            "id": course.id,
            "name": course.name,
            "description": course.description,
            "teacher": course.teacher.username,
            "enrolled_at": enrollment.enrolled_at,
            "quiz_count": quiz_count,
            "assignment_count": assignment_count,
            "chatbots": [{"id": bot.id, "name": bot.name, "description": bot.description, "provider": bot.llm_provider, "model": bot.llm_model} for bot in chatbots]
        })
    
    # Get recent quiz attempts
    recent_attempts = db.query(QuizAttempt).filter(
        QuizAttempt.student_id == current_student.id
    ).order_by(QuizAttempt.started_at.desc()).limit(5).all()
    
    # Get achievements earned
    earned_achievements = []
    if progress.badges_list:
        achievements = db.query(Achievement).filter(
            Achievement.id.in_(progress.badges_list)
        ).all()
        earned_achievements = [
            {
                "id": ach.id,
                "name": ach.name,
                "description": ach.description,
                "badge_icon": ach.badge_icon,
                "xp_reward": ach.xp_reward
            }
            for ach in achievements
        ]
    
    return {
        "student": {
            "id": current_student.id,
            "username": current_student.username,
            "email": current_student.email
        },
        "progress": {
            "xp_points": progress.xp_points,
            "level": progress.level,
            "streak_days": progress.streak_days,
            "badges_count": len(progress.badges_list) if progress.badges_list else 0
        },
        "courses": courses,
        "recent_attempts": [
            {
                "quiz_id": attempt.quiz_id,
                "quiz_title": attempt.quiz.title,
                "score": attempt.score,
                "max_score": attempt.max_score,
                "started_at": attempt.started_at,
                "completed_at": attempt.completed_at
            }
            for attempt in recent_attempts
        ],
        "achievements": earned_achievements
    }


# ============================================
# COURSE ENROLLMENT
# ============================================

@router.get("/courses", response_model=List[CourseResponse])
def list_enrolled_courses(
    current_student: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    List all courses the student is enrolled in
    """
    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == current_student.id
    ).all()
    
    courses = [enrollment.course for enrollment in enrollments]
    return courses


@router.post("/courses/{course_id}/enroll")
def enroll_in_course(
    course_id: int,
    current_student: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Self-enroll in a course (if allowed)
    """
    # Check if course exists
    course = db.query(Course).filter(Course.id == course_id, Course.is_active == True).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Check if already enrolled
    existing = db.query(Enrollment).filter(
        Enrollment.course_id == course_id,
        Enrollment.student_id == current_student.id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already enrolled in this course"
        )
    
    # Create enrollment
    enrollment = Enrollment(
        course_id=course_id,
        student_id=current_student.id
    )
    
    db.add(enrollment)
    db.commit()
    
    # Award XP for enrollment
    _award_xp(current_student.id, 10, "Enrolled in course", db)
    
    return {
        "message": f"Successfully enrolled in {course.name}",
        "xp_earned": 10
    }


# ============================================
# QUIZ TAKING
# ============================================

@router.get("/courses/{course_id}/quizzes")
def list_course_quizzes(
    course_id: int,
    current_student: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    List all quizzes for an enrolled course
    """
    # Verify enrollment
    enrollment = db.query(Enrollment).filter(
        Enrollment.course_id == course_id,
        Enrollment.student_id == current_student.id
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enrolled in this course"
        )
    
    quizzes = db.query(Quiz).filter(
        Quiz.course_id == course_id,
        Quiz.is_active == True
    ).all()
    
    quiz_list = []
    for quiz in quizzes:
        # Get all attempts
        attempts = db.query(QuizAttempt).filter(
            QuizAttempt.quiz_id == quiz.id,
            QuizAttempt.student_id == current_student.id
        ).all()
        
        attempts_count = len(attempts)
        
        # Check for active (incomplete) attempt
        active_attempt = next((a for a in attempts if a.completed_at is None), None)
        
        # Get best score
        completed_attempts = [a for a in attempts if a.score is not None]
        best_score = max([a.score for a in completed_attempts]) if completed_attempts else None
        
        quiz_list.append({
            "id": quiz.id,
            "title": quiz.title,
            "description": quiz.description,
            "time_limit_minutes": quiz.time_limit_minutes,
            "max_attempts": quiz.max_attempts,
            "attempts_taken": attempts_count,
            "attempts_remaining": max(0, quiz.max_attempts - attempts_count),
            "best_score": best_score,
            "can_attempt": attempts_count < quiz.max_attempts or active_attempt is not None,
            "active_attempt_id": active_attempt.id if active_attempt else None
        })
    
    return quiz_list


@router.post("/quizzes/{quiz_id}/attempt", status_code=status.HTTP_201_CREATED)
def start_quiz_attempt(
    quiz_id: int,
    current_student: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Start a new quiz attempt or resume existing incomplete one
    
    Returns quiz questions (without correct answers)
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.is_active == True).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    # Verify enrollment
    enrollment = db.query(Enrollment).filter(
        Enrollment.course_id == quiz.course_id,
        Enrollment.student_id == current_student.id
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enrolled in this course"
        )
    
    # Check for existing incomplete attempt
    existing_attempt = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.student_id == current_student.id,
        QuizAttempt.completed_at == None
    ).first()
    
    if existing_attempt:
        attempt = existing_attempt
        # (Resume logic continues below...)
    else:
        # Check attempts limit for NEW attempts
        attempts_count = db.query(QuizAttempt).filter(
            QuizAttempt.quiz_id == quiz_id,
            QuizAttempt.student_id == current_student.id
        ).count()
        
        if attempts_count >= quiz.max_attempts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum attempts ({quiz.max_attempts}) reached"
            )
        
        # Create new attempt
        attempt = QuizAttempt(
            quiz_id=quiz_id,
            student_id=current_student.id,
            started_at=datetime.utcnow()
        )
        
        db.add(attempt)
        db.commit()
        db.refresh(attempt)
    
    # Get questions (without correct answers)
    questions = db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz_id).all()
    
    questions_data = []
    for q in questions:
        questions_data.append({
            "id": q.id,
            "question_text": q.question_text,
            "question_type": q.question_type,
            "options": q.options_list,
            "points": q.points
        })
    
    return {
        "attempt_id": attempt.id,
        "quiz_id": quiz.id,
        "quiz_title": quiz.title,
        "time_limit_minutes": quiz.time_limit_minutes,
        "started_at": attempt.started_at,
        "questions": questions_data,
        "is_resumed": existing_attempt is not None
    }


@router.post("/quiz-attempts/{attempt_id}/submit")
def submit_quiz_attempt(
    attempt_id: int,
    answers: dict,  # {question_id: answer}
    current_student: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Submit quiz attempt with answers
    
    Auto-grades and awards XP
    """
    from ai_services import get_answer_evaluator
    
    attempt = db.query(QuizAttempt).filter(
        QuizAttempt.id == attempt_id,
        QuizAttempt.student_id == current_student.id
    ).first()
    
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attempt not found"
        )
    
    if attempt.completed_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Attempt already submitted"
        )
    
    # Get questions
    questions = db.query(QuizQuestion).filter(QuizQuestion.quiz_id == attempt.quiz_id).all()
    
    evaluator = get_answer_evaluator()
    total_score = 0
    max_score = 0
    results = []
    
    for question in questions:
        max_score += question.points
        student_answer = answers.get(str(question.id), "")
        
        # Evaluate based on question type
        if question.question_type in ["mcq", "true_false"]:
            eval_result = evaluator.evaluate_mcq(student_answer, question.correct_answer)
            score = eval_result["score"] * question.points
            feedback = eval_result["feedback"]
        else:
            # Short answer - use AI evaluation
            eval_result = evaluator.evaluate_short_answer(
                question.question_text,
                student_answer,
                question.correct_answer,
                question.points
            )
            score = eval_result.get("score", 0)
            feedback = eval_result.get("feedback", "Unable to auto-grade")
        
        total_score += score
        
        results.append({
            "question_id": question.id,
            "question_text": question.question_text,
            "student_answer": student_answer,
            "correct_answer": question.correct_answer,
            "points_earned": score,
            "points_possible": question.points,
            "feedback": feedback,
            "explanation": question.explanation
        })
    
    # Update attempt
    attempt.score = total_score
    attempt.max_score = max_score
    attempt.answers = json.dumps(answers)
    attempt.completed_at = datetime.utcnow()
    
    db.commit()
    
    # Award XP based on score
    percentage = (total_score / max_score * 100) if max_score > 0 else 0
    xp_earned = int(percentage / 10) * 5  # 5 XP per 10% score
    
    if percentage >= 100:
        xp_earned += 20  # Bonus for perfect score
        _check_and_award_achievement(current_student.id, "quiz_score", 100, db)
    
    _award_xp(current_student.id, xp_earned, f"Completed quiz: {attempt.quiz.title}", db)
    _check_and_award_achievement(current_student.id, "quiz_complete", 1, db)
    
    return {
        "attempt_id": attempt.id,
        "score": total_score,
        "max_score": max_score,
        "percentage": round(percentage, 2),
        "xp_earned": xp_earned,
        "results": results
    }


# ============================================
# CHATBOT INTERACTION
# ============================================

@router.get("/courses/{course_id}/chatbots")
def list_course_chatbots(
    course_id: int,
    current_student: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    List available chatbots for an enrolled course
    """
    # Verify enrollment
    enrollment = db.query(Enrollment).filter(
        Enrollment.course_id == course_id,
        Enrollment.student_id == current_student.id
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enrolled in this course"
        )
    
    chatbots = db.query(Chatbot).join(ChatbotCourse).filter(
        ChatbotCourse.course_id == course_id,
        Chatbot.is_active == True
    ).all()
    
    return [
        {
            "id": bot.id,
            "name": bot.name,
            "description": bot.description,
            "provider": bot.llm_provider,
            "model": bot.llm_model
        }
        for bot in chatbots
    ]


@router.post("/chatbots/{chatbot_id}/query")
def query_chatbot(
    chatbot_id: int,
    question: str,
    current_student: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Ask a question to the chatbot
    
    """
    
    chatbot = db.query(Chatbot).filter(
        Chatbot.id == chatbot_id,
        Chatbot.is_active == True
    ).first()
    
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbot not found"
        )
    
    # Verify enrollment
    # Verify enrollment in ANY course this chatbot is assigned to
    enrollment = db.query(Enrollment).join(ChatbotCourse, Enrollment.course_id == ChatbotCourse.course_id).filter(
        ChatbotCourse.chatbot_id == chatbot_id,
        Enrollment.student_id == current_student.id
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enrolled in this course"
        )
    
    # Save student's question
    student_message = ChatMessage(
        chatbot_id=chatbot_id,
        user_id=current_student.id,
        role="user",
        content=question
    )
    db.add(student_message)
    db.commit()
    
    # Get RAG response using chatbot's configured LLM
    rag_system = get_rag_system()
    result = rag_system.query(
        collection_name=chatbot.collection_name,
        question=question,
        system_prompt=chatbot.system_prompt,
        llm_provider=chatbot.llm_provider or "gemini",
        llm_model=chatbot.llm_model
    )
    
    # Save assistant's response
    assistant_message = ChatMessage(
        chatbot_id=chatbot_id,
        user_id=current_student.id,
        role="assistant",
        content=result["answer"]
    )
    db.add(assistant_message)
    db.commit()
    
    # Award XP for engagement
    _award_xp(current_student.id, 2, "Asked chatbot question", db)
    
    return {
        "question": question,
        "answer": result["answer"],
        "context_used": result["context_used"],
        "sources": result.get("sources", []),
        "xp_earned": 2
    }


@router.get("/chatbots/{chatbot_id}/history")
def get_chat_history(
    chatbot_id: int,
    limit: int = 20,
    current_student: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Get chat history with this chatbot
    """
    # Verify access
    chatbot = db.query(Chatbot).filter(Chatbot.id == chatbot_id).first()
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    
    # Check if student is enrolled in ANY course this chatbot is assigned to
    enrollment = db.query(Enrollment).join(ChatbotCourse, Enrollment.course_id == ChatbotCourse.course_id).filter(
        ChatbotCourse.chatbot_id == chatbot_id,
        Enrollment.student_id == current_student.id
    ).first()
    
    if not enrollment:
        raise HTTPException(status_code=403, detail="Not enrolled")
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.chatbot_id == chatbot_id,
        ChatMessage.user_id == current_student.id
    ).order_by(ChatMessage.created_at.desc()).limit(limit).all()
    
    return [
        {
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at
        }
        for msg in reversed(messages)
    ]

@router.delete("/chatbots/{chatbot_id}/history")
def clear_chat_history(
    chatbot_id: int,
    current_student: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Clear chat history for this chatbot
    """
    # Simply delete all messages for this user and chatbot
    db.query(ChatMessage).filter(
        ChatMessage.chatbot_id == chatbot_id,
        ChatMessage.user_id == current_student.id
    ).delete()
    
    db.commit()
    
    return {"message": "Chat history cleared"}
# ============================================
# ASSIGNMENTS
# ============================================

@router.get("/courses/{course_id}/assignments")
def list_course_assignments(
    course_id: int,
    current_student: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    List assignments for a course
    """
    # Verify enrollment
    enrollment = db.query(Enrollment).filter(
        Enrollment.course_id == course_id,
        Enrollment.student_id == current_student.id
    ).first()
    
    if not enrollment:
        raise HTTPException(status_code=403, detail="Not enrolled")
    
    assignments = db.query(Assignment).filter(
        Assignment.course_id == course_id,
        Assignment.is_active == True
    ).all()
    
    assignment_list = []
    for assignment in assignments:
        # Check if student has submitted
        submission = db.query(Submission).filter(
            Submission.assignment_id == assignment.id,
            Submission.student_id == current_student.id
        ).first()
        
        assignment_list.append({
            "id": assignment.id,
            "title": assignment.title,
            "description": assignment.description,
            "max_score": assignment.max_score,
            "due_date": assignment.due_date,
            "submitted": submission is not None,
            "score": submission.score if submission else None,
            "feedback": submission.teacher_feedback if submission else None
        })
    
    return assignment_list


@router.post("/assignments/{assignment_id}/submit")
def submit_assignment(
    assignment_id: int,
    content: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_student: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Submit an assignment via text or file upload
    """
    from ai_services import get_answer_evaluator
    
    if not content and not file:
        raise HTTPException(status_code=400, detail="Either text content or file must be provided")

    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id,
        Assignment.is_active == True
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Verify enrollment
    enrollment = db.query(Enrollment).filter(
        Enrollment.course_id == assignment.course_id,
        Enrollment.student_id == current_student.id
    ).first()
    
    if not enrollment:
        raise HTTPException(status_code=403, detail="Not enrolled")
    
    # Check if already submitted
    existing = db.query(Submission).filter(
        Submission.assignment_id == assignment_id,
        Submission.student_id == current_student.id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already submitted")
    
    file_path = None
    extracted_text = ""
    
    # Handle file upload
    if file:
        upload_dir = f"uploads/submissions/{current_student.id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = f"{upload_dir}/{filename}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Try to read text content for AI grading if it's a text file
        if file.filename.endswith('.txt'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    extracted_text = f.read()
            except:
                pass
                
        # For PDFs we could add pdf reading logic here, for now we rely on explicit text content
        # or just mark it for manual grading
        if not content:
            content = f"File submitted: {file.filename}"

    # Use extracted text if content is empty, or combine them
    grading_content = extracted_text if extracted_text else content

    # AI evaluation (preliminary)
    ai_eval = {"score": None, "feedback": "Pending teacher review (File submitted)"}
    
    # Only run AI grading if we have sufficient text content
    if len(grading_content) > 20 and not (file and not extracted_text):
        evaluator = get_answer_evaluator()
        ai_eval = evaluator.evaluate_assignment(
            assignment.description,
            grading_content,
            assignment.max_score
        )
    
    # Create submission
    submission = Submission(
        assignment_id=assignment_id,
        student_id=current_student.id,
        content=content,
        file_path=file_path,
        score=ai_eval.get("score") if not ai_eval.get("error") else None,
        ai_feedback=ai_eval.get("feedback", ""),
        submitted_at=datetime.utcnow()
    )
    
    db.add(submission)
    db.commit()
    
    # Award XP
    _award_xp(current_student.id, 15, f"Submitted assignment: {assignment.title}", db)
    
    return {
        "message": "Assignment submitted successfully",
        "submission_id": submission.id,
        "ai_preliminary_score": ai_eval.get("score"),
        "ai_feedback": ai_eval.get("feedback"),
        "note": "Final grading by teacher",
        "xp_earned": 15
    }


# ============================================
# PROGRESS & GAMIFICATION
# ============================================

@router.get("/progress", response_model=StudentProgressResponse)
def get_student_progress(
    current_student: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Get student's gamification progress
    """
    progress = db.query(StudentProgress).filter(
        StudentProgress.student_id == current_student.id
    ).first()
    
    if not progress:
        progress = StudentProgress(
            student_id=current_student.id,
            xp_points=0,
            level=1,
            streak_days=0
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)
    
    return progress


@router.get("/achievements", response_model=List[AchievementResponse])
def list_achievements(
    current_student: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    List all available achievements and earned status
    """
    all_achievements = db.query(Achievement).all()
    
    progress = db.query(StudentProgress).filter(
        StudentProgress.student_id == current_student.id
    ).first()
    
    earned_ids = progress.badges_list if progress and progress.badges_list else []
    
    return [
        {
            "id": ach.id,
            "name": ach.name,
            "description": ach.description,
            "badge_icon": ach.badge_icon,
            "xp_reward": ach.xp_reward,
            "earned": ach.id in earned_ids
        }
        for ach in all_achievements
    ]


# ============================================
# HELPER FUNCTIONS
# ============================================

def _award_xp(student_id: int, xp: int, reason: str, db: Session):
    """Award XP to student and update level"""
    progress = db.query(StudentProgress).filter(
        StudentProgress.student_id == student_id
    ).first()
    
    if not progress:
        return
    
    progress.xp_points += xp
    
    # Calculate new level (100 XP per level)
    new_level = 1 + (progress.xp_points // 100)
    if new_level > progress.level:
        progress.level = new_level
        # Award bonus for leveling up
        progress.xp_points += 50
    
    # Update streak
    today = date.today()
    if progress.last_activity_date:
        days_diff = (today - progress.last_activity_date).days
        if days_diff == 1:
            progress.streak_days += 1
        elif days_diff > 1:
            progress.streak_days = 1
    else:
        progress.streak_days = 1
    
    progress.last_activity_date = today
    
    # Log activity
    # Log activity
    activity = ActivityLog(
        user_id=student_id,
        activity_type="xp_award",
        entity_type="system",
        action_metadata=json.dumps({"reason": reason, "xp_earned": xp})
    )
    db.add(activity)
    
    db.commit()


def _check_and_award_achievement(student_id: int, condition_type: str, value: float, db: Session):
    """Check and award achievements based on conditions"""
    progress = db.query(StudentProgress).filter(
        StudentProgress.student_id == student_id
    ).first()
    
    if not progress:
        return
    
    # Find matching achievements
    achievements = db.query(Achievement).filter(
        Achievement.condition_type == condition_type,
        Achievement.condition_value <= value
    ).all()
    
    earned_ids = progress.badges_list if progress.badges_list else []
    new_achievements = []
    
    for ach in achievements:
        if ach.id not in earned_ids:
            earned_ids.append(ach.id)
            progress.badges = json.dumps(earned_ids)
            progress.xp_points += ach.xp_reward
            new_achievements.append(ach.name)
    
    if new_achievements:
        db.commit()