"""
AI-Powered Quiz Generation and Answer Evaluation
Supports multiple LLM providers and RAG-based content generation
Uses ML scoring for answer evaluation alongside LLM
"""

import json
from typing import List, Dict, Optional
from config import settings


class QuizGenerator:
    """
    Generate quiz questions using multiple LLM providers
    Supports RAG-based generation from course materials
    """
    
    def __init__(self, llm_provider: str = "gemini", llm_model: str = None):
        """
        Initialize quiz generator with configurable LLM
        
        Args:
            llm_provider: 'gemini' or 'mistral'
            llm_model: Specific model name (optional)
        """
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self._provider = None
    
    def _get_provider(self):
        """Lazy load LLM provider"""
        if self._provider is None:
            from ai_services.llm_providers import get_llm_provider
            self._provider = get_llm_provider(self.llm_provider, self.llm_model)
        return self._provider
    
    def generate_quiz_questions(
        self,
        topic: str,
        num_questions: int = 5,
        question_types: List[str] = None,
        difficulty: str = "medium"
    ) -> List[Dict]:
        """
        Generate quiz questions for a given topic
        
        Args:
            topic: The topic/subject for questions
            num_questions: Number of questions to generate
            question_types: List of types ('mcq', 'true_false', 'short_answer')
            difficulty: easy, medium, or hard
            
        Returns:
            List of question dictionaries
        """
        if question_types is None:
            question_types = ["mcq", "true_false"]
        
        prompt = f"""Generate {num_questions} {difficulty} difficulty quiz questions about: {topic}

Question types to include: {', '.join(question_types)}

For each question, provide:
1. question_text: The question
2. question_type: One of {question_types}
3. options: Array of options (for MCQ and true/false)
4. correct_answer: The correct answer
5. explanation: Brief explanation of the answer
6. points: Suggested points (1.0 for easy, 2.0 for medium, 3.0 for hard)

Return ONLY a JSON array of questions, nothing else. Example format:
[
  {{
    "question_text": "What is the capital of France?",
    "question_type": "mcq",
    "options": ["London", "Berlin", "Paris", "Madrid"],
    "correct_answer": "Paris",
    "explanation": "Paris is the capital and largest city of France.",
    "points": 1.0
  }}
]"""
        
        return self._generate_and_parse(prompt)
    
    def generate_from_content(
        self,
        content: str,
        num_questions: int = 5,
        question_types: List[str] = None
    ) -> List[Dict]:
        """
        Generate quiz questions based on provided content/document
        
        Args:
            content: The learning content/document text
            num_questions: Number of questions to generate
            question_types: Types of questions
            
        Returns:
            List of question dictionaries
        """
        if question_types is None:
            question_types = ["mcq", "short_answer"]
        
        # Truncate content if too long
        max_content_length = 4000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
        
        prompt = f"""Based on the following learning content, generate {num_questions} quiz questions.

**Content:**
{content}

**Requirements:**
- Question types: {', '.join(question_types)}
- Cover key concepts from the content
- Include a mix of difficulty levels
- Provide clear explanations
- Questions should ONLY be based on the provided content

Return ONLY a JSON array of questions with this structure:
[
  {{
    "question_text": "...",
    "question_type": "mcq" or "true_false" or "short_answer",
    "options": ["...", "...", "...", "..."],
    "correct_answer": "...",
    "explanation": "...",
    "points": 1.0 or 2.0 or 3.0
  }}
]"""
        
        return self._generate_and_parse(prompt)
    
    def generate_from_rag(
        self,
        collection_name: str,
        topic: str = None,
        num_questions: int = 5,
        question_types: List[str] = None,
        difficulty: str = "medium"
    ) -> Dict:
        """
        Generate quiz questions from RAG-retrieved course content
        
        Args:
            collection_name: ChromaDB collection name for the chatbot
            topic: Optional topic to focus questions on
            num_questions: Number of questions to generate
            question_types: Types of questions
            difficulty: easy, medium, or hard
            
        Returns:
            Dict with questions and metadata
        """
        from ai_services.rag_system import get_rag_system
        
        if question_types is None:
            question_types = ["mcq", "true_false", "short_answer"]
        
        # Get RAG system
        rag = get_rag_system()
        
        # Retrieve relevant content from the collection
        query = topic or "main concepts and important topics"
        chunks = rag.retrieve_relevant_chunks(collection_name, query, top_k=10)
        
        if not chunks:
            return {
                "questions": [],
                "error": "No content found in the course materials",
                "message": "Please upload documents to the chatbot first"
            }
        
        # Combine retrieved chunks into context
        context = "\n\n---\n\n".join([chunk["content"] for chunk in chunks])
        
        prompt = f"""Based STRICTLY on the following course content, generate {num_questions} {difficulty} difficulty quiz questions.

**Course Content:**
{context}

**Requirements:**
- Question types: {', '.join(question_types)}
- ALL questions MUST be directly answerable from the provided content
- Do NOT use any external knowledge
- Cover key concepts from the content
- Provide clear explanations that reference the content
- Difficulty level: {difficulty}

Return ONLY a JSON array of questions with this structure:
[
  {{
    "question_text": "...",
    "question_type": "mcq" or "true_false" or "short_answer",
    "options": ["...", "...", "...", "..."],
    "correct_answer": "...",
    "explanation": "...",
    "points": 1.0 or 2.0 or 3.0,
    "topic_covered": "Brief description of the topic this question covers"
  }}
]"""
        
        questions = self._generate_and_parse(prompt)
        
        return {
            "questions": questions,
            "source": "rag",
            "collection": collection_name,
            "chunks_used": len(chunks),
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model
        }
    
    def _generate_and_parse(self, prompt: str) -> List[Dict]:
        """Generate with LLM and parse JSON response"""
        try:
            provider = self._get_provider()
            response = provider.generate(prompt)
            
            # Clean and parse response
            response_text = response.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # Parse JSON
            questions = json.loads(response_text)
            return questions
            
            print(f"❌ JSON Parse Error. Raw response: '{response_text}'")
            import traceback
            traceback.print_exc()
            snippet = response_text[:200] if response_text else "Empty response"
            return [{
                "error": "Failed to parse generated questions",
                "message": f"Invalid JSON ({str(e)}). Raw response starting with: {snippet}",
                "raw_response": response_text
            }]
        except Exception as e:
            return [{
                "error": "Failed to generate questions",
                "message": str(e)
            }]


