# ML Models
"""
ML Models for Student Performance Prediction and Learning Gap Analysis
Uses scikit-learn for traditional ML algorithms
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from typing import List, Dict, Tuple
import joblib
import os


class PerformancePredictor:
    """
    Predict student performance and identify at-risk students
    Uses Random Forest Classifier
    """
    
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    
    def prepare_features(self, student_data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare features from student data
        
        Features:
        - Average quiz score
        - Average assignment score
        - Number of quizzes attempted
        - Number of assignments submitted
        - Days since enrollment
        - Engagement score (activity frequency)
        
        Returns:
            X: Feature matrix, y: Labels (0=low-risk, 1=medium-risk, 2=high-risk)
        """
        features = []
        labels = []
        
        for student in student_data:
            feature_vec = [
                student.get('quiz_average', 0),
                student.get('assignment_average', 0),
                student.get('quizzes_attempted', 0),
                student.get('assignments_submitted', 0),
                student.get('days_since_enrollment', 0),
                student.get('engagement_score', 0)
            ]
            features.append(feature_vec)
            
            # Determine risk level based on overall average
            overall_avg = student.get('overall_average', 0)
            if overall_avg >= 70:
                labels.append(0)  # Low risk
            elif overall_avg >= 50:
                labels.append(1)  # Medium risk
            else:
                labels.append(2)  # High risk
        
        X = np.array(features)
        y = np.array(labels)
        
        return X, y
    
    
    def train(self, student_data: List[Dict]):
        """
        Train the performance prediction model
        
        Args:
            student_data: List of student dictionaries with performance metrics
        """
        X, y = self.prepare_features(student_data)
        
        if len(X) < 5:
            # Not enough data to train
            return False
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        return True
    
    
    def predict_risk(self, student_features: Dict) -> Dict:
        """
        Predict risk level for a student
        
        Args:
            student_features: Dictionary with student performance metrics
            
        Returns:
            Dict with risk level and confidence
        """
        if not self.is_trained:
            return {
                "risk_level": "unknown",
                "confidence": 0.0,
                "message": "Model not trained yet. Need more data."
            }
        
        # Prepare feature vector
        feature_vec = [[
            student_features.get('quiz_average', 0),
            student_features.get('assignment_average', 0),
            student_features.get('quizzes_attempted', 0),
            student_features.get('assignments_submitted', 0),
            student_features.get('days_since_enrollment', 0),
            student_features.get('engagement_score', 0)
        ]]
        
        # Scale and predict
        X_scaled = self.scaler.transform(feature_vec)
        prediction = self.model.predict(X_scaled)[0]
        probabilities = self.model.predict_proba(X_scaled)[0]
        
        risk_labels = {0: "low", 1: "medium", 2: "high"}
        
        return {
            "risk_level": risk_labels[prediction],
            "confidence": float(probabilities[prediction]),
            "probabilities": {
                "low": float(probabilities[0]),
                "medium": float(probabilities[1]),
                "high": float(probabilities[2])
            },
            "prediction": int(prediction)
        }


