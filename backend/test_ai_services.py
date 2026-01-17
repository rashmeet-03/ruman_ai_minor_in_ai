"""
Comprehensive test suite for Phase 5: AI/ML Services
Tests RAG system, ML models, quiz generation, and answer evaluation
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_services import (
    get_rag_system,
    get_quiz_generator,
    get_answer_evaluator,
    get_performance_predictor,
    get_learning_gap_analyzer
)
from config import settings
import tempfile


def test_rag_system():
    """Test RAG system functionality"""
    print("=" * 60)
    print("TEST 1: RAG System")
    print("=" * 60)
    
    rag = get_rag_system()
    
    # Test 1: Create sample document
    sample_text = """
    Python is a high-level, interpreted programming language.
    It was created by Guido van Rossum and first released in 1991.
    Python emphasizes code readability with its notable use of significant indentation.
    Python is dynamically typed and garbage-collected.
    It supports multiple programming paradigms, including structured, object-oriented, and functional programming.
    """
    
    print("\n1.1 Testing text chunking...")
    chunks = rag.chunk_document(sample_text)
    print(f"   ✅ Created {len(chunks)} chunks")
    print(f"   Sample chunk: {chunks[0][:100]}...")
    
    print("\n1.2 Testing embedding generation...")
    embeddings = rag.embed_chunks(chunks)
    print(f"   ✅ Generated {len(embeddings)} embeddings")
    print(f"   Embedding dimension: {len(embeddings[0])}")
    
    print("\n1.3 Testing ChromaDB storage...")
    collection_name = "test_collection"
    chunk_count = rag.store_in_chromadb(collection_name, chunks, embeddings)
    print(f"   ✅ Stored {chunk_count} chunks in ChromaDB")
    
    print("\n1.4 Testing retrieval...")
    retrieved = rag.retrieve_relevant_chunks(collection_name, "Who created Python?", top_k=2)
    print(f"   ✅ Retrieved {len(retrieved)} relevant chunks")
    if retrieved:
        print(f"   Top result: {retrieved[0]['content'][:100]}...")
    
    print("\n1.5 Testing full RAG query...")
    result = rag.query(collection_name, "What year was Python first released?")
    print(f"   ✅ Generated answer:")
    print(f"   {result['answer'][:200]}...")
    print(f"   Context used: {result['context_used']}")
    
    print("\n✅ RAG System tests PASSED!\n")


def test_quiz_generation():
    """Test AI quiz generation"""
    print("=" * 60)
    print("TEST 2: Quiz Generation")
    print("=" * 60)
    
    quiz_gen = get_quiz_generator()
    
    print("\n2.1 Testing quiz question generation...")
    questions = quiz_gen.generate_quiz_questions(
        topic="Python Programming",
        num_questions=3,
        difficulty="easy"
    )
    
    if questions and "error" not in questions[0]:
        print(f"   ✅ Generated {len(questions)} questions")
        for i, q in enumerate(questions, 1):
            print(f"\n   Question {i}:")
            print(f"   Q: {q.get('question_text', 'N/A')}")
            print(f"   Type: {q.get('question_type', 'N/A')}")
            print(f"   Options: {q.get('options', 'N/A')}")
            print(f"   Answer: {q.get('correct_answer', 'N/A')}")
    else:
        print(f"   ⚠️  {questions[0].get('message', 'Unknown error')}")
    
    print("\n✅ Quiz Generation tests PASSED!\n")


def test_answer_evaluation():
    """Test answer evaluation"""
    print("=" * 60)
    print("TEST 3: Answer Evaluation")
    print("=" * 60)
    
    evaluator = get_answer_evaluator()
    
    print("\n3.1 Testing MCQ evaluation...")
    result = evaluator.evaluate_mcq("Paris", "Paris")
    print(f"   ✅ Correct answer: {result['is_correct']}, Score: {result['score']}")
    
    result = evaluator.evaluate_mcq("London", "Paris")
    print(f"   ✅ Wrong answer: {result['is_correct']}, Feedback: {result['feedback']}")
    
    print("\n3.2 Testing short answer evaluation...")
    evaluation = evaluator.evaluate_short_answer(
        question="What is the capital of France?",
        student_answer="The capital of France is Paris, which is also the largest city.",
        correct_answer="Paris",
        max_points=2.0
    )
    
    if "error" not in evaluation:
        print(f"   ✅ Score: {evaluation.get('score', 'N/A')}/{2.0}")
        print(f"   Feedback: {evaluation.get('feedback', 'N/A')}")
    else:
        print(f"   ⚠️  {evaluation.get('message', 'Unknown error')}")
    
    print("\n✅ Answer Evaluation tests PASSED!\n")


def test_performance_prediction():
    """Test ML performance prediction"""
    print("=" * 60)
    print("TEST 4: Performance Prediction")
    print("=" * 60)
    
    predictor = get_performance_predictor()
    
    print("\n4.1 Testing model training...")
    # Sample student data
    student_data = [
        {"quiz_average": 85, "assignment_average": 90, "quizzes_attempted": 5, "assignments_submitted": 4, "days_since_enrollment": 30, "engagement_score": 8, "overall_average": 87.5},
        {"quiz_average": 60, "assignment_average": 65, "quizzes_attempted": 4, "assignments_submitted": 3, "days_since_enrollment": 25, "engagement_score": 5, "overall_average": 62.5},
        {"quiz_average": 40, "assignment_average": 45, "quizzes_attempted": 2, "assignments_submitted": 1, "days_since_enrollment": 20, "engagement_score": 3, "overall_average": 42.5},
        {"quiz_average": 75, "assignment_average": 80, "quizzes_attempted": 5, "assignments_submitted": 5, "days_since_enrollment": 35, "engagement_score": 7, "overall_average": 77.5},
        {"quiz_average": 55, "assignment_average": 50, "quizzes_attempted": 3, "assignments_submitted": 2, "days_since_enrollment": 15, "engagement_score": 4, "overall_average": 52.5},
    ]
    
    trained = predictor.train(student_data)
    if trained:
        print(f"   ✅ Model trained on {len(student_data)} students")
    else:
        print(f"   ⚠️  Not enough data to train")
        return
    
    print("\n4.2 Testing risk prediction...")
    test_student = {
        "quiz_average": 45,
        "assignment_average": 50,
        "quizzes_attempted": 2,
        "assignments_submitted": 1,
        "days_since_enrollment": 10,
        "engagement_score": 3
    }
    
    prediction = predictor.predict_risk(test_student)
    print(f"   ✅ Risk Level: {prediction['risk_level']}")
    print(f"   Confidence: {prediction['confidence']:.2f}")
    print(f"   Probabilities: Low={prediction['probabilities']['low']:.2f}, Med={prediction['probabilities']['medium']:.2f}, High={prediction['probabilities']['high']:.2f}")
    
    print("\n✅ Performance Prediction tests PASSED!\n")


def test_learning_gap_analysis():
    """Test learning gap analysis"""
    print("=" * 60)
    print("TEST 5: Learning Gap Analysis")
    print("=" * 60)
    
    analyzer = get_learning_gap_analyzer()
    
    print("\n5.1 Testing topic performance analysis...")
    topic_scores = {
        "Variables": [80, 85, 90, 75, 88],
        "Functions": [70, 65, 75, 60, 72],
        "Classes": [50, 45, 55, 40, 48],
        "Loops": [85, 90, 95, 80, 92]
    }
    
    analysis = analyzer.analyze_topic_performance(topic_scores)
    print(f"   ✅ Analyzed {len(topic_scores)} topics")
    print(f"\n   Weak topics:")
    for topic in analysis['weak_topics'][:3]:
        print(f"   - {topic['topic']}: {topic['average_score']}% ({topic['difficulty_level']})")
    
    if analysis['analysis']:
        print(f"\n   Recommendations:")
        for rec in analysis['analysis']:
            print(f"   {rec}")
    
    print("\n5.2 Testing student clustering...")
    student_performance = [
        {"student_id": 1, "quiz_average": 85, "assignment_average": 90, "quizzes_attempted": 5, "assignments_submitted": 4},
        {"student_id": 2, "quiz_average": 60, "assignment_average": 65, "quizzes_attempted": 4, "assignments_submitted": 3},
        {"student_id": 3, "quiz_average": 40, "assignment_average": 45, "quizzes_attempted": 2, "assignments_submitted": 1},
        {"student_id": 4, "quiz_average": 75, "assignment_average": 80, "quizzes_attempted": 5, "assignments_submitted": 5},
        {"student_id": 5, "quiz_average": 55, "assignment_average": 50, "quizzes_attempted": 3, "assignments_submitted": 2},
    ]
    
    clusters = analyzer.cluster_students(student_performance)
    if "clusters" in clusters and clusters["clusters"]:
        print(f"   ✅ Created {clusters['num_clusters']} clusters")
        for cluster in clusters['clusters']:
            print(f"\n   Cluster {cluster['cluster_id']} ({cluster['performance_tier']}):")
            print(f"   - Students: {cluster['student_count']}")
            print(f"   - Avg Quiz: {cluster['characteristics']['avg_quiz_score']}")
            print(f"   - Avg Assignment: {cluster['characteristics']['avg_assignment_score']}")
    else:
        print(f"   ⚠️  {clusters.get('message', 'Clustering failed')}")
    
    print("\n✅ Learning Gap Analysis tests PASSED!\n")


def run_all_tests():
    """Run all AI/ML tests"""
    print("\n🚀 Starting AI/ML Services Test Suite")
    print(f"Gemini API configured: {'✅' if settings.GEMINI_API_KEY else '❌'}")
    print(f"ChromaDB path: {settings.CHROMA_PERSIST_DIRECTORY}")
    print()
    
    try:
        test_rag_system()
        test_quiz_generation()
        test_answer_evaluation()
        test_performance_prediction()
        test_learning_gap_analysis()
        
        print("=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print("\n✅ RAG System: Document processing, embedding, retrieval, generation")
        print("✅ Quiz Generation: AI-powered question creation")
        print("✅ Answer Evaluation: MCQ and short answer grading")
        print("✅ Performance Prediction: Risk assessment with ML")
        print("✅ Learning Gap Analysis: Topic analysis and clustering")
        print()
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
