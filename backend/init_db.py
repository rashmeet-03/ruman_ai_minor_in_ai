"""
Database Initialization Script
Run this to create all tables and seed initial data
"""

from database import init_db, reset_db, get_db_context
from models import User, Achievement, StudentProgress, Course, Enrollment
from auth_utils import get_password_hash
from datetime import datetime


def create_sample_data():
    """Create sample users, courses, and achievements"""
    print("Creating sample data...")
    
    with get_db_context() as db:
        # ============================================
        # USERS
        # ============================================
        
        # Admin user
        admin = User(
            username="admin",
            email="admin@ruman.ai",
            password_hash=get_password_hash("admin123"),
            role="admin",
            is_active=True
        )
        db.add(admin)
        
        # Teacher: Rajesh Kumar
        teacher1 = User(
            username="rajeshkumar",
            email="rajesh@ruman.ai",
            password_hash=get_password_hash("teacher123"),
            role="teacher",
            is_active=True
        )
        db.add(teacher1)
        
        # Teacher: Priya Sharma
        teacher2 = User(
            username="priyasharma",
            email="priya@ruman.ai",
            password_hash=get_password_hash("teacher123"),
            role="teacher",
            is_active=True
        )
        db.add(teacher2)
        
        # Students
        students = []
        student_names = [
            ("rahul", "rahul@student.ruman.ai"),
            ("sneha", "sneha@student.ruman.ai"),
            ("amit", "amit@student.ruman.ai"),
            ("pooja", "pooja@student.ruman.ai"),
            ("vikram", "vikram@student.ruman.ai"),
        ]
        
        for name, email in student_names:
            student = User(
                username=name,
                email=email,
                password_hash=get_password_hash("student123"),
                role="student",
                is_active=True
            )
            db.add(student)
            students.append(student)
        
        db.flush()  # Get IDs
        
        # ============================================
        # COURSES (for Teacher Rajesh)
        # ============================================
        
        courses = []
        course_data = [
            ("Mathematics - Class 10A", "Mathematics course for Class 10A"),
            ("Mathematics - Class 10B", "Mathematics course for Class 10B"),
            ("Mathematics - Class 11A", "Mathematics course for Class 11A"),
            ("Mathematics - Class 11B", "Mathematics course for Class 11B"),
            ("Mathematics - Class 12A", "Mathematics course for Class 12A"),
            ("Mathematics - Class 12B", "Mathematics course for Class 12B"),
        ]
        
        for name, desc in course_data:
            course = Course(
                name=name,
                description=desc,
                teacher_id=teacher1.id,
                is_active=True
            )
            db.add(course)
            courses.append(course)
        
        # Add Science course for Teacher Priya
        science_course = Course(
            name="Science - Class 10A",
            description="Science course for Class 10A",
            teacher_id=teacher2.id,
            is_active=True
        )
        db.add(science_course)
        
        db.flush()  # Get course IDs
        
        # ============================================
        # ENROLLMENTS
        # ============================================
        
        # Enroll students in courses
        for student in students:
            # Each student enrolled in Class 10A Math
            enrollment = Enrollment(
                course_id=courses[0].id,
                student_id=student.id
            )
            db.add(enrollment)
            
            # Also enroll in Science
            enrollment2 = Enrollment(
                course_id=science_course.id,
                student_id=student.id
            )
            db.add(enrollment2)
        
        # ============================================
        # STUDENT PROGRESS
        # ============================================
        
        for i, student in enumerate(students):
            progress = StudentProgress(
                student_id=student.id,
                xp_points=i * 100,  # Give some XP
                level=1 + (i // 2),
                streak_days=i,
                last_activity_date=datetime.utcnow().date()
            )
            db.add(progress)
        
        # ============================================
        # ACHIEVEMENTS
        # ============================================
        
        achievements = [
            Achievement(
                name="First Quiz",
                description="Complete your first quiz",
                badge_icon="[1]",
                xp_reward=50,
                condition_type="quiz_complete",
                condition_value=1
            ),
            Achievement(
                name="Perfect Score",
                description="Score 100% on a quiz",
                badge_icon="[*]",
                xp_reward=100,
                condition_type="quiz_score",
                condition_value=100
            ),
            Achievement(
                name="Streak Master",
                description="Maintain a 7-day streak",
                badge_icon="[~]",
                xp_reward=200,
                condition_type="streak",
                condition_value=7
            ),
            Achievement(
                name="Knowledge Seeker",
                description="Ask 50 questions to AI tutors",
                badge_icon="[?]",
                xp_reward=150,
                condition_type="chatbot_queries",
                condition_value=50
            ),
            Achievement(
                name="Course Champion",
                description="Complete your first course",
                badge_icon="[+]",
                xp_reward=500,
                condition_type="course_complete",
                condition_value=1
            )
        ]
        
        for achievement in achievements:
            db.add(achievement)
        
        print("Sample data created successfully!")
        print("\n" + "=" * 50)
        print("DEFAULT USERS:")
        print("=" * 50)
        print("\nADMIN:")
        print("   username: admin      password: admin123")
        print("\nTEACHERS:")
        print("   username: rajeshkumar  password: teacher123")
        print("   username: priyasharma  password: teacher123")
        print("\nSTUDENTS:")
        print("   username: rahul       password: student123")
        print("   username: sneha       password: student123")
        print("   username: amit        password: student123")
        print("   username: pooja       password: student123")
        print("   username: vikram      password: student123")
        print("=" * 50)


def main():
    print("=" * 60)
    print("Ruman AI Learning Platform - Database Initialization")
    print("=" * 60)
    print()
    
    choice = input("Options:\n1. Initialize fresh database\n2. Reset database (WARNING: deletes all data!)\n3. Just create sample data\n\nEnter choice (1-3): ")
    
    if choice == "1":
        init_db()
        create_sample_data()
    elif choice == "2":
        confirm = input("WARNING: This will DELETE ALL DATA! Type 'yes' to confirm: ")
        if confirm.lower() == "yes":
            reset_db()
            create_sample_data()
        else:
            print("Cancelled")
    elif choice == "3":
        create_sample_data()
    else:
        print("Invalid choice")
    
    print("\nDone!")


if __name__ == "__main__":
    main()
