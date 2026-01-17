import axios from 'axios';

const API_BASE_URL = '/api';

// Create axios instance
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add token to requests
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// API Methods
export const authAPI = {
    login: (username, password) =>
        api.post('/auth/login', new URLSearchParams({ username, password }), {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        }),
    register: (data) => api.post('/auth/register', data),
    getCurrentUser: () => api.get('/auth/me'),
};

export const studentAPI = {
    getDashboard: () => api.get('/student/dashboard'),
    getCourses: () => api.get('/student/courses'),
    enrollCourse: (courseId) => api.post(`/student/courses/${courseId}/enroll`),

    getQuizzes: (courseId) => api.get(`/student/courses/${courseId}/quizzes`),
    startQuiz: (quizId) => api.post(`/student/quizzes/${quizId}/attempt`),
    submitQuiz: (attemptId, answers) => api.post(`/student/quiz-attempts/${attemptId}/submit`, { answers }),

    getChatbots: (courseId) => api.get(`/student/courses/${courseId}/chatbots`),
    queryChatbot: (chatbotId, question) =>
        api.post(`/student/chatbots/${chatbotId}/query?question=${encodeURIComponent(question)}`),
    getChatHistory: (chatbotId) => api.get(`/student/chatbots/${chatbotId}/history`),
    clearChatHistory: (chatbotId) => api.delete(`/student/chatbots/${chatbotId}/history`),

    getAssignments: (courseId) => api.get(`/student/courses/${courseId}/assignments`),
    submitAssignment: (assignmentId, formData) =>
        api.post(`/student/assignments/${assignmentId}/submit`, formData),

    getProgress: () => api.get('/student/progress'),
    getAchievements: () => api.get('/student/achievements'),
};

