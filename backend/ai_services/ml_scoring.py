"""
ML-Based Answer Scoring System
Uses traditional ML techniques instead of pure LLM API calls for scoring

Components:
1. TextSimilarityScorer - TF-IDF + Cosine Similarity
2. SemanticSimilarityScorer - Sentence Transformer Embeddings
3. KeywordMatchScorer - Keyword extraction and matching
4. HybridScorer - Combines all methods for robust evaluation
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import re
from collections import Counter


class TextSimilarityScorer:
    """
    Score answers using TF-IDF vectorization and cosine similarity
    
    This is a traditional ML approach that:
    1. Converts text to TF-IDF vectors
    2. Computes cosine similarity between student and correct answers
    """
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            ngram_range=(1, 2),  # Unigrams and bigrams
            max_features=5000
        )
    
    def score_answer(
        self, 
        student_answer: str, 
        correct_answer: str
    ) -> Dict:
        """
        Score using TF-IDF cosine similarity
        
        Args:
            student_answer: Student's submitted answer
            correct_answer: Model/expected answer
            
        Returns:
            Dict with score (0.0-1.0) and details
        """
        if not student_answer or not correct_answer:
            return {
                "score": 0.0,
                "method": "tfidf_cosine",
                "details": "Empty answer provided"
            }
        
        try:
            # Fit and transform both answers
            texts = [correct_answer, student_answer]
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            # Compute cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return {
                "score": round(float(similarity), 4),
                "method": "tfidf_cosine",
                "vocabulary_size": len(self.vectorizer.vocabulary_),
                "details": self._get_score_interpretation(similarity)
            }
        except Exception as e:
            return {
                "score": 0.0,
                "method": "tfidf_cosine",
                "error": str(e)
            }
    
    def _get_score_interpretation(self, score: float) -> str:
        """Interpret the similarity score"""
        if score >= 0.8:
            return "Excellent match - covers key concepts well"
        elif score >= 0.6:
            return "Good match - most concepts covered"
        elif score >= 0.4:
            return "Partial match - some concepts covered"
        elif score >= 0.2:
            return "Weak match - few concepts covered"
        else:
            return "Poor match - answer does not align with expected content"


class SemanticSimilarityScorer:
    """
    Score answers using sentence embeddings for semantic similarity
    
    Uses Sentence Transformers (all-MiniLM-L6-v2) to capture meaning
    beyond just word overlap
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
    
    def score_answer(
        self, 
        student_answer: str, 
        correct_answer: str
    ) -> Dict:
        """
        Score using semantic embeddings
        
        Args:
            student_answer: Student's submitted answer
            correct_answer: Model/expected answer
            
        Returns:
            Dict with score (0.0-1.0) and details
        """
        if not student_answer or not correct_answer:
            return {
                "score": 0.0,
                "method": "semantic_embedding",
                "details": "Empty answer provided"
            }
        
        try:
            # Generate embeddings
            embeddings = self.model.encode([correct_answer, student_answer])
            
            # Compute cosine similarity
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            
            # Convert to 0-1 range (cosine similarity can be negative)
            normalized_score = (similarity + 1) / 2
            
            return {
                "score": round(float(normalized_score), 4),
                "raw_similarity": round(float(similarity), 4),
                "method": "semantic_embedding",
                "model": self.model_name,
                "details": self._get_score_interpretation(normalized_score)
            }
        except Exception as e:
            return {
                "score": 0.0,
                "method": "semantic_embedding",
                "error": str(e)
            }
    
    def _get_score_interpretation(self, score: float) -> str:
        """Interpret the semantic similarity score"""
        if score >= 0.85:
            return "Semantically very similar - excellent understanding"
        elif score >= 0.70:
            return "Semantically similar - good understanding"
        elif score >= 0.55:
            return "Partially similar - moderate understanding"
        elif score >= 0.40:
            return "Some semantic overlap - basic understanding"
        else:
            return "Low semantic similarity - possible misunderstanding"


