import React, { useState, useEffect } from 'react';
import { studentAPI } from '../api';
import './Quiz.css';

const QuizTaker = ({ courseId }) => {
    const [quizzes, setQuizzes] = useState([]);
    const [selectedQuiz, setSelectedQuiz] = useState(null);
    const [attempt, setAttempt] = useState(null);
    const [answers, setAnswers] = useState({});
    const [result, setResult] = useState(null);
    const [timeLeft, setTimeLeft] = useState(null);

    useEffect(() => {
        loadQuizzes();
    }, [courseId]);

    useEffect(() => {
        if (attempt && attempt.time_limit_minutes) {
            const timer = setInterval(() => {
                const elapsed = Math.floor((Date.now() - new Date(attempt.started_at)) / 1000 / 60);
                const remaining = attempt.time_limit_minutes - elapsed;
                setTimeLeft(Math.max(0, remaining));

                if (remaining <= 0) {
                    handleSubmit();
                }
            }, 1000);

            return () => clearInterval(timer);
        }
    }, [attempt]);

    const loadQuizzes = async () => {
        try {
            const { data } = await studentAPI.getQuizzes(courseId);
            setQuizzes(data);
        } catch (error) {
            console.error('Failed to load quizzes', error);
        }
    };

    const startQuiz = async (quizId) => {
        try {
            const { data } = await studentAPI.startQuiz(quizId);
            setAttempt(data);
            setAnswers({});
            setResult(null);
        } catch (error) {
            alert(error.response?.data?.detail || 'Failed to start quiz');
        }
    };

    const handleAnswerChange = (questionId, answer) => {
        setAnswers(prev => ({ ...prev, [questionId]: answer }));
    };

    const handleSubmit = async () => {
        if (!attempt) return;

        try {
            const { data } = await studentAPI.submitQuiz(attempt.attempt_id, answers);
            setResult(data);
            setAttempt(null);
        } catch (error) {
            alert('Failed to submit quiz');
        }
    };

    if (result) {
        return (
            <div className="quiz-container">
                <div className="quiz-result card">
                    <h2 className="result-title">Quiz Completed! 🎉</h2>

                    <div className="result-score">
                        <div className="score-circle">
                            <span className="score-value">{result.percentage.toFixed(0)}%</span>
                        </div>
                        <p className="score-text">
                            {result.score.toFixed(1)} / {result.max_score} points
                        </p>
                    </div>

                    <div className="xp-earned">
                        <span className="badge badge-yellow">+{result.xp_earned} XP Earned!</span>
                    </div>

                    <div className="result-details">
                        <h3>Question Results:</h3>
                        {result.results.map((q, idx) => (
                            <div key={idx} className="question-result">
                                <div className="question-header">
                                    <span className="question-number">Q{idx + 1}</span>
                                    <span className={`points ${q.points_earned === q.points_possible ? 'correct' : 'incorrect'}`}>
                                        {q.points_earned.toFixed(1)} / {q.points_possible} pts
                                    </span>
                                </div>
                                <p className="question-text">{q.question_text}</p>
                                <div className="answer-info">
                                    <p><strong>Your Answer:</strong> {q.student_answer}</p>
                                    <p><strong>Correct Answer:</strong> {q.correct_answer}</p>
                                    {q.feedback && <p className="feedback">{q.feedback}</p>}
                                    {q.explanation && <p className="explanation">💡 {q.explanation}</p>}
                                </div>
                            </div>
                        ))}
                    </div>

                    <button onClick={() => setResult(null)} className="btn btn-primary">
                        Back to Quizzes
                    </button>
                </div>
            </div>
        );
    }

    if (attempt) {
        return (
            <div className="quiz-container">
                <div className="quiz-taking card">
                    <div className="quiz-header">
                        <h2>{attempt.quiz_title}</h2>
                        {timeLeft !== null && (
                            <div className="timer">
                                ⏱️ {Math.floor(timeLeft)} min remaining
                            </div>
                        )}
                    </div>

                    <div className="quiz-questions">
                        {attempt.questions.map((question, idx) => (
                            <div key={question.id} className="question-card">
                                <div className="question-header">
                                    <span className="question-number">Question {idx + 1}</span>
                                    <span className="question-points">{question.points} pts</span>
                                </div>
                                <p className="question-text">{question.question_text}</p>

                                {question.question_type === 'mcq' && (
                                    <div className="options">
                                        {question.options.map((option, optIdx) => (
                                            <label key={optIdx} className="option">
                                                <input
                                                    type="radio"
                                                    name={`question-${question.id}`}
                                                    value={option}
                                                    checked={answers[question.id] === option}
                                                    onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                                                />
                                                <span>{option}</span>
                                            </label>
                                        ))}
                                    </div>
                                )}

                                {question.question_type === 'true_false' && (
                                    <div className="options">
                                        {['True', 'False'].map(option => (
                                            <label key={option} className="option">
                                                <input
                                                    type="radio"
                                                    name={`question-${question.id}`}
                                                    value={option}
                                                    checked={answers[question.id] === option}
                                                    onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                                                />
                                                <span>{option}</span>
                                            </label>
                                        ))}
                                    </div>
                                )}

                                {question.question_type === 'short_answer' && (
                                    <textarea
                                        className="input short-answer"
                                        rows="3"
                                        value={answers[question.id] || ''}
                                        onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                                        placeholder="Type your answer here..."
                                    />
                                )}
                            </div>
                        ))}
                    </div>

                    <button onClick={handleSubmit} className="btn btn-primary btn-full">
                        Submit Quiz
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="quiz-container">
            <h2 className="section-title">Available Quizzes</h2>
            <div className="quizzes-grid">
                {quizzes.map(quiz => (
                    <div key={quiz.id} className="quiz-card card">
                        <h3 className="quiz-title">{quiz.title}</h3>
                        <p className="quiz-description">{quiz.description}</p>

                        <div className="quiz-info">
                            <span>⏱️ {quiz.time_limit_minutes} min</span>
                            <span>🔄 {quiz.attempts_remaining} attempts left</span>
                        </div>

                        {quiz.best_score !== null && (
                            <div className="best-score">
                                Best Score: <span className="badge badge-yellow">{quiz.best_score.toFixed(1)}%</span>
                            </div>
                        )}

                        <button
                            onClick={() => startQuiz(quiz.id)}
                            className="btn btn-primary btn-full"
                            disabled={!quiz.can_attempt}
                        >
                            {quiz.can_attempt ? 'Start Quiz' : 'No Attempts Left'}
                        </button>
                    </div>
                ))}
            </div>

            {quizzes.length === 0 && (
                <p className="empty-state">No quizzes available for this course</p>
            )}
        </div>
    );
};

export default QuizTaker;
