import React, { useState, useEffect } from 'react';
import { teacherAPI } from '../api';
import './QuizGenerator.css';

const QuizGenerator = () => {
    const [courses, setCourses] = useState([]);
    const [chatbots, setChatbots] = useState([]);
    const [llmProviders, setLLMProviders] = useState({ providers: {}, models: {} });
    const [generationMode, setGenerationMode] = useState('topic'); // 'topic' or 'rag'
    const [formData, setFormData] = useState({
        courseId: '',
        chatbotId: '',
        topic: '',
        numQuestions: 5,
        difficulty: 'medium',
        llmProvider: 'gemini',
        llmModel: ''
    });
    const [generatedQuestions, setGeneratedQuestions] = useState([]);
    const [loading, setLoading] = useState(false);
    const [quizTitle, setQuizTitle] = useState('');
    const [saving, setSaving] = useState(false);
    const [ragInfo, setRagInfo] = useState(null);
    const [savedQuizId, setSavedQuizId] = useState(null); // Track saved quiz ID
    const [publishing, setPublishing] = useState(false);

    useEffect(() => {
        loadCourses();
        loadLLMProviders();
    }, []);

    useEffect(() => {
        if (formData.courseId) {
            loadCourseChatbots(formData.courseId);
        }
    }, [formData.courseId]);

    const loadCourses = async () => {
        try {
            const response = await teacherAPI.getCourses();
            setCourses(response.data);
        } catch (error) {
            console.error('Error loading courses:', error);
        }
    };

    const loadCourseChatbots = async (courseId) => {
        try {
            const response = await teacherAPI.getCourseChatbots(courseId);
            setChatbots(response.data);
        } catch (error) {
            console.error('Error loading chatbots:', error);
            setChatbots([]);
        }
    };

    const loadLLMProviders = async () => {
        try {
            const response = await teacherAPI.getLLMProviders();
            setLLMProviders(response.data);
        } catch (error) {
            console.error('Error loading LLM providers:', error);
        }
    };

    const handleGenerate = async (e) => {
        e.preventDefault();
        setLoading(true);
        setGeneratedQuestions([]);
        setRagInfo(null);
        setSavedQuizId(null);

        try {
            let response;

            if (generationMode === 'rag') {
                // Generate from RAG (course documents)
                response = await teacherAPI.generateQuizFromRAG(
                    formData.courseId,
                    formData.chatbotId,
                    formData.topic || null,
                    formData.numQuestions,
                    formData.difficulty,
                    formData.llmProvider
                );
                setRagInfo({
                    source: 'Course Documents',
                    chatbotUsed: response.data.chatbot_used,
                    chunksUsed: response.data.chunks_used
                });
                // For RAG mode quiz is auto-saved
                setSavedQuizId(response.data.quiz_id);
                setQuizTitle(response.data.quiz_title);
                setGeneratedQuestions([]); // Already saved
            } else {
                // Generate from topic
                response = await teacherAPI.generateQuiz(
                    formData.courseId,
                    formData.topic,
                    formData.numQuestions,
                    formData.difficulty,
                    formData.llmProvider,
                    formData.llmModel || null
                );
                setGeneratedQuestions(response.data.questions || []);
                setQuizTitle(response.data.title || `${formData.topic} Quiz`);
            }
        } catch (error) {
            console.error('Error generating quiz:', error);
            const errorMsg = error.response?.data?.detail || 'Failed to generate quiz. Please check your API configuration.';
            alert(errorMsg);
        } finally {
            setLoading(false);
        }
    };

    const handleSaveQuiz = async () => {
        if (!quizTitle.trim()) {
            alert('Please enter a quiz title');
            return;
        }

        setSaving(true);
        try {
            const quizData = {
                title: quizTitle,
                description: `AI-generated quiz on ${formData.topic}`,
                time_limit_minutes: Math.max(formData.numQuestions * 2, 15),
                max_attempts: 3,
                questions: generatedQuestions
            };

            const response = await teacherAPI.createQuiz(formData.courseId, quizData);
            setSavedQuizId(response.data.id);
            setGeneratedQuestions([]);
            alert('Quiz saved as draft! Use the Forward button to publish to students.');
        } catch (error) {
            console.error('Error saving quiz:', error);
            alert('Failed to save quiz: ' + (error.response?.data?.detail || 'Unknown error'));
        } finally {
            setSaving(false);
        }
    };

    const handlePublishQuiz = async () => {
        if (!savedQuizId) return;

        setPublishing(true);
        try {
            await teacherAPI.publishQuiz(savedQuizId);
            alert('Quiz published successfully! Students can now see it.');
            setSavedQuizId(null);
            setFormData({ ...formData, topic: '' });
        } catch (error) {
            console.error('Error publishing quiz:', error);
            alert('Failed to publish quiz: ' + (error.response?.data?.detail || 'Unknown error'));
        } finally {
            setPublishing(false);
        }
    };

    return (
        <div className="quiz-generator-page">
            <div className="generator-header">
                <h1>🎯 AI Quiz Generator</h1>
                <p>Generate quizzes using AI with multiple LLM providers</p>
            </div>

            <div className="generator-content">
                <div className="generator-form card">
                    <h2>Quiz Parameters</h2>

                    {/* Generation Mode Toggle */}
                    <div className="mode-toggle">
                        <button
                            type="button"
                            className={`mode-btn ${generationMode === 'topic' ? 'active' : ''}`}
                            onClick={() => setGenerationMode('topic')}
                        >
                            📝 From Topic
                        </button>
                        <button
                            type="button"
                            className={`mode-btn ${generationMode === 'rag' ? 'active' : ''}`}
                            onClick={() => setGenerationMode('rag')}
                        >
                            📚 From Course Documents (RAG)
                        </button>
                    </div>

                    {generationMode === 'rag' && (
                        <div className="rag-info-banner">
                            <span className="rag-badge">🔍 RAG Mode</span>
                            <p>Questions will be generated <strong>only from uploaded course documents</strong>.
                                This ensures quiz content aligns with your actual teaching materials.</p>
                        </div>
                    )}

                    <form onSubmit={handleGenerate}>
                        <div className="form-group">
                            <label>Course *</label>
                            <select
                                value={formData.courseId}
                                onChange={(e) => setFormData({ ...formData, courseId: e.target.value, chatbotId: '' })}
                                required
                            >
                                <option value="">Select a course...</option>
                                {courses.map(course => (
                                    <option key={course.id} value={course.id}>
                                        {course.name}
                                    </option>
                                ))}
                            </select>
                        </div>

                        {generationMode === 'rag' && (
                            <div className="form-group">
                                <label>Knowledge Base (Chatbot) *</label>
                                <select
                                    value={formData.chatbotId}
                                    onChange={(e) => setFormData({ ...formData, chatbotId: e.target.value })}
                                    required
                                >
                                    <option value="">Select chatbot with documents...</option>
                                    {chatbots.map(bot => (
                                        <option key={bot.id} value={bot.id}>
                                            {bot.name} {bot.document_count > 0 ? `(${bot.document_count} docs)` : '(no documents)'}
                                        </option>
                                    ))}
                                </select>

                                {formData.chatbotId && (
                                    <div className="upload-helper" style={{ marginTop: '10px', fontSize: '0.9em' }}>
                                        <label style={{ cursor: 'pointer', color: '#ffd700', display: 'inline-flex', alignItems: 'center', gap: '5px' }}>
                                            <span className="icon">📂</span> Upload Document to this Chatbot
                                            <input
                                                type="file"
                                                accept=".pdf,.txt"
                                                style={{ display: 'none' }}
                                                onChange={async (e) => {
                                                    const file = e.target.files[0];
                                                    if (!file) return;
                                                    try {
                                                        await teacherAPI.uploadDocument(formData.chatbotId, file);
                                                        alert(`File "${file.name}" uploaded! It is processing...`);
                                                    } catch (error) {
                                                        alert('Upload failed: ' + (error.response?.data?.detail || error.message));
                                                    }
                                                }}
                                            />
                                        </label>
                                    </div>
                                )}

                                {chatbots.length === 0 && formData.courseId && (
                                    <p className="help-text">No chatbots found. Create a chatbot and upload documents first.</p>
                                )}
                            </div>
                        )}

                        <div className="form-group">
                            <label>{generationMode === 'rag' ? 'Focus Topic (optional)' : 'Topic *'}</label>
                            <input
                                type="text"
                                value={formData.topic}
                                onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
                                placeholder={generationMode === 'rag'
                                    ? "e.g., Real Numbers, Quadratic Equations (or leave empty for all topics)"
                                    : "e.g., Quadratic Equations, Python Functions"
                                }
                                required={generationMode === 'topic'}
                            />
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label>Number of Questions</label>
                                <input
                                    type="number"
                                    value={formData.numQuestions}
                                    onChange={(e) => setFormData({ ...formData, numQuestions: parseInt(e.target.value) })}
                                    min="1"
                                    max="20"
                                />
                            </div>

                            <div className="form-group">
                                <label>Difficulty</label>
                                <select
                                    value={formData.difficulty}
                                    onChange={(e) => setFormData({ ...formData, difficulty: e.target.value })}
                                >
                                    <option value="easy">Easy</option>
                                    <option value="medium">Medium</option>
                                    <option value="hard">Hard</option>
                                </select>
                            </div>
                        </div>

                        {/* LLM Provider Selection */}
                        <div className="form-row">
                            <div className="form-group">
                                <label>AI Provider</label>
                                <select
                                    value={formData.llmProvider}
                                    onChange={(e) => setFormData({ ...formData, llmProvider: e.target.value, llmModel: '' })}
                                >
                                    {Object.entries(llmProviders.providers || {}).map(([name, available]) => (
                                        <option key={name} value={name} disabled={!available}>
                                            {name.charAt(0).toUpperCase() + name.slice(1)} {!available && '(not configured)'}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div className="form-group">
                                <label>Model (optional)</label>
                                <select
                                    value={formData.llmModel}
                                    onChange={(e) => setFormData({ ...formData, llmModel: e.target.value })}
                                >
                                    <option value="">Default</option>
                                    {(llmProviders.models?.[formData.llmProvider] || []).map(model => (
                                        <option key={model} value={model}>{model}</option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        <button
                            type="submit"
                            className="btn btn-primary btn-large"
                            disabled={loading || (generationMode === 'rag' && !formData.chatbotId)}
                        >
                            {loading ? '⏳ Generating...' : generationMode === 'rag' ? '📚 Generate from Documents' : '✨ Generate Quiz'}
                        </button>
                    </form>
                </div>

                {(ragInfo || savedQuizId) && (
                    <div className="success-card card">
                        {ragInfo && (
                            <>
                                <h3>Generation Complete</h3>
                                <p><strong>Source:</strong> {ragInfo.source}</p>
                                <p><strong>Chatbot Used:</strong> {ragInfo.chatbotUsed}</p>
                                <p><strong>Document Chunks Used:</strong> {ragInfo.chunksUsed}</p>
                            </>
                        )}

                        {savedQuizId && (
                            <>
                                <div className="quiz-status">
                                    <h3>Quiz Saved</h3>
                                    <span className="badge badge-draft">Draft</span>
                                </div>
                                <p><strong>Title:</strong> {quizTitle}</p>
                                <p className="help-text">Quiz is saved as a draft. Students cannot see it yet.</p>
                                <button
                                    onClick={handlePublishQuiz}
                                    className="btn btn-success btn-large"
                                    disabled={publishing}
                                >
                                    {publishing ? 'Publishing...' : 'Forward to Students'}
                                </button>
                            </>
                        )}
                    </div>
                )}

                {generatedQuestions.length > 0 && (
                    <div className="generated-questions card">
                        <div className="questions-header">
                            <h2>Generated Questions ({generatedQuestions.length})</h2>
                            <div className="save-section">
                                <input
                                    type="text"
                                    value={quizTitle}
                                    onChange={(e) => setQuizTitle(e.target.value)}
                                    placeholder="Enter quiz title..."
                                    className="title-input"
                                />
                                <button
                                    onClick={handleSaveQuiz}
                                    className="btn btn-primary"
                                    disabled={saving}
                                >
                                    {saving ? '⏳ Saving...' : '💾 Save Quiz'}
                                </button>
                            </div>
                        </div>

                        <div className="questions-list">
                            {generatedQuestions.map((q, index) => (
                                <div key={index} className="question-card">
                                    <div className="question-header">
                                        <span className="question-number">Q{index + 1}</span>
                                        <span className={`question-type ${q.question_type}`}>
                                            {q.question_type === 'mcq' ? 'Multiple Choice' :
                                                q.question_type === 'true_false' ? 'True/False' :
                                                    'Short Answer'}
                                        </span>
                                        <span className="question-points">{q.points || 10} pts</span>
                                    </div>

                                    <div className="question-text">{q.question_text}</div>

                                    {q.question_type === 'mcq' && q.options && (
                                        <div className="question-options">
                                            {(typeof q.options === 'string' ? JSON.parse(q.options) : q.options).map((opt, i) => (
                                                <div
                                                    key={i}
                                                    className={`option ${opt === q.correct_answer ? 'correct' : ''}`}
                                                >
                                                    <span className="option-label">{String.fromCharCode(65 + i)}.</span>
                                                    {opt}
                                                    {opt === q.correct_answer && <span className="correct-icon">✓</span>}
                                                </div>
                                            ))}
                                        </div>
                                    )}

                                    {q.question_type === 'true_false' && (
                                        <div className="question-options">
                                            <div className={`option ${q.correct_answer === 'True' ? 'correct' : ''}`}>
                                                True {q.correct_answer === 'True' && <span className="correct-icon">✓</span>}
                                            </div>
                                            <div className={`option ${q.correct_answer === 'False' ? 'correct' : ''}`}>
                                                False {q.correct_answer === 'False' && <span className="correct-icon">✓</span>}
                                            </div>
                                        </div>
                                    )}

                                    {q.question_type === 'short_answer' && (
                                        <div className="correct-answer">
                                            <strong>Expected Answer:</strong> {q.correct_answer}
                                        </div>
                                    )}

                                    {q.explanation && (
                                        <div className="question-explanation">
                                            <strong>📝 Explanation:</strong> {q.explanation}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {loading && (
                    <div className="loading-state card">
                        <div className="loading-spinner">⏳</div>
                        <p>Generating quiz with {formData.llmProvider.charAt(0).toUpperCase() + formData.llmProvider.slice(1)} AI...</p>
                        <p className="loading-subtitle">
                            {generationMode === 'rag'
                                ? 'Retrieving content from course documents...'
                                : 'This may take a few moments'}
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default QuizGenerator;