export const teacherAPI = {
    getCourses: () => api.get('/teacher/courses'),
    createCourse: (data) => api.post('/teacher/courses', data),
    getCourse: (courseId) => api.get(`/teacher/courses/${courseId}`),
    updateCourse: (courseId, data) => api.put(`/teacher/courses/${courseId}`, data),
    deleteCourse: (courseId) => api.delete(`/teacher/courses/${courseId}`),

    getStudents: (courseId) => api.get(`/teacher/courses/${courseId}/students`),
    enrollStudent: (courseId, studentId) => api.post(`/teacher/courses/${courseId}/enroll/${studentId}`),

    // Chatbot Management
    createChatbot: (courseId, data) => api.post(`/teacher/courses/${courseId}/chatbots`, data),
    getChatbot: (chatbotId) => api.get(`/teacher/chatbots/${chatbotId}`),
    getChatbots: () => api.get('/teacher/chatbots'),
    getCourseChatbots: (courseId) => api.get(`/teacher/courses/${courseId}/chatbots`),
    updateChatbot: (chatbotId, data) => api.put(`/teacher/chatbots/${chatbotId}`, null, { params: data }),
    deleteChatbot: (chatbotId) => api.delete(`/teacher/chatbots/${chatbotId}`),
    publishChatbot: (chatbotId) => api.post(`/teacher/chatbots/${chatbotId}/publish`),
    unpublishChatbot: (chatbotId) => api.post(`/teacher/chatbots/${chatbotId}/unpublish`),
    testChatbot: (chatbotId, question) => api.post(`/teacher/chatbots/${chatbotId}/test?question=${encodeURIComponent(question)}`),
    getTestChatHistory: (chatbotId) => api.get(`/teacher/chatbots/${chatbotId}/test-history`),

    // Chatbot Course Assignment
    assignChatbotToCourse: (chatbotId, courseId) => api.post(`/teacher/chatbots/${chatbotId}/assign/${courseId}`),
    unassignChatbotFromCourse: (chatbotId, courseId) => api.delete(`/teacher/chatbots/${chatbotId}/unassign/${courseId}`),

    // Knowledge Base Documents
    uploadDocument: (chatbotId, file) => {
        const formData = new FormData();
        formData.append('file', file);
        return api.post(`/teacher/chatbots/${chatbotId}/upload`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
    },
    getDocuments: (chatbotId) => api.get(`/teacher/chatbots/${chatbotId}/documents`),
    deleteDocument: (chatbotId, documentId) => api.delete(`/teacher/chatbots/${chatbotId}/documents/${documentId}`),
    processDocuments: (chatbotId) => api.post(`/teacher/chatbots/${chatbotId}/process-documents`),

    // Quiz Management
    createQuiz: (courseId, data) => api.post(`/teacher/courses/${courseId}/quizzes`, data),
    getQuiz: (quizId) => api.get(`/teacher/quizzes/${quizId}`),
    publishQuiz: (quizId) => api.post(`/teacher/quizzes/${quizId}/publish`),
    unpublishQuiz: (quizId) => api.post(`/teacher/quizzes/${quizId}/unpublish`),
    generateQuiz: (courseId, topic, numQuestions, difficulty, llmProvider = 'gemini', llmModel = null) =>
        api.post(`/teacher/quizzes/generate?course_id=${courseId}&topic=${encodeURIComponent(topic)}&num_questions=${numQuestions}&difficulty=${difficulty}&llm_provider=${llmProvider}${llmModel ? `&llm_model=${llmModel}` : ''}`),

    // RAG-Based Quiz Generation (from course documents)
    generateQuizFromRAG: (courseId, chatbotId, topic, numQuestions, difficulty, llmProvider = 'gemini', llmModel = null) =>
        api.post(`/teacher/quizzes/generate-from-rag?course_id=${courseId}&chatbot_id=${chatbotId}${topic ? `&topic=${encodeURIComponent(topic)}` : ''}&num_questions=${numQuestions}&difficulty=${difficulty}&llm_provider=${llmProvider}${llmModel ? `&llm_model=${llmModel}` : ''}`),

    // RAG-Based Assignment Generation (from course documents)
    generateAssignmentFromRAG: (courseId, chatbotId, topic, maxScore = 100, numQuestions = 5, llmProvider = 'gemini', llmModel = null) =>
        api.post(`/teacher/assignments/generate-from-rag?course_id=${courseId}&chatbot_id=${chatbotId}${topic ? `&topic=${encodeURIComponent(topic)}` : ''}&max_score=${maxScore}&num_questions=${numQuestions}&llm_provider=${llmProvider}${llmModel ? `&llm_model=${llmModel}` : ''}`),

    // Assignment Management
    createAssignment: (courseId, data) => api.post(`/teacher/courses/${courseId}/assignments`, data),
    getAssignment: (assignmentId) => api.get(`/teacher/assignments/${assignmentId}`),
    publishAssignment: (assignmentId) => api.post(`/teacher/assignments/${assignmentId}/publish`),
    unpublishAssignment: (assignmentId) => api.post(`/teacher/assignments/${assignmentId}/unpublish`),
    getSubmissions: (assignmentId) => api.get(`/teacher/assignments/${assignmentId}/submissions`),
    gradeSubmission: (submissionId, score, feedback) =>
        api.put(`/teacher/submissions/${submissionId}/grade?score=${score}&feedback=${encodeURIComponent(feedback || '')}`),

    // Analytics
    getAnalytics: (courseId) => api.get(`/teacher/courses/${courseId}/analytics`),

    // AI/ML Features
    getLLMProviders: () => api.get('/teacher/ai/llm-providers'),
    predictDifficulty: (studentId, courseId) =>
        api.post(`/teacher/ai/predict-difficulty?student_id=${studentId}&course_id=${courseId}`),
    evaluateAnswer: (question, studentAnswer, correctAnswer, maxPoints = 1.0, useLLMFeedback = true, llmProvider = 'gemini') =>
        api.post(`/teacher/ai/evaluate-answer?question=${encodeURIComponent(question)}&student_answer=${encodeURIComponent(studentAnswer)}&correct_answer=${encodeURIComponent(correctAnswer)}&max_points=${maxPoints}&use_llm_feedback=${useLLMFeedback}&llm_provider=${llmProvider}`),
    mlScoringDemo: (studentAnswer, correctAnswer) =>
        api.get(`/teacher/ai/ml-scoring-demo?student_answer=${encodeURIComponent(studentAnswer)}&correct_answer=${encodeURIComponent(correctAnswer)}`),
};

export default api;