class KeywordMatchScorer:
    """
    Score based on presence of key concepts/keywords
    
    Extracts important terms and checks for their presence
    """
    
    def __init__(self):
        # Common stop words to filter out
        self.stop_words = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 
            'would', 'could', 'should', 'may', 'might', 'must', 'shall',
            'can', 'need', 'to', 'of', 'in', 'for', 'on', 'with', 'at',
            'by', 'from', 'as', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'between', 'under', 'again',
            'further', 'then', 'once', 'here', 'there', 'when', 'where',
            'why', 'how', 'all', 'each', 'few', 'more', 'most', 'other',
            'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
            'so', 'than', 'too', 'very', 'just', 'and', 'but', 'if', 'or',
            'because', 'until', 'while', 'this', 'that', 'these', 'those',
            'it', 'its', 'they', 'them', 'their', 'what', 'which', 'who'
        }
    
    def extract_keywords(self, text: str, min_length: int = 3) -> List[str]:
        """
        Extract important keywords from text
        
        Args:
            text: Input text
            min_length: Minimum word length to consider
            
        Returns:
            List of extracted keywords
        """
        # Tokenize and clean
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # Filter stop words and short words
        keywords = [
            word for word in words 
            if word not in self.stop_words and len(word) >= min_length
        ]
        
        return keywords
    
    def score_answer(
        self, 
        student_answer: str, 
        correct_answer: str
    ) -> Dict:
        """
        Score based on keyword matching
        
        Args:
            student_answer: Student's submitted answer
            correct_answer: Model/expected answer
            
        Returns:
            Dict with score, matched keywords, and missed keywords
        """
        if not student_answer or not correct_answer:
            return {
                "score": 0.0,
                "method": "keyword_match",
                "details": "Empty answer provided"
            }
        
        # Extract keywords
        expected_keywords = set(self.extract_keywords(correct_answer))
        student_keywords = set(self.extract_keywords(student_answer))
        
        if not expected_keywords:
            return {
                "score": 1.0,
                "method": "keyword_match",
                "details": "No keywords to match"
            }
        
        # Find matches and misses
        matched = expected_keywords & student_keywords
        missed = expected_keywords - student_keywords
        extra = student_keywords - expected_keywords
        
        # Calculate coverage score
        coverage = len(matched) / len(expected_keywords)
        
        # Bonus for additional relevant terms (capped)
        bonus = min(len(extra) * 0.02, 0.1)
        
        final_score = min(coverage + bonus, 1.0)
        
        return {
            "score": round(final_score, 4),
            "method": "keyword_match",
            "matched_keywords": list(matched)[:10],  # Top 10
            "missed_keywords": list(missed)[:10],
            "additional_keywords": list(extra)[:5],
            "coverage_percent": round(coverage * 100, 1),
            "details": self._get_feedback(coverage, list(missed))
        }
    
    def _get_feedback(self, coverage: float, missed: List[str]) -> str:
        """Generate feedback based on keyword coverage"""
        if coverage >= 0.9:
            return "Excellent - covers all key concepts"
        elif coverage >= 0.7:
            msg = "Good - most key concepts covered"
            if missed:
                msg += f". Consider including: {', '.join(missed[:3])}"
            return msg
        elif coverage >= 0.5:
            msg = "Partial - some concepts missing"
            if missed:
                msg += f". Missing: {', '.join(missed[:5])}"
            return msg
        else:
            msg = "Incomplete - many key concepts missing"
            if missed:
                msg += f". Key terms to include: {', '.join(missed[:5])}"
            return msg