class AnswerEvaluator:
    """
    Evaluate student answers using ML scoring + optional LLM feedback
    
    Combines:
    - ML-based scoring (TF-IDF, Semantic, Keyword matching)
    - Optional LLM feedback for detailed explanations
    """
    
    def __init__(
        self, 
        llm_provider: str = "gemini", 
        llm_model: str = None,
        use_ml_scoring: bool = True
    ):
        """
        Initialize answer evaluator
        
        Args:
            llm_provider: 'gemini' or 'mistral'
            llm_model: Specific model name
            use_ml_scoring: Whether to use ML-based scoring (recommended)
        """
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.use_ml_scoring = use_ml_scoring
        self._provider = None
        self._ml_scorer = None
    
    def _get_provider(self):
        """Lazy load LLM provider"""
        if self._provider is None:
            from ai_services.llm_providers import get_llm_provider
            self._provider = get_llm_provider(self.llm_provider, self.llm_model)
        return self._provider
    
    def _get_ml_scorer(self):
        """Lazy load ML scorer"""
        if self._ml_scorer is None:
            from ai_services.ml_scoring import get_hybrid_scorer
            self._ml_scorer = get_hybrid_scorer()
        return self._ml_scorer
    
    def evaluate_mcq(
        self,
        student_answer: str,
        correct_answer: str
    ) -> Dict:
        """
        Evaluate multiple choice or true/false answers
        
        Args:
            student_answer: Student's selected answer
            correct_answer: The correct answer
            
        Returns:
            Dict with score and feedback
        """
        is_correct = student_answer.strip().lower() == correct_answer.strip().lower()
        
        return {
            "is_correct": is_correct,
            "score": 1.0 if is_correct else 0.0,
            "feedback": "Correct!" if is_correct else f"Incorrect. The correct answer is: {correct_answer}",
            "method": "exact_match"
        }
    
    def evaluate_short_answer(
        self,
        question: str,
        student_answer: str,
        correct_answer: str,
        max_points: float = 1.0,
        use_llm_feedback: bool = True
    ) -> Dict:
        """
        Evaluate short answer questions using ML scoring + optional LLM feedback
        
        Args:
            question: The question text
            student_answer: Student's written answer
            correct_answer: Model/expected answer
            max_points: Maximum points for this question
            use_llm_feedback: Whether to get additional LLM feedback
            
        Returns:
            Dict with score, feedback, and detailed evaluation
        """
        if not student_answer:
            return {
                "score": 0.0,
                "max_score": max_points,
                "feedback": "No answer provided",
                "method": "empty_check"
            }
        
        # Use ML-based scoring
        if self.use_ml_scoring:
            ml_scorer = self._get_ml_scorer()
            result = ml_scorer.score_answer(
                student_answer=student_answer,
                correct_answer=correct_answer,
                question=question,
                max_points=max_points,
                llm_provider=self.llm_provider if use_llm_feedback else None,
                llm_model=self.llm_model
            )
            return result
        
        # Fallback to LLM-only evaluation
        return self._evaluate_with_llm(question, student_answer, correct_answer, max_points)
    
    def _evaluate_with_llm(
        self,
        question: str,
        student_answer: str,
        correct_answer: str,
        max_points: float
    ) -> Dict:
        """Evaluate using LLM only (fallback)"""
        prompt = f"""You are an educational assessment AI. Evaluate the student's answer.

**Question:**
{question}

**Model Answer:**
{correct_answer}

**Student's Answer:**
{student_answer}

**Task:**
1. Compare the student's answer to the model answer
2. Assign a score from 0.0 to {max_points} based on:
   - Correctness of key concepts
   - Completeness
   - Clarity and coherence
3. Provide constructive feedback

Return ONLY a JSON object with this structure:
{{
  "score": 0.0 to {max_points},
  "feedback": "Brief constructive feedback",
  "key_points_covered": ["point1", "point2"],
  "key_points_missed": ["point1", "point2"],
  "overall_assessment": "excellent/good/fair/poor"
}}"""
        
        try:
            provider = self._get_provider()
            response = provider.generate(prompt)
            
            # Parse response
            response_text = response.strip()
            response_text = response_text.replace("```json", "").replace("```", "").strip()
            
            evaluation = json.loads(response_text)
            evaluation["method"] = "llm_only"
            evaluation["llm_provider"] = self.llm_provider
            return evaluation
            
        except Exception as e:
            return {
                "error": "Failed to evaluate answer",
                "message": str(e),
                "score": 0.0,
                "feedback": "Auto-grading failed. Manual review needed.",
                "method": "error"
            }
    
    def evaluate_assignment(
        self,
        assignment_description: str,
        student_submission: str,
        max_score: float = 100.0,
        rubric: Dict = None
    ) -> Dict:
        """
        Evaluate full assignment submissions using ML + LLM
        
        Args:
            assignment_description: The assignment requirements
            student_submission: Student's submission text
            max_score: Maximum possible score
            rubric: Optional grading rubric
            
        Returns:
            Dict with score, feedback, and detailed evaluation
        """
        if not student_submission:
            return {
                "score": 0.0,
                "max_score": max_score,
                "feedback": "No submission provided",
                "method": "empty_check"
            }
        
        # Get ML-based score first
        ml_result = None
        if self.use_ml_scoring:
            ml_scorer = self._get_ml_scorer()
            ml_result = ml_scorer.score_answer(
                student_answer=student_submission,
                correct_answer=assignment_description,  # Use description as reference
                max_points=max_score
            )
        
        # Get detailed LLM evaluation
        # Truncate if too long
        submission_text = student_submission
        if len(submission_text) > 3000:
            submission_text = submission_text[:3000] + "\n[Content truncated...]"
        
        rubric_text = ""
        if rubric:
            rubric_text = f"\n**Grading Rubric:**\n{json.dumps(rubric, indent=2)}"
        
        prompt = f"""You are an educational assessment AI. Evaluate this assignment submission.

**Assignment Description:**
{assignment_description}
{rubric_text}

**Student Submission:**
{submission_text}

**Task:**
Provide a comprehensive evaluation with:
1. Score (0 to {max_score})
2. Detailed feedback
3. Strengths identified
4. Areas for improvement
5. Specific suggestions

Return ONLY a JSON object:
{{
  "score": 0 to {max_score},
  "feedback": "Comprehensive feedback paragraph",
  "strengths": ["strength1", "strength2"],
  "improvements": ["area1", "area2"],
  "suggestions": ["suggestion1", "suggestion2"],
  "grade_breakdown": {{
    "content_quality": 0-30,
    "completeness": 0-30,
    "organization": 0-20,
    "technical_accuracy": 0-20
  }}
}}"""
        
        try:
            provider = self._get_provider()
            response = provider.generate(prompt)
            
            # Parse response
            response_text = response.strip()
            response_text = response_text.replace("```json", "").replace("```", "").strip()
            
            evaluation = json.loads(response_text)
            evaluation["method"] = "hybrid" if ml_result else "llm_only"
            evaluation["llm_provider"] = self.llm_provider
            
            # Include ML scores if available
            if ml_result:
                evaluation["ml_analysis"] = {
                    "score": ml_result.get("score"),
                    "percentage": ml_result.get("percentage"),
                    "component_scores": ml_result.get("component_scores")
                }
                
                # Average ML and LLM scores for final
                ml_normalized = (ml_result.get("percentage", 0) / 100) * max_score
                llm_score = evaluation.get("score", 0)
                evaluation["combined_score"] = round((ml_normalized + llm_score) / 2, 2)
            
            return evaluation
            
        except Exception as e:
            # If LLM fails but ML worked, use ML result
            if ml_result:
                return {
                    "score": ml_result.get("score", 0),
                    "feedback": ml_result.get("feedback", "Auto-graded using ML"),
                    "method": "ml_only",
                    "ml_analysis": ml_result
                }
            
            return {
                "error": "Failed to evaluate assignment",
                "message": str(e),
                "score": 0.0,
                "feedback": "Auto-grading failed. Manual review needed.",
                "method": "error"
            }


# Singleton instances with default providers
_quiz_generator = None
_answer_evaluator = None


def get_quiz_generator(
    llm_provider: str = "gemini", 
    llm_model: str = None
) -> QuizGenerator:
    """Get or create quiz generator"""
    global _quiz_generator
    # Create new instance if provider/model changed
    if _quiz_generator is None or \
       _quiz_generator.llm_provider != llm_provider or \
       _quiz_generator.llm_model != llm_model:
        _quiz_generator = QuizGenerator(llm_provider, llm_model)
    return _quiz_generator


def get_answer_evaluator(
    llm_provider: str = "gemini",
    llm_model: str = None,
    use_ml_scoring: bool = True
) -> AnswerEvaluator:
    """Get or create answer evaluator"""
    global _answer_evaluator
    # Create new instance if settings changed
    if _answer_evaluator is None or \
       _answer_evaluator.llm_provider != llm_provider or \
       _answer_evaluator.llm_model != llm_model:
        _answer_evaluator = AnswerEvaluator(llm_provider, llm_model, use_ml_scoring)
    return _answer_evaluator
