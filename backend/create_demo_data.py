"""
Complete School Demo Database Creator for Ruman AI Platform
Realistic school structure: Classes (10A, 10B, 11A, etc.) with different subjects
"""

from database import get_db_context, init_db
from models import (
    User, Course, Enrollment, Quiz, QuizQuestion, Assignment, 
    Chatbot, StudentProgress, Achievement
)
from auth_utils import get_password_hash
from datetime import datetime, timedelta
import random

def create_school_demo_data():
    """Create comprehensive school demo data with classes and sections"""
    
    print("=" * 80)
    print("🏫 Creating Ruman AI Platform - Complete School Database")
    print("=" * 80)
    
    # Initialize database tables first
    print("\n🔧 Initializing database tables...")
    init_db()
    print("   ✅ Tables created successfully!")
    
    with get_db_context() as db:
        
        # ================================================================
        # STEP 1: Create Admin User
        # ================================================================
        print("\n📋 Step 1: Creating Admin User...")
        admin = User(
            username="admin",
            email="admin@ruman.ai",
            password_hash=get_password_hash("admin123"),
            role="admin",
            is_active=True
        )
        db.add(admin)
        print("   ✅ Admin: admin/admin123")
        
        # ================================================================
        # STEP 2: Create Teachers with Subjects
        # ================================================================
        print("\n👨‍🏫 Step 2: Creating Teachers...")
        teachers_data = [
            # Name, Email, Subject, Password
            ("Rajesh Kumar", "rajesh.kumar@ruman.ai", "Mathematics", "rajesh123"),
            ("Priya Sharma", "priya.sharma@ruman.ai", "Computer Science", "priya123"),
            ("Amit Patel", "amit.patel@ruman.ai", "English", "amit123"),
            ("Sneha Reddy", "sneha.reddy@ruman.ai", "Science", "sneha123"),
            ("Vikram Singh", "vikram.singh@ruman.ai", "Physics", "vikram123"),
            ("Meera Gupta", "meera.gupta@ruman.ai", "Chemistry", "meera123"),
            ("Arjun Verma", "arjun.verma@ruman.ai", "Biology", "arjun123"),
            ("Kavita Iyer", "kavita.iyer@ruman.ai", "History", "kavita123"),
            ("Sanjay Desai", "sanjay.desai@ruman.ai", "Geography", "sanjay123"),
            ("Pooja Nair", "pooja.nair@ruman.ai", "Hindi", "pooja123"),
        ]
        
        teachers = {}  # {subject: teacher_user_object}
        for name, email, subject, password in teachers_data:
            username = name.lower().replace(" ", "")
            teacher = User(
                username=username,
                email=email,
                password_hash=get_password_hash(password),
                role="teacher",
                is_active=True
            )
            db.add(teacher)
            teachers[subject] = teacher
            print(f"   ✅ {name} - {subject}")
            print(f"      Login: {username}/{password}")
        
        db.flush()  # Get teacher IDs
        
        # ================================================================
        # STEP 3: Create Students for Different Classes
        # ================================================================
        print("\n👨‍🎓 Step 3: Creating Students for Each Class...")
        
        # Students grouped by class
        students_by_class = {
            "10A": [
                ("Aarav Gupta", "aarav.gupta@student.ruman.ai"),
                ("Diya Verma", "diya.verma@student.ruman.ai"),
                ("Arjun Malhotra", "arjun.malhotra@student.ruman.ai"),
                ("Ananya Iyer", "ananya.iyer@student.ruman.ai"),
                ("Rohan Desai", "rohan.desai@student.ruman.ai"),
            ],
            "10B": [
                ("Ishaan Joshi", "ishaan.joshi@student.ruman.ai"),
                ("Kavya Nair", "kavya.nair@student.ruman.ai"),
                ("Aditya Kapoor", "aditya.kapoor@student.ruman.ai"),
                ("Saanvi Agarwal", "saanvi.agarwal@student.ruman.ai"),
                ("Vihaan Mehta", "vihaan.mehta@student.ruman.ai"),
            ],
            "11A": [
                ("Myra Choudhary", "myra.choudhary@student.ruman.ai"),
                ("Reyansh Pandey", "reyansh.pandey@student.ruman.ai"),
                ("Aadhya Bansal", "aadhya.bansal@student.ruman.ai"),
                ("Atharv Kulkarni", "atharv.kulkarni@student.ruman.ai"),
                ("Navya Pillai", "navya.pillai@student.ruman.ai"),
            ],
            "11B": [
                ("Vivaan Shah", "vivaan.shah@student.ruman.ai"),
                ("Kiara Sinha", "kiara.sinha@student.ruman.ai"),
                ("Ayaan Bose", "ayaan.bose@student.ruman.ai"),
                ("Ira Rao", "ira.rao@student.ruman.ai"),
                ("Dhruv Jain", "dhruv.jain@student.ruman.ai"),
            ],
            "12A": [
                ("Shanaya Khanna", "shanaya.khanna@student.ruman.ai"),
                ("Arnav Saxena", "arnav.saxena@student.ruman.ai"),
                ("Riya Mishra", "riya.mishra@student.ruman.ai"),
                ("Kabir Chawla", "kabir.chawla@student.ruman.ai"),
                ("Tara Bhatt", "tara.bhatt@student.ruman.ai"),
            ],
            "12B": [
                ("Yuvraj Singh", "yuvraj.singh@student.ruman.ai"),
                ("Anika Ghosh", "anika.ghosh@student.ruman.ai"),
                ("Shaurya Dubey", "shaurya.dubey@student.ruman.ai"),
                ("Zara Khan", "zara.khan@student.ruman.ai"),
                ("Neil Chatterjee", "neil.chatterjee@student.ruman.ai"),
            ],
        }
        
        students = {}  # {class: [students]}
        total_students = 0
        
        for class_name, students_list in students_by_class.items():
            print(f"\n   Class {class_name}:")
            class_students = []
            
            for name, email in students_list:
                username = name.lower().replace(" ", "")
                password = username + "123"
                student = User(
                    username=username,
                    email=email,
                    password_hash=get_password_hash(password),
                    role="student",
                    is_active=True
                )
                db.add(student)
                class_students.append(student)
                total_students += 1
                print(f"      ✅ {name} ({username}/{password})")
            
            students[class_name] = class_students
        
        db.flush()  # Get student IDs
        
        # Create student progress
        for class_students in students.values():
            for student in class_students:
                progress = StudentProgress(
                    student_id=student.id,
                    xp_points=random.randint(0, 500),
                    level=random.randint(1, 5),
                    streak_days=random.randint(0, 10),
                    last_activity_date=datetime.utcnow().date()
                )
                db.add(progress)
        
        print(f"\n   📊 Total Students: {total_students}")
        
        # ================================================================
        # STEP 4: Create Courses (Subject + Class) 
        # ================================================================
        print("\n📚 Step 4: Creating Courses (Subject for each Class)...")
        
        # Subjects by grade level
        grade_subjects = {
            10: ["Mathematics", "Science", "English", "Hindi", "Computer Science"],
            11: ["Mathematics", "Physics", "Chemistry", "English", "Computer Science"],
            12: ["Mathematics", "Physics", "Chemistry", "Biology", "English"],
        }
        
        courses = {}  # {(class, subject): course_object}
        course_count = 0
        
        for grade in [10, 11, 12]:
            for section in ['A', 'B']:
                class_name = f"{grade}{section}"
                print(f"\n   Class {class_name}:")
                
                for subject in grade_subjects[grade]:
                    teacher = teachers[subject]
                    course_name = f"{subject} - Class {class_name}"
                    
                    course = Course(
                        name=course_name,
                        description=f"{subject} course for Class {class_name}",
                        teacher_id=teacher.id,
                        is_active=True
                    )
                    db.add(course)
                    courses[(class_name, subject)] = course
                    course_count += 1
                    print(f"      ✅ {course_name} (Teacher: {teacher.username})")
        
        db.flush()  # Get course IDs
        print(f"\n   📊 Total Courses: {course_count}")
        
        # ================================================================
        # STEP 5: Enroll Students in Their Class Courses
        # ================================================================
        print("\n🎒 Step 5: Enrolling Students in Their Class Courses...")
        
        enrollment_count = 0
        for class_name, class_students in students.items():
            grade = int(class_name[:-1])  # Extract grade (10, 11, 12)
            subjects = grade_subjects[grade]
            
            print(f"   Class {class_name}: Enrolling {len(class_students)} students in {len(subjects)} subjects")
            
            for student in class_students:
                for subject in subjects:
                    course = courses[(class_name, subject)]
                    enrollment = Enrollment(
                        student_id=student.id,
                        course_id=course.id
                    )
                    db.add(enrollment)
                    enrollment_count += 1
        
        print(f"   ✅ Total Enrollments: {enrollment_count}")
        
        # ================================================================
        # STEP 6: Create AI Chatbots for Each Course
        # ================================================================
        print("\n🤖 Step 6: Creating AI Chatbots...")
        chatbot_count = 0
        for (class_name, subject), course in courses.items():
            chatbot = Chatbot(
                name=f"{subject} AI Tutor - {class_name}",
                description=f"AI assistant for {subject} in Class {class_name}",
                course_id=course.id,
                system_prompt=f"You are an expert {subject} tutor for Class {class_name} students. Explain concepts clearly and help with homework.",
                collection_name=f"course_{course.id}_docs",
                is_active=True
            )
            db.add(chatbot)
            chatbot_count += 1
        
        print(f"   ✅ Created {chatbot_count} AI Chatbots")
        
        # ================================================================
        # STEP 7: Create Sample Quizzes
        # ================================================================
        print("\n📝 Step 7: Creating Sample Quizzes...")
        
        quiz_templates = {
            "Mathematics": [
                ("Algebra Basics", [
                    ("Solve: 2x + 5 = 15", "mcq", '["x=5", "x=10", "x=15"]', "x=5", "Subtract 5, then divide by 2"),
                    ("Is (a+b)² = a² + b²?", "true_false", "[]", "False", "Correct formula: (a+b)² = a² + 2ab + b²"),
                ]),
            ],
            "Science": [
                ("Basic Physics", [
                    ("Force = Mass × ?", "mcq", '["Acceleration", "Velocity", "Distance"]', "Acceleration", "Newton's Second Law"),
                ]),
            ],
            "Computer Science": [
                ("Python Basics", [
                    ("Which keyword defines a function?", "mcq", '["def", "function", "func"]', "def", "Use 'def' keyword"),
                ]),
            ],
        }
        
        quiz_count = 0
        for (class_name, subject), course in courses.items():
            if subject in quiz_templates:
                for quiz_title, questions_data in quiz_templates[subject]:
                    quiz = Quiz(
                        title=f"{quiz_title} - {class_name}",
                        description=f"Test for Class {class_name}",
                        course_id=course.id,
                        time_limit_minutes=30,
                        max_attempts=3,
                        is_active=True
                    )
                    db.add(quiz)
                    db.flush()
                    quiz_count += 1
                    
                    for q_text, q_type, options, answer, explanation in questions_data:
                        question = QuizQuestion(
                            quiz_id=quiz.id,
                            question_text=q_text,
                            question_type=q_type,
                            options=options,
                            correct_answer=answer,
                            points=10.0,
                            explanation=explanation
                        )
                        db.add(question)
        
        print(f"   ✅ Created {quiz_count} quizzes")
        
        # ================================================================
        # STEP 8: Create Assignments
        # ================================================================
        print("\n📋 Step 8: Creating Assignments...")
        
        assignment_count = 0
        assignment_templates = {
            "Mathematics": "Solve the attached problem set",
            "Science": "Lab report on the recent experiment",
            "English": "Essay writing assignment",
            "Computer Science": "Programming project",
        }
        
        for (class_name, subject), course in courses.items():
            if subject in assignment_templates:
                assignment = Assignment(
                    title=f"{subject} Assignment - {class_name}",
                    description=assignment_templates[subject],
                    course_id=course.id,
                    max_score=100,
                    due_date=datetime.utcnow() + timedelta(days=14),
                    is_active=True
                )
                db.add(assignment)
                assignment_count += 1
        
        print(f"   ✅ Created {assignment_count} assignments")
        
        # ================================================================
        # STEP 9: Create Achievements
        # ================================================================
        print("\n🏆 Step 9: Creating Achievements...")
        achievements_data = [
            ("First Quiz", "Complete your first quiz", "🎯", 50, "quiz_complete", 1),
            ("Perfect Score", "Score 100% on a quiz", "🏆", 100, "quiz_score", 100),
            ("Streak Master", "7-day login streak", "🔥", 200, "streak", 7),
            ("Knowledge Seeker", "Ask 50 AI questions", "💡", 150, "chatbot_queries", 50),
            ("Class Topper", "Complete all course quizzes", "🎓", 500, "course_complete", 1),
        ]
        
        for name, desc, icon, xp, cond_type, cond_val in achievements_data:
            achievement = Achievement(
                name=name,
                description=desc,
                badge_icon=icon,
                xp_reward=xp,
                condition_type=cond_type,
                condition_value=cond_val
            )
            db.add(achievement)
        
        print(f"   ✅ Created {len(achievements_data)} achievements")
        
        # ================================================================
        # Commit All Changes
        # ================================================================
        print("\n💾 Saving to database...")
        db.commit()
        
        # ================================================================
        # FINAL SUMMARY
        # ================================================================
        print("\n" + "=" * 80)
        print("✅ COMPLETE SCHOOL DATABASE CREATED!")
        print("=" * 80)
        
        print("\n🏫 School Structure:")
        print("   📚 Classes: 10A, 10B, 11A, 11B, 12A, 12B")
        print(f"   👨‍🏫 Teachers: {len(teachers)} (assigned by subject)")
        print(f"   👨‍🎓 Students: {total_students} (distributed across classes)")
        print(f"   📖 Courses: {course_count} (subject × class)")
        print(f"   🎒 Enrollments: {enrollment_count}")
        print(f"   🤖 AI Chatbots: {chatbot_count}")
        print(f"   📝 Quizzes: {quiz_count}")
        print(f"   📋 Assignments: {assignment_count}")
        print(f"   🏆 Achievements: {len(achievements_data)}")
        
        print("\n🔐 Sample Login Credentials:")
        print("\n   👑 ADMIN:")
        print("      admin / admin123")
        
        print("\n   👨‍🏫 TEACHERS:")
        print("      rajeshkumar / rajesh123 (Mathematics)")
        print("      priyasharma / priya123 (Computer Science)")
        print("      amitpatel / amit123 (English)")
        print("      ... and 7 more teachers")
        
        print("\n   👨‍🎓 STUDENTS (Class 10A):")
        print("      aaravgupta / aaravgupta123")
        print("      diyaverma / diyaverma123")
        print("      ... and 28 more students")
        
        print("\n🎯 What to Test:")
        print("   1. Login as admin → Manage users")
        print("   2. Login as teacher → View your courses by class")
        print("   3. Login as student → See your class subjects")
        print("   4. Try AI chatbot, quizzes, assignments")
        
        print("\n🌐 Access Points:")
        print("   Backend API: http://localhost:8000/docs")
        print("   Frontend: http://localhost:3000")
        
        print("\n" + "=" * 80)


if __name__ == "__main__":
    create_school_demo_data()