class LearningGapAnalyzer:
    """
    Identify learning gaps and weak topics across students
    Uses K-Means clustering to group students by performance patterns
    """
    
    def __init__(self, n_clusters: int = 3):
        self.n_clusters = n_clusters
        self.model = KMeans(n_clusters=n_clusters, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    
    def analyze_topic_performance(
        self,
        topic_scores: Dict[str, List[float]]
    ) -> Dict:
        """
        Analyze which topics are most challenging
        
        Args:
            topic_scores: Dict mapping topic names to list of student scores
            
        Returns:
            Dict with weak topics and statistics
        """
        weak_topics = []
        
        for topic, scores in topic_scores.items():
            if not scores:
                continue
            
            avg_score = np.mean(scores)
            std_score = np.std(scores)
            
            weak_topics.append({
                "topic": topic,
                "average_score": round(avg_score, 2),
                "std_deviation": round(std_score, 2),
                "num_students": len(scores),
                "difficulty_level": self._get_difficulty_level(avg_score)
            })
        
        # Sort by average score (ascending)
        weak_topics.sort(key=lambda x: x["average_score"])
        
        return {
            "weak_topics": weak_topics[:5],  # Top 5 weakest topics
            "analysis": self._generate_recommendations(weak_topics)
        }
    
    
    def _get_difficulty_level(self, avg_score: float) -> str:
        """Classify difficulty based on average score"""
        if avg_score >= 80:
            return "easy"
        elif avg_score >= 60:
            return "moderate"
        elif avg_score >= 40:
            return "challenging"
        else:
            return "very_challenging"
    
    
    def _generate_recommendations(self, topics: List[Dict]) -> List[str]:
        """Generate teaching recommendations"""
        recommendations = []
        
        for topic in topics[:3]:  # Top 3 weakest
            if topic["average_score"] < 50:
                recommendations.append(
                    f"📚 Focus on '{topic['topic']}' - students averaging {topic['average_score']}%"
                )
            elif topic["std_deviation"] > 20:
                recommendations.append(
                    f"⚖️ High variance in '{topic['topic']}' - consider personalized instruction"
                )
        
        return recommendations
    
    
    def cluster_students(
        self,
        student_performance: List[Dict]
    ) -> Dict:
        """
        Group students by performance patterns
        
        Args:
            student_performance: List of student performance dictionaries
            
        Returns:
            Dict with cluster assignments and characteristics
        """
        if len(student_performance) < self.n_clusters:
            return {
                "message": "Not enough students for clustering",
                "clusters": []
            }
        
        # Extract features for clustering
        features = []
        student_ids = []
        
        for student in student_performance:
            features.append([
                student.get('quiz_average', 0),
                student.get('assignment_average', 0),
                student.get('quizzes_attempted', 0),
                student.get('assignments_submitted', 0)
            ])
            student_ids.append(student.get('student_id'))
        
        X = np.array(features)
        X_scaled = self.scaler.fit_transform(X)
        
        # Perform clustering
        cluster_labels = self.model.fit_predict(X_scaled)
        
        # Analyze clusters
        clusters = []
        for cluster_id in range(self.n_clusters):
            cluster_students = [
                student_ids[i]
                for i, label in enumerate(cluster_labels)
                if label == cluster_id
            ]
            
            cluster_features = X[cluster_labels == cluster_id]
            
            if len(cluster_features) > 0:
                clusters.append({
                    "cluster_id": cluster_id,
                    "student_count": len(cluster_students),
                    "student_ids": cluster_students,
                    "characteristics": {
                        "avg_quiz_score": round(np.mean(cluster_features[:, 0]), 2),
                        "avg_assignment_score": round(np.mean(cluster_features[:, 1]), 2),
                        "avg_quizzes_attempted": round(np.mean(cluster_features[:, 2]), 2),
                        "avg_assignments_submitted": round(np.mean(cluster_features[:, 3]), 2)
                    },
                    "performance_tier": self._classify_cluster(np.mean(cluster_features[:, :2]))
                })
        
        return {
            "num_clusters": self.n_clusters,
            "clusters": clusters
        }
    
    
    def _classify_cluster(self, avg_score: float) -> str:
        """Classify cluster as high/medium/low performers"""
        if avg_score >= 75:
            return "high_performers"
        elif avg_score >= 50:
            return "medium_performers"
        else:
            return "struggling_students"


class AdaptiveDifficultySelector:
    """
    Use ML to select appropriate question difficulty based on student history
    
    Uses RandomForestRegressor to predict optimal difficulty level that:
    - Challenges the student appropriately
    - Maintains engagement (not too easy, not too hard)
    - Adapts based on recent performance trends
    """
    
    def __init__(self):
        from sklearn.ensemble import RandomForestRegressor
        self.model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.difficulty_mapping = {0: "easy", 1: "medium", 2: "hard"}
    
    def prepare_features(self, student_history: Dict) -> np.ndarray:
        """
        Extract features from student performance history
        
        Features:
        - Recent quiz average (last 5)
        - Overall quiz average
        - Quiz score trend (improving/declining)
        - Number of quizzes taken
        - Time since last quiz (days)
        - Assignment performance
        """
        recent_scores = student_history.get('recent_quiz_scores', [])
        all_scores = student_history.get('all_quiz_scores', [])
        
        # Calculate recent average (last 5 quizzes)
        recent_avg = np.mean(recent_scores[-5:]) if recent_scores else 50.0
        
        # Calculate overall average
        overall_avg = np.mean(all_scores) if all_scores else 50.0
        
        # Calculate trend (positive = improving)
        if len(recent_scores) >= 3:
            first_half = np.mean(recent_scores[:len(recent_scores)//2])
            second_half = np.mean(recent_scores[len(recent_scores)//2:])
            trend = second_half - first_half
        else:
            trend = 0.0
        
        # Other features
        num_quizzes = len(all_scores)
        days_since_last = student_history.get('days_since_last_quiz', 0)
        assignment_avg = student_history.get('assignment_average', 50.0)
        
        return np.array([[
            recent_avg,
            overall_avg,
            trend,
            min(num_quizzes, 50),  # Cap at 50
            min(days_since_last, 30),  # Cap at 30 days
            assignment_avg
        ]])
    
    def train(self, training_data: List[Dict]):
        """
        Train the difficulty selector
        
        Args:
            training_data: List of dicts with 'features' and 'optimal_difficulty'
        """
        if len(training_data) < 10:
            return False
        
        X = []
        y = []
        
        for record in training_data:
            features = self.prepare_features(record['history'])
            X.append(features[0])
            
            # Map difficulty to numeric
            diff_map = {"easy": 0, "medium": 1, "hard": 2}
            y.append(diff_map.get(record['optimal_difficulty'], 1))
        
        X = np.array(X)
        y = np.array(y)
        
        # Scale and train
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        return True
    
    def predict_optimal_difficulty(self, student_history: Dict) -> Dict:
        """
        Predict the optimal difficulty for next quiz
        
        Args:
            student_history: Dict with student's performance metrics
            
        Returns:
            Dict with recommended difficulty and reasoning
        """
        features = self.prepare_features(student_history)
        
        # If model is trained, use ML prediction
        if self.is_trained:
            X_scaled = self.scaler.transform(features)
            prediction = self.model.predict(X_scaled)[0]
            
            # Round to nearest difficulty level
            difficulty_index = int(round(max(0, min(2, prediction))))
            confidence = 1.0 - abs(prediction - difficulty_index)
            
            return {
                "difficulty": self.difficulty_mapping[difficulty_index],
                "confidence": round(float(confidence), 2),
                "method": "ml_prediction",
                "reasoning": self._get_reasoning(features[0], difficulty_index)
            }
        
        # Fallback: Use rule-based selection
        return self._rule_based_selection(features[0], student_history)
    
    def _rule_based_selection(self, features: np.ndarray, history: Dict) -> Dict:
        """Rule-based fallback when model isn't trained"""
        recent_avg = features[0]
        trend = features[2]
        
        # Simple rules based on performance
        if recent_avg >= 85:
            if trend >= 5:
                difficulty = "hard"
                reason = "Excellent recent performance with improving trend"
            else:
                difficulty = "hard"
                reason = "Consistently high scores - ready for challenge"
        elif recent_avg >= 70:
            if trend >= 0:
                difficulty = "medium"
                reason = "Good performance - maintaining current level"
            else:
                difficulty = "medium"  # Don't drop too fast
                reason = "Good scores but slight decline - reinforcing current level"
        elif recent_avg >= 50:
            if trend >= 5:
                difficulty = "medium"
                reason = "Improving trend - stepping up difficulty"
            else:
                difficulty = "easy"
                reason = "Moderate scores - building confidence with easier questions"
        else:
            difficulty = "easy"
            reason = "Focus on fundamentals before increasing difficulty"
        
        return {
            "difficulty": difficulty,
            "confidence": 0.7,  # Lower confidence for rule-based
            "method": "rule_based",
            "reasoning": reason,
            "stats": {
                "recent_average": round(float(recent_avg), 1),
                "trend": round(float(trend), 1)
            }
        }
    
    def _get_reasoning(self, features: np.ndarray, difficulty_index: int) -> str:
        """Generate human-readable reasoning for the prediction"""
        recent_avg = features[0]
        trend = features[2]
        difficulty = self.difficulty_mapping[difficulty_index]
        
        parts = [f"Based on recent average of {recent_avg:.1f}%"]
        
        if trend > 5:
            parts.append("with improving trend")
        elif trend < -5:
            parts.append("with declining trend")
        
        parts.append(f"→ recommended: {difficulty}")
        
        return " ".join(parts)


# Global instances
_performance_predictor = None
_learning_gap_analyzer = None
_difficulty_selector = None


def get_performance_predictor() -> PerformancePredictor:
    """Get or create performance predictor singleton"""
    global _performance_predictor
    if _performance_predictor is None:
        _performance_predictor = PerformancePredictor()
    return _performance_predictor


def get_learning_gap_analyzer() -> LearningGapAnalyzer:
    """Get or create learning gap analyzer singleton"""
    global _learning_gap_analyzer
    if _learning_gap_analyzer is None:
        _learning_gap_analyzer = LearningGapAnalyzer()
    return _learning_gap_analyzer


def get_difficulty_selector() -> AdaptiveDifficultySelector:
    """Get or create difficulty selector singleton"""
    global _difficulty_selector
    if _difficulty_selector is None:
        _difficulty_selector = AdaptiveDifficultySelector()
    return _difficulty_selector