class HybridScorer:
    """
    Combines multiple scoring methods for robust answer evaluation
    
    Uses weighted combination of:
    - TF-IDF similarity (lexical matching)
    - Semantic similarity (meaning understanding)
    - Keyword matching (concept coverage)
    """
    
    def __init__(
        self,
        weights: Dict[str, float] = None,
        use_llm_fallback: bool = True
    ):
        """
        Initialize hybrid scorer
        
        Args:
            weights: Dict with 'tfidf', 'semantic', 'keyword' weights (should sum to 1.0)
            use_llm_fallback: Whether to use LLM for subjective feedback
        """
        self.text_scorer = TextSimilarityScorer()
        self.semantic_scorer = SemanticSimilarityScorer()
        self.keyword_scorer = KeywordMatchScorer()
        
        # Default weights emphasize semantic understanding
        self.weights = weights or {
            'tfidf': 0.25,
            'semantic': 0.50,
            'keyword': 0.25
        }
        
        self.use_llm_fallback = use_llm_fallback
    
    def score_answer(
        self,
        student_answer: str,
        correct_answer: str,
        question: str = None,
        max_points: float = 1.0,
        llm_provider: str = None,
        llm_model: str = None
    ) -> Dict:
        """
        Score answer using all methods combined
        
        Args:
            student_answer: Student's submitted answer
            correct_answer: Model/expected answer
            question: Optional question text for context
            max_points: Maximum points for this answer
            llm_provider: Optional LLM for additional feedback
            llm_model: Specific LLM model
            
        Returns:
            Comprehensive evaluation dict
        """
        # Get individual scores
        tfidf_result = self.text_scorer.score_answer(student_answer, correct_answer)
        semantic_result = self.semantic_scorer.score_answer(student_answer, correct_answer)
        keyword_result = self.keyword_scorer.score_answer(student_answer, correct_answer)
        
        # Calculate weighted score
        weighted_score = (
            self.weights['tfidf'] * tfidf_result['score'] +
            self.weights['semantic'] * semantic_result['score'] +
            self.weights['keyword'] * keyword_result['score']
        )
        
        # Scale to max points
        final_score = round(weighted_score * max_points, 2)
        
        # Determine overall assessment
        assessment = self._get_assessment(weighted_score)
        
        result = {
            "score": final_score,
            "max_score": max_points,
            "percentage": round(weighted_score * 100, 1),
            "overall_assessment": assessment,
            "method": "hybrid_ml",
            "weights_used": self.weights,
            "component_scores": {
                "tfidf": {
                    "score": tfidf_result['score'],
                    "weight": self.weights['tfidf'],
                    "weighted": round(tfidf_result['score'] * self.weights['tfidf'], 4)
                },
                "semantic": {
                    "score": semantic_result['score'],
                    "weight": self.weights['semantic'],
                    "weighted": round(semantic_result['score'] * self.weights['semantic'], 4)
                },
                "keyword": {
                    "score": keyword_result['score'],
                    "weight": self.weights['keyword'],
                    "weighted": round(keyword_result['score'] * self.weights['keyword'], 4),
                    "matched": keyword_result.get('matched_keywords', []),
                    "missed": keyword_result.get('missed_keywords', [])
                }
            },
            "feedback": self._generate_feedback(
                weighted_score, 
                tfidf_result, 
                semantic_result, 
                keyword_result
            )
        }
        
        # Optionally get LLM feedback for more detailed explanation
        if self.use_llm_fallback and llm_provider and weighted_score < 0.7:
            llm_feedback = self._get_llm_feedback(
                question, student_answer, correct_answer,
                result, llm_provider, llm_model
            )
            if llm_feedback:
                result["llm_feedback"] = llm_feedback
        
        return result
    
    def _get_assessment(self, score: float) -> str:
        """Get overall assessment category"""
        if score >= 0.9:
            return "excellent"
        elif score >= 0.75:
            return "good"
        elif score >= 0.6:
            return "satisfactory"
        elif score >= 0.4:
            return "needs_improvement"
        else:
            return "poor"
    
    def _generate_feedback(
        self,
        overall_score: float,
        tfidf: Dict,
        semantic: Dict,
        keyword: Dict
    ) -> str:
        """Generate comprehensive feedback based on all scores"""
        feedback_parts = []
        
        if overall_score >= 0.8:
            feedback_parts.append("✅ Excellent answer!")
        elif overall_score >= 0.6:
            feedback_parts.append("👍 Good answer with room for improvement.")
        elif overall_score >= 0.4:
            feedback_parts.append("⚠️ Partial understanding demonstrated.")
        else:
            feedback_parts.append("❌ Answer needs significant improvement.")
        
        # Add specific feedback based on component scores
        if semantic['score'] < 0.5:
            feedback_parts.append(
                "The meaning of your answer doesn't fully align with the expected response."
            )
        
        if keyword.get('missed_keywords'):
            missed = keyword['missed_keywords'][:3]
            feedback_parts.append(
                f"Consider including these concepts: {', '.join(missed)}"
            )
        
        if tfidf['score'] > semantic['score'] + 0.2:
            feedback_parts.append(
                "Your answer uses similar words but may miss the deeper meaning."
            )
        
        return " ".join(feedback_parts)
    
    def _get_llm_feedback(
        self,
        question: str,
        student_answer: str,
        correct_answer: str,
        ml_result: Dict,
        provider: str,
        model: str
    ) -> Optional[str]:
        """Get additional feedback from LLM for low-scoring answers"""
        try:
            from ai_services.llm_providers import get_llm_provider
            
            llm = get_llm_provider(provider, model)
            
            prompt = f"""A student answered this question:
Question: {question or 'N/A'}

Expected answer: {correct_answer}

Student's answer: {student_answer}

ML Score: {ml_result['percentage']}%

Provide brief, constructive feedback (2-3 sentences) on how the student can improve.
Focus on what's missing or incorrect. Be encouraging but specific."""
            
            return llm.generate(prompt)
        except Exception:
            return None


# Singleton instances
_hybrid_scorer = None
_text_scorer = None
_semantic_scorer = None
_keyword_scorer = None


def get_hybrid_scorer(weights: Dict = None) -> HybridScorer:
    """Get or create hybrid scorer singleton"""
    global _hybrid_scorer
    if _hybrid_scorer is None or weights:
        _hybrid_scorer = HybridScorer(weights=weights)
    return _hybrid_scorer


def get_text_scorer() -> TextSimilarityScorer:
    """Get or create TF-IDF scorer singleton"""
    global _text_scorer
    if _text_scorer is None:
        _text_scorer = TextSimilarityScorer()
    return _text_scorer


def get_semantic_scorer() -> SemanticSimilarityScorer:
    """Get or create semantic scorer singleton"""
    global _semantic_scorer
    if _semantic_scorer is None:
        _semantic_scorer = SemanticSimilarityScorer()
    return _semantic_scorer


def get_keyword_scorer() -> KeywordMatchScorer:
    """Get or create keyword scorer singleton"""
    global _keyword_scorer
    if _keyword_scorer is None:
        _keyword_scorer = KeywordMatchScorer()
    return _keyword_scorer
