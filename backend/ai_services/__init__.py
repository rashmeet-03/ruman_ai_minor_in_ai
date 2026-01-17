# AI Services package
from .rag_system import RAGSystem, get_rag_system
from .ml_models import (
    PerformancePredictor,
    LearningGapAnalyzer,
    AdaptiveDifficultySelector,
    get_performance_predictor,
    get_learning_gap_analyzer,
    get_difficulty_selector
)
from .ai_assessment import (
    QuizGenerator,
    AnswerEvaluator,
    get_quiz_generator,
    get_answer_evaluator
)
from .ml_scoring import (
    TextSimilarityScorer,
    SemanticSimilarityScorer,
    KeywordMatchScorer,
    HybridScorer,
    get_hybrid_scorer,
    get_text_scorer,
    get_semantic_scorer,
    get_keyword_scorer
)
from .llm_providers import (
    LLMProvider,
    GeminiProvider,
    MistralProvider,
    get_llm_provider,
    get_available_providers,
    get_all_models
)

__all__ = [
    # RAG
    'RAGSystem',
    'get_rag_system',
    # ML Models
    'PerformancePredictor',
    'LearningGapAnalyzer',
    'AdaptiveDifficultySelector',
    'get_performance_predictor',
    'get_learning_gap_analyzer',
    'get_difficulty_selector',
    # Assessment
    'QuizGenerator',
    'AnswerEvaluator',
    'get_quiz_generator',
    'get_answer_evaluator',
    # ML Scoring
    'TextSimilarityScorer',
    'SemanticSimilarityScorer',
    'KeywordMatchScorer',
    'HybridScorer',
    'get_hybrid_scorer',
    'get_text_scorer',
    'get_semantic_scorer',
    'get_keyword_scorer',
    # LLM Providers
    'LLMProvider',
    'GeminiProvider',
    'MistralProvider',
    'get_llm_provider',
    'get_available_providers',
    'get_all_models',
]
