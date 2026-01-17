import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { teacherAPI } from '../api';
import './TeacherDashboard.css';

const TeacherDashboard = () => {
    const [courses, setCourses] = useState([]);
    const [selectedCourse, setSelectedCourse] = useState(null);
    const [activeTab, setActiveTab] = useState('overview');
    const [loading, setLoading] = useState(true);
    const [analytics, setAnalytics] = useState(null);
    const [showAllChatbots, setShowAllChatbots] = useState(false);

    // Form states
    const [showChatbotForm, setShowChatbotForm] = useState(false);
    const [showQuizForm, setShowQuizForm] = useState(false);
    const [showAssignmentForm, setShowAssignmentForm] = useState(false);

    const [chatbotForm, setChatbotForm] = useState({
        name: '',
        description: '',
        system_prompt: '',
        llm_provider: 'mistral',
        llm_model: 'mistral-small-latest'
    });
    const [assignmentForm, setAssignmentForm] = useState({ title: '', description: '', max_score: 100, due_date: '' });

    // Handler to update model when provider changes
    const handleProviderChange = (provider) => {
        const defaultModel = provider === 'mistral' ? 'mistral-small-latest' : 'gemini-2.0-flash';
        setChatbotForm({ ...chatbotForm, llm_provider: provider, llm_model: defaultModel });
    };

    // Get all chatbots from all courses
    const getAllChatbots = () => {
        const allBots = [];
        const seenIds = new Set();
        courses.forEach(course => {
            course.chatbots?.forEach(bot => {
                if (!seenIds.has(bot.id)) {
                    seenIds.add(bot.id);
                    allBots.push(bot);
                }
            });
        });
        return allBots;
    };

    useEffect(() => {
        loadCourses();
    }, []);


    useEffect(() => {
        if (selectedCourse) {
            loadAnalytics(selectedCourse.id);
        }
    }, [selectedCourse]);

    const loadCourses = async () => {
        try {
            const response = await teacherAPI.getCourses();
            setCourses(response.data);
            if (response.data.length > 0) {
                setSelectedCourse(response.data[0]);
            }
        } catch (error) {
            console.error('Error loading courses:', error);
        } finally {
            setLoading(false);
        }
    };

    const loadAnalytics = async (courseId) => {
        try {
            const response = await teacherAPI.getAnalytics(courseId);
            setAnalytics(response.data);
        } catch (error) {
            console.error('Error loading analytics:', error);
        }
    };

    const handleCreateChatbot = async (e) => {
        e.preventDefault();
        const courseId = chatbotForm.target_course_id || selectedCourse?.id;
        if (!courseId) {
            alert('Please select a course');
            return;
        }
        try {
            await teacherAPI.createChatbot(courseId, chatbotForm);
            alert('Chatbot created successfully!');
            setShowChatbotForm(false);
            setChatbotForm({ name: '', description: '', system_prompt: '', llm_provider: 'mistral', llm_model: 'mistral-small-latest' });
            loadCourses();
        } catch (error) {
            alert('Error: ' + (error.response?.data?.detail || 'Failed to create chatbot'));
        }
    };

    const handleCreateAssignment = async (e) => {
        e.preventDefault();
        try {
            await teacherAPI.createAssignment(selectedCourse.id, assignmentForm);
            alert('Assignment created successfully!');
            setShowAssignmentForm(false);
            setAssignmentForm({ title: '', description: '', max_score: 100, due_date: '' });
            loadCourses();
        } catch (error) {
            alert('Error: ' + (error.response?.data?.detail || 'Failed to create assignment'));
        }
    };

    const handleFileUpload = async (chatbotId, e) => {
        const file = e.target.files[0];
        if (!file) return;
        try {
            await teacherAPI.uploadDocument(chatbotId, file);
            await teacherAPI.processDocuments(chatbotId);
            alert('Document uploaded and embedded successfully! 📄✨');
            return true;
        } catch (error) {
            alert('Error: ' + (error.response?.data?.detail || 'Upload/Embedding failed'));
            return false;
        }
    };

    if (loading) {
        return <div className="loading-container"><div className="spinner"></div></div>;
    }

    return (
        <div className="teacher-dashboard">
            {/* Sidebar */}
            <div className="dashboard-sidebar">
                <div className="sidebar-header">
                    <h2><span className="icon">&#9726;</span> My Courses</h2>
                </div>

                {/* All Chatbots Button */}
                <div
                    className={`course-item all-chatbots ${showAllChatbots ? 'active' : ''}`}
                    onClick={() => { setShowAllChatbots(true); setSelectedCourse(null); }}
                >
                    <span className="course-name"><span className="icon">&#127760;</span> All Chatbots ({getAllChatbots().length})</span>
                </div>

                <div className="course-list">
                    {courses.map(course => (
                        <div
                            key={course.id}
                            className={`course-item ${selectedCourse?.id === course.id && !showAllChatbots ? 'active' : ''}`}
                            onClick={() => { setSelectedCourse(course); setShowAllChatbots(false); }}
                        >
                            <span className="course-name">{course.name}</span>
                        </div>
                    ))}
                </div>
                <div className="sidebar-footer">
                    <Link to="/teacher/quiz-generator" className="btn btn-primary btn-full">
                        <span className="icon">&#10022;</span> AI Quiz Generator
                    </Link>
                </div>
            </div>

            {/* Main Content */}
            <div className="dashboard-main">
                {showAllChatbots ? (
                    /* Global Chatbots View */
                    <ChatbotsTab
                        course={{ name: "All My Chatbots", chatbots: getAllChatbots() }}
                        showForm={showChatbotForm}
                        setShowForm={setShowChatbotForm}
                        form={chatbotForm}
                        setForm={setChatbotForm}
                        onSubmit={handleCreateChatbot}
                        onFileUpload={handleFileUpload}
                        allCourses={courses}
                        onRefresh={loadCourses}
                        isGlobal={true}
                    />
                ) : selectedCourse ? (
                    <>
                        <div className="main-header">
                            <h1>{selectedCourse.name}</h1>
                            <p>{selectedCourse.description}</p>
                        </div>

                        {/* Tabs */}
                        <div className="tabs">
                            <button
                                className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
                                onClick={() => setActiveTab('overview')}
                            ><span className="icon">&#9636;</span> Overview</button>
                            <button
                                className={`tab ${activeTab === 'chatbots' ? 'active' : ''}`}
                                onClick={() => setActiveTab('chatbots')}
                            ><span className="icon">&#9881;</span> Chatbots</button>
                            <button
                                className={`tab ${activeTab === 'quizzes' ? 'active' : ''}`}
                                onClick={() => setActiveTab('quizzes')}
                            ><span className="icon">&#9998;</span> Quizzes</button>
                            <button
                                className={`tab ${activeTab === 'assignments' ? 'active' : ''}`}
                                onClick={() => setActiveTab('assignments')}
                            ><span className="icon">&#9776;</span> Assignments</button>
                            <button
                                className={`tab ${activeTab === 'students' ? 'active' : ''}`}
                                onClick={() => setActiveTab('students')}
                            ><span className="icon">&#9679;</span> Students</button>
                        </div>

                        {/* Tab Content */}
                        <div className="tab-content">
                            {activeTab === 'overview' && (
                                <OverviewTab analytics={analytics} />
                            )}

                            {activeTab === 'chatbots' && (
                                <ChatbotsTab
                                    course={selectedCourse}
                                    showForm={showChatbotForm}
                                    setShowForm={setShowChatbotForm}
                                    form={chatbotForm}
                                    setForm={setChatbotForm}
                                    onSubmit={handleCreateChatbot}
                                    onFileUpload={handleFileUpload}
                                    allCourses={courses}
                                    onRefresh={loadCourses}
                                />
                            )}

                            {activeTab === 'quizzes' && (
                                <QuizzesTab course={selectedCourse} />
                            )}

                            {activeTab === 'assignments' && (
                                <AssignmentsTab
                                    course={selectedCourse}
                                    showForm={showAssignmentForm}
                                    setShowForm={setShowAssignmentForm}
                                    form={assignmentForm}
                                    setForm={setAssignmentForm}
                                    onSubmit={handleCreateAssignment}
                                />
                            )}

                            {activeTab === 'students' && (
                                <StudentsTab courseId={selectedCourse.id} />
                            )}
                        </div>
                    </>
                ) : (
                    <div className="no-course">
                        <h2>No courses yet</h2>
                        <p>Create your first course to get started!</p>
                    </div>
                )}
            </div>
        </div>
    );
};

// Overview Tab Component
const OverviewTab = ({ analytics }) => (
    <div className="overview-tab">
        <div className="stats-grid">
            <div className="stat-card">
                <div className="stat-icon">&#9679;</div>
                <div className="stat-info">
                    <h3>{analytics?.total_students || 0}</h3>
                    <p>Total Students</p>
                </div>
            </div>
            <div className="stat-card">
                <div className="stat-icon">&#9998;</div>
                <div className="stat-info">
                    <h3>{analytics?.total_quizzes || 0}</h3>
                    <p>Quizzes</p>
                </div>
            </div>
            <div className="stat-card">
                <div className="stat-icon">&#9776;</div>
                <div className="stat-info">
                    <h3>{analytics?.total_assignments || 0}</h3>
                    <p>Assignments</p>
                </div>
            </div>
            <div className="stat-card">
                <div className="stat-icon">&#8599;</div>
                <div className="stat-info">
                    <h3>{analytics?.avg_quiz_score?.toFixed(1) || 0}%</h3>
                    <p>Avg Quiz Score</p>
                </div>
            </div>
        </div>

        {analytics?.top_students?.length > 0 && (
            <div className="section-card">
                <h3><span className="icon">&#9733;</span> Top Performing Students</h3>
                <div className="student-list">
                    {analytics.top_students.map((student, idx) => (
                        <div key={idx} className="student-row">
                            <span className="rank">#{idx + 1}</span>
                            <span className="name">{student.username}</span>
                            <span className="score">{student.avg_score?.toFixed(1) || 0}%</span>
                        </div>
                    ))}
                </div>
            </div>
        )}
    </div>
);

// Chatbots Tab Component with Full Management
const ChatbotsTab = ({ course, showForm, setShowForm, form, setForm, onSubmit, onFileUpload, allCourses, onRefresh, isGlobal }) => {
    const [editingBot, setEditingBot] = useState(null);
    const [showDocuments, setShowDocuments] = useState(null);
    const [documents, setDocuments] = useState([]);
    const [showAssign, setShowAssign] = useState(null);
    const [testingBot, setTestingBot] = useState(null);
    const [uploading, setUploading] = useState(null);

    // Load documents for a chatbot
    const loadDocuments = async (botId) => {
        try {
            const response = await teacherAPI.getDocuments(botId);
            setDocuments(response.data);
            setShowDocuments(botId);
        } catch (error) {
            console.error('Error loading documents:', error);
        }
    };

    // Delete a document
    const handleDeleteDocument = async (botId, docId) => {
        if (!confirm('Delete this document?')) return;
        try {
            await teacherAPI.deleteDocument(botId, docId);
            loadDocuments(botId);
            onRefresh && onRefresh();
        } catch (error) {
            alert('Error deleting document');
        }
    };

    // Update chatbot settings
    const handleUpdateChatbot = async (botId) => {
        try {
            await teacherAPI.updateChatbot(botId, editingBot);
            alert('Chatbot updated!');
            setEditingBot(null);
            onRefresh && onRefresh();
        } catch (error) {
            alert('Error updating chatbot');
        }
    };

    // Assign chatbot to another course
    const handleAssign = async (botId, courseId) => {
        try {
            await teacherAPI.assignChatbotToCourse(botId, courseId);
            alert('Chatbot assigned to course!');
            setShowAssign(null);
            onRefresh && onRefresh();
        } catch (error) {
            alert(error.response?.data?.detail || 'Error assigning chatbot');
        }
    };

    // Delete chatbot
    const handleDeleteChatbot = async (botId) => {
        if (!confirm('Delete this chatbot and all its documents?')) return;
        try {
            await teacherAPI.deleteChatbot(botId);
            onRefresh && onRefresh();
        } catch (error) {
            alert('Error deleting chatbot');
        }
    };

    return (
        <div className="chatbots-tab">
            <div className="tab-header">
                <h3>{isGlobal ? 'All Chatbots Management' : `AI Chatbots for ${course.name}`}</h3>
                <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
                    {showForm ? 'x Cancel' : '+ Create Chatbot'}
                </button>
            </div>

            {showForm && (
                <form className="form-card" onSubmit={onSubmit}>
                    {isGlobal && (
                        <div className="form-group">
                            <label>Select Course *</label>
                            <select
                                required
                                onChange={(e) => setForm({ ...form, target_course_id: e.target.value })}
                            >
                                <option value="">-- Select a Course --</option>
                                {allCourses?.map(c => (
                                    <option key={c.id} value={c.id}>{c.name}</option>
                                ))}
                            </select>
                        </div>
                    )}
                    <div className="form-group">
                        <label>Chatbot Name *</label>
                        <input
                            type="text"
                            value={form.name}
                            onChange={(e) => setForm({ ...form, name: e.target.value })}
                            placeholder="e.g., Math Tutor"
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label>Description</label>
                        <textarea
                            value={form.description}
                            onChange={(e) => setForm({ ...form, description: e.target.value })}
                            placeholder="Brief description of what this chatbot helps with"
                        />
                    </div>

                    {/* LLM Provider Selection */}
                    <div className="form-row">
                        <div className="form-group">
                            <label>AI Provider</label>
                            <select
                                value={form.llm_provider || 'mistral'}
                                onChange={(e) => {
                                    const provider = e.target.value;
                                    const model = provider === 'mistral' ? 'mistral-small-latest' : 'gemini-2.0-flash';
                                    setForm({ ...form, llm_provider: provider, llm_model: model });
                                }}
                            >
                                <option value="mistral">Mistral AI</option>
                                <option value="gemini">Google Gemini</option>
                            </select>
                        </div>
                        <div className="form-group">
                            <label>Model</label>
                            <select
                                value={form.llm_model || ''}
                                onChange={(e) => setForm({ ...form, llm_model: e.target.value })}
                            >
                                {form.llm_provider === 'mistral' ? (
                                    <>
                                        <option value="mistral-small-latest">Mistral Small (Fast)</option>
                                        <option value="mistral-large-latest">Mistral Large (Best)</option>
                                    </>
                                ) : (
                                    <>
                                        <option value="gemini-2.0-flash">Gemini 2.0 Flash (Fast)</option>
                                        <option value="gemini-2.5-pro">Gemini 2.5 Pro (Best)</option>
                                    </>
                                )}
                            </select>
                        </div>
                    </div>

                    <div className="form-group">
                        <label>System Prompt (AI Instructions)</label>
                        <textarea
                            value={form.system_prompt}
                            onChange={(e) => setForm({ ...form, system_prompt: e.target.value })}
                            placeholder="You are a helpful math tutor. Explain concepts clearly..."
                            rows={4}
                        />
                    </div>
                    <button type="submit" className="btn btn-primary">Create Chatbot</button>
                </form>
            )}

            <div className="chatbot-list">
                {course.chatbots?.length > 0 ? (
                    course.chatbots.map(bot => (
                        <div key={bot.id} className="chatbot-card">
                            {/* Chatbot Header with Actions */}
                            <div className="chatbot-info">
                                <div className="chatbot-header">
                                    <h4>{bot.name}</h4>
                                    <span className="llm-badge">{bot.llm_provider || 'gemini'}</span>
                                    <div className="chatbot-actions-top">
                                        <button className="btn-icon" onClick={() => setTestingBot(bot)} title="Test Chatbot" style={{ background: '#28a745', color: 'white', marginRight: '5px' }}>
                                            💬 Test
                                        </button>
                                        <button className="btn-icon" onClick={() => setEditingBot({ ...bot })} title="Edit">
                                            Edit
                                        </button>
                                        <button className="btn-icon" onClick={() => setShowAssign(bot.id)} title="Assign to Course">
                                            Assign
                                        </button>
                                        <button className="btn-icon danger" onClick={() => handleDeleteChatbot(bot.id)} title="Delete">
                                            Delete
                                        </button>
                                    </div>
                                </div>
                                <p className="chatbot-desc">{bot.description || 'No description'}</p>
                                <p className="chatbot-model">Model: {bot.llm_model || 'default'}</p>

                                {/* Assigned Courses */}
                                {bot.assigned_courses?.length > 0 && (
                                    <div className="assigned-courses">
                                        <span className="label">Assigned to: </span>
                                        {bot.assigned_courses.map((c, i) => (
                                            <span key={c.id} className="course-tag">
                                                {c.name}{i < bot.assigned_courses.length - 1 ? ', ' : ''}
                                            </span>
                                        ))}
                                    </div>
                                )}
                            </div>

                            {/* Assign to Course Modal */}
                            {showAssign === bot.id && (
                                <div className="assign-section">
                                    <h5>Assign to Another Course</h5>
                                    <select onChange={(e) => e.target.value && handleAssign(bot.id, e.target.value)}>
                                        <option value="">Select a course...</option>
                                        {allCourses?.filter(c => c.id !== course.id).map(c => (
                                            <option key={c.id} value={c.id}>{c.name}</option>
                                        ))}
                                    </select>
                                    <button className="btn btn-secondary" onClick={() => setShowAssign(null)}>Cancel</button>
                                </div>
                            )}

                            {/* Knowledge Base Section */}
                            <div className="knowledge-base-section">
                                <div className="kb-header">
                                    <h5>Knowledge Base</h5>
                                    <button className="btn-link" onClick={() => loadDocuments(bot.id)}>
                                        View Documents ({bot.document_count || 0})
                                    </button>
                                </div>
                                <p className="kb-info">Upload PDF or TXT files. The chatbot answers from these only.</p>
                                <div className="kb-actions">
                                    <label className={`upload-btn ${uploading === bot.id ? 'disabled' : ''}`} style={{ cursor: uploading === bot.id ? 'wait' : 'pointer' }}>
                                        {uploading === bot.id ? (
                                            <span>⏳ Processing...</span>
                                        ) : (
                                            <span><span className="icon">+</span> Upload PDF/TXT</span>
                                        )}
                                        <input
                                            type="file"
                                            accept=".pdf,.txt"
                                            disabled={uploading === bot.id}
                                            onChange={async (e) => {
                                                if (e.target.files[0]) {
                                                    setUploading(bot.id);
                                                    const success = await onFileUpload(bot.id, e);
                                                    if (success) await loadDocuments(bot.id);
                                                    setUploading(null);
                                                    e.target.value = '';
                                                }
                                            }}
                                            style={{ display: 'none' }}
                                        />
                                    </label>
                                </div>

                                {/* Document List */}
                                {showDocuments === bot.id && (
                                    <div className="document-list">
                                        <h6>Documents:</h6>
                                        {documents.length > 0 ? (
                                            documents.map(doc => (
                                                <div key={doc.id} className="document-item">
                                                    <span>{doc.filename}</span>
                                                    <button
                                                        className="btn-delete"
                                                        onClick={() => handleDeleteDocument(bot.id, doc.id)}
                                                    >
                                                        Delete
                                                    </button>
                                                </div>
                                            ))
                                        ) : (
                                            <p>No documents uploaded yet.</p>
                                        )}
                                        <button className="btn-link" onClick={() => setShowDocuments(null)}>Close</button>
                                    </div>
                                )}
                            </div>
                        </div>
                    ))
                ) : (
                    <div className="empty-state">
                        <p>No chatbots yet.</p>
                        <p>Create a chatbot to let students ask questions about your course materials.</p>
                    </div>
                )}
            </div>

            {/* Edit Modal */}
            {editingBot && (
                <div className="modal-overlay" onClick={() => setEditingBot(null)}>
                    <div className="modal-content" onClick={e => e.stopPropagation()}>
                        <h3>Edit Chatbot</h3>
                        <div className="form-group">
                            <label>Name</label>
                            <input
                                type="text"
                                value={editingBot.name}
                                onChange={(e) => setEditingBot({ ...editingBot, name: e.target.value })}
                            />
                        </div>
                        <div className="form-group">
                            <label>Description</label>
                            <textarea
                                value={editingBot.description || ''}
                                onChange={(e) => setEditingBot({ ...editingBot, description: e.target.value })}
                            />
                        </div>
                        <div className="form-group">
                            <label>System Prompt</label>
                            <textarea
                                value={editingBot.system_prompt || ''}
                                onChange={(e) => setEditingBot({ ...editingBot, system_prompt: e.target.value })}
                                rows={4}
                            />
                        </div>
                        <div className="form-row">
                            <div className="form-group">
                                <label>AI Provider</label>
                                <select
                                    value={editingBot.llm_provider}
                                    onChange={(e) => setEditingBot({ ...editingBot, llm_provider: e.target.value })}
                                >
                                    <option value="gemini">Google Gemini</option>
                                    <option value="mistral">Mistral AI</option>
                                </select>
                            </div>
                            <div className="form-group">
                                <label>Model</label>
                                <select
                                    value={editingBot.llm_model}
                                    onChange={(e) => setEditingBot({ ...editingBot, llm_model: e.target.value })}
                                >
                                    {editingBot.llm_provider === 'mistral' ? (
                                        <>
                                            <option value="mistral-small-latest">Mistral Small</option>
                                            <option value="mistral-large-latest">Mistral Large</option>
                                        </>
                                    ) : (
                                        <>
                                            <option value="gemini-2.0-flash">Gemini 2.0 Flash</option>
                                            <option value="gemini-2.5-pro">Gemini 2.5 Pro</option>
                                        </>
                                    )}
                                </select>
                            </div>
                        </div>
                        <div className="modal-actions">
                            <button className="btn btn-secondary" onClick={() => setEditingBot(null)}>Cancel</button>
                            <button className="btn btn-primary" onClick={() => handleUpdateChatbot(editingBot.id)}>Save</button>
                        </div>
                    </div>
                </div>
            )}
            {/* Test Chatbot Modal */}
            {testingBot && (
                <TestChatbotModal
                    chatbot={testingBot}
                    onClose={() => setTestingBot(null)}
                />
            )}
        </div>
    );
};

// Test Chatbot Modal Component
const TestChatbotModal = ({ chatbot, onClose }) => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const scrollRef = useRef(null);

    useEffect(() => {
        loadHistory();
    }, []);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const loadHistory = async () => {
        try {
            const res = await teacherAPI.getTestChatHistory(chatbot.id);
            setMessages(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const question = input;
        setInput('');
        const userMsg = { role: 'user', content: question, created_at: new Date().toISOString() };
        setMessages(prev => [...prev, userMsg]);
        setLoading(true);

        try {
            const res = await teacherAPI.testChatbot(chatbot.id, question);
            const aiMsg = { role: 'assistant', content: res.data.answer, created_at: new Date().toISOString() };
            setMessages(prev => [...prev, aiMsg]);
        } catch (err) {
            alert("Error testing bot: " + err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="modal-overlay">
            <div className="modal-content" style={{ width: '600px', height: '80vh', display: 'flex', flexDirection: 'column', padding: 0 }}>
                <div className="modal-header" style={{ padding: '20px', borderBottom: '1px solid #333' }}>
                    <div>
                        <h3 style={{ margin: 0 }}>💬 Test: {chatbot.name}</h3>
                        <span style={{ fontSize: '0.9em', color: '#aaa' }}>Model: {chatbot.llm_model}</span>
                    </div>
                    <button className="close-btn" onClick={onClose}>×</button>
                </div>

                <div className="chat-messages" ref={scrollRef} style={{ flex: 1, overflowY: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: '15px' }}>
                    {messages.length === 0 && <p style={{ textAlign: 'center', color: '#666', marginTop: '50px' }}>Start testing your chatbot!</p>}
                    {messages.map((msg, idx) => (
                        <div key={idx} className={`message ${msg.role === 'user' ? 'user-message' : 'bot-message'}`}
                            style={{
                                alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                                background: msg.role === 'user' ? '#007bff' : '#333',
                                color: '#fff',
                                padding: '10px 15px',
                                borderRadius: '15px',
                                maxWidth: '80%'
                            }}>
                            <strong>{msg.role === 'user' ? 'You' : 'AI'}:</strong>
                            <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
                        </div>
                    ))}
                    {loading && <div className="loading-dots" style={{ alignSelf: 'flex-start', color: '#aaa' }}>AI is thinking...</div>}
                </div>

                <form onSubmit={handleSend} style={{ padding: '20px', borderTop: '1px solid #333', display: 'flex', gap: '10px' }}>
                    <input
                        type="text"
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        placeholder="Type a message..."
                        style={{ flex: 1, padding: '10px', borderRadius: '5px', border: '1px solid #444', background: '#222', color: '#fff' }}
                        autoFocus
                    />
                    <button type="submit" className="btn btn-primary" disabled={loading}>Send</button>
                </form>
            </div>
        </div>
    );
};

// Quizzes Tab Component
const QuizzesTab = ({ course }) => {
    const [quizzes, setQuizzes] = useState(course.quizzes || []);
    const [publishing, setPublishing] = useState(null);
    const [viewingQuiz, setViewingQuiz] = useState(null);
    const [quizDetails, setQuizDetails] = useState(null);
    const [loadingQuiz, setLoadingQuiz] = useState(false);

    const handleTogglePublish = async (quizId, currentStatus) => {
        setPublishing(quizId);
        try {
            if (currentStatus) {
                await teacherAPI.unpublishQuiz(quizId);
                alert('Quiz unpublished - students can no longer see it');
            } else {
                await teacherAPI.publishQuiz(quizId);
                alert('Quiz published - students can now see it!');
            }
            setQuizzes(quizzes.map(q =>
                q.id === quizId ? { ...q, is_active: !currentStatus } : q
            ));
        } catch (error) {
            alert('Error: ' + (error.response?.data?.detail || 'Operation failed'));
        } finally {
            setPublishing(null);
        }
    };

    const handleViewQuiz = async (quizId) => {
        setViewingQuiz(quizId);
        setLoadingQuiz(true);
        try {
            const response = await teacherAPI.getQuiz(quizId);
            setQuizDetails(response.data);
        } catch (error) {
            alert('Error loading quiz: ' + (error.response?.data?.detail || 'Failed to load'));
            setViewingQuiz(null);
        } finally {
            setLoadingQuiz(false);
        }
    };

    return (
        <div className="quizzes-tab">
            <div className="tab-header">
                <h3>Quizzes for {course.name}</h3>
                <Link to="/teacher/quiz-generator" className="btn btn-primary">
                    <span className="icon">&#10022;</span> Generate with AI
                </Link>
            </div>

            <div className="quiz-list">
                {quizzes.length > 0 ? (
                    quizzes.map(quiz => (
                        <div key={quiz.id} className="quiz-card">
                            <div className="quiz-info">
                                <div className="quiz-header-row">
                                    <h4>{quiz.title}</h4>
                                    <span className={`badge ${quiz.is_active ? 'badge-published' : 'badge-draft'}`}>
                                        {quiz.is_active ? 'Published' : 'Draft'}
                                    </span>
                                </div>
                                <p>{quiz.description}</p>
                                <div className="quiz-meta">
                                    <span>Time: {quiz.time_limit_minutes} min</span>
                                    <span>Questions: {quiz.question_count || 0}</span>
                                    <span>Attempts: {quiz.max_attempts}</span>
                                </div>
                            </div>
                            <div className="quiz-actions">
                                <button
                                    className="btn btn-secondary btn-sm"
                                    onClick={() => handleViewQuiz(quiz.id)}
                                    title="View quiz questions"
                                >
                                    View
                                </button>
                                <button
                                    className={`btn ${quiz.is_active ? 'btn-warning' : 'btn-success'} btn-sm`}
                                    onClick={() => handleTogglePublish(quiz.id, quiz.is_active)}
                                    disabled={publishing === quiz.id}
                                >
                                    {publishing === quiz.id ? '...' : quiz.is_active ? 'Unforward' : 'Forward'}
                                </button>
                            </div>
                        </div>
                    ))
                ) : (
                    <p className="empty-state">No quizzes yet. Use AI to generate them!</p>
                )}
            </div>

            {/* Quiz Viewer Modal */}
            {viewingQuiz && (
                <div className="modal-overlay" onClick={() => setViewingQuiz(null)}>
                    <div className="modal-content quiz-viewer" onClick={e => e.stopPropagation()}>
                        {loadingQuiz ? (
                            <div className="loading">Loading quiz...</div>
                        ) : quizDetails ? (
                            <>
                                <div className="modal-header">
                                    <h2>{quizDetails.title}</h2>
                                    <button className="close-btn" onClick={() => setViewingQuiz(null)}>×</button>
                                </div>
                                <div className="modal-body">
                                    <p className="quiz-description">{quizDetails.description}</p>
                                    <div className="quiz-info-bar">
                                        <span>Time Limit: {quizDetails.time_limit_minutes} minutes</span>
                                        <span>Max Attempts: {quizDetails.max_attempts}</span>
                                        <span className={`badge ${quizDetails.is_active ? 'badge-published' : 'badge-draft'}`}>
                                            {quizDetails.is_active ? 'Published' : 'Draft'}
                                        </span>
                                    </div>

                                    <h3>Questions ({quizDetails.questions?.length || 0})</h3>
                                    <div className="questions-preview">
                                        {quizDetails.questions?.map((q, idx) => (
                                            <div key={q.id} className="question-preview">
                                                <div className="question-header">
                                                    <span className="q-number">Q{idx + 1}</span>
                                                    <span className={`q-type ${q.question_type}`}>
                                                        {q.question_type === 'mcq' ? 'Multiple Choice' :
                                                            q.question_type === 'true_false' ? 'True/False' : 'Short Answer'}
                                                    </span>
                                                    <span className="q-points">{q.points} pts</span>
                                                </div>
                                                <p className="q-text">{q.question_text}</p>

                                                {q.question_type === 'mcq' && q.options && (
                                                    <div className="q-options">
                                                        {q.options.map((opt, i) => (
                                                            <div key={i} className={`q-option ${opt === q.correct_answer ? 'correct' : ''}`}>
                                                                <span className="opt-label">{String.fromCharCode(65 + i)}.</span>
                                                                {opt}
                                                                {opt === q.correct_answer && <span className="check">✓</span>}
                                                            </div>
                                                        ))}
                                                    </div>
                                                )}

                                                {q.question_type === 'true_false' && (
                                                    <div className="q-options">
                                                        <div className={`q-option ${q.correct_answer === 'True' ? 'correct' : ''}`}>
                                                            True {q.correct_answer === 'True' && <span className="check">✓</span>}
                                                        </div>
                                                        <div className={`q-option ${q.correct_answer === 'False' ? 'correct' : ''}`}>
                                                            False {q.correct_answer === 'False' && <span className="check">✓</span>}
                                                        </div>
                                                    </div>
                                                )}

                                                {q.question_type === 'short_answer' && (
                                                    <div className="q-answer">
                                                        <strong>Expected Answer:</strong> {q.correct_answer}
                                                    </div>
                                                )}

                                                {q.explanation && (
                                                    <div className="q-explanation">
                                                        <strong>Explanation:</strong> {q.explanation}
                                                    </div>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </>
                        ) : (
                            <div>No quiz data</div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

// Assignments Tab Component
const AssignmentsTab = ({ course, showForm, setShowForm, form, setForm, onSubmit }) => {
    const [showRAGForm, setShowRAGForm] = useState(false);
    const [ragForm, setRagForm] = useState({
        chatbotId: '',
        topic: '',
        maxScore: 100,
        numQuestions: 5,
        llmProvider: 'gemini',
        llmModel: 'gemini-1.5-flash'
    });
    const [generating, setGenerating] = useState(false);

    // New state for assignment actions
    const [assignments, setAssignments] = useState(course.assignments || []);
    const [publishing, setPublishing] = useState(null);
    const [viewingAssignment, setViewingAssignment] = useState(null);

    // Update local assignments when course prop changes
    useEffect(() => {
        setAssignments(course.assignments || []);
    }, [course.assignments]);

    const handleTogglePublish = async (assignmentId, currentStatus) => {
        setPublishing(assignmentId);
        try {
            if (currentStatus) {
                await teacherAPI.unpublishAssignment(assignmentId);
                alert('Assignment unpublished - students can no longer see it');
            } else {
                await teacherAPI.publishAssignment(assignmentId);
                alert('Assignment forwarded - students can now see it!');
            }
            setAssignments(assignments.map(a =>
                a.id === assignmentId ? { ...a, is_active: !currentStatus } : a
            ));
        } catch (error) {
            alert('Error: ' + (error.response?.data?.detail || 'Operation failed'));
        } finally {
            setPublishing(null);
        }
    };

    const handleRAGGenerate = async (e) => {
        e.preventDefault();
        setGenerating(true);
        try {
            const response = await teacherAPI.generateAssignmentFromRAG(
                course.id,
                ragForm.chatbotId,
                ragForm.topic,
                ragForm.maxScore,
                ragForm.numQuestions,
                ragForm.llmProvider,
                ragForm.llmModel
            );
            alert(`Assignment created from course documents!\n\nTitle: ${response.data.assignment_title}\nSource: ${response.data.chatbot_used}\nChunks used: ${response.data.chunks_used}\n\nAssignment is saved as Draft. Check below and click Forward when ready.`);
            setShowRAGForm(false);
            setRagForm({ chatbotId: '', topic: '', maxScore: 100, numQuestions: 5, llmProvider: 'gemini', llmModel: 'gemini-1.5-flash' });
            window.location.reload(); // Reload to show new assignment
        } catch (error) {
            alert('Error: ' + (error.response?.data?.detail || 'Failed to generate'));
        } finally {
            setGenerating(false);
        }
    };

    return (
        <div className="assignments-tab">
            <div className="tab-header">
                <h3>Assignments for {course.name}</h3>
                <div className="header-buttons">
                    <button
                        className="btn btn-secondary"
                        onClick={() => {
                            setShowRAGForm(!showRAGForm);
                            setShowForm(false);
                        }}
                    >
                        {showRAGForm ? '× Cancel' : '✨ Generate with AI'}
                    </button>
                    <button
                        className="btn btn-primary"
                        onClick={() => {
                            setShowForm(!showForm);
                            setShowRAGForm(false);
                        }}
                    >
                        {showForm ? '× Cancel' : '+ Create Assignment'}
                    </button>
                </div>
            </div>

            {showRAGForm && (
                <form className="form-card rag-form" onSubmit={handleRAGGenerate}>
                    <h4>Generate Assignment from Course Documents</h4>
                    <p className="help-text">AI will create assignment based on uploaded course materials</p>

                    <div className="form-group">
                        <label>Knowledge Base (Chatbot) *</label>
                        <select
                            value={ragForm.chatbotId}
                            onChange={(e) => setRagForm({ ...ragForm, chatbotId: e.target.value })}
                            required
                        >
                            <option value="">Select chatbot with documents...</option>
                            {course.chatbots?.map(bot => (
                                <option key={bot.id} value={bot.id}>
                                    {bot.name} {bot.document_count > 0 ? `(${bot.document_count} docs)` : '(no documents)'}
                                </option>
                            ))}
                        </select>

                        {ragForm.chatbotId && (
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
                                                await teacherAPI.uploadDocument(ragForm.chatbotId, file);
                                                alert(`File "${file.name}" uploaded! It is processing...`);
                                            } catch (error) {
                                                alert('Upload failed: ' + (error.response?.data?.detail || error.message));
                                            }
                                        }}
                                    />
                                </label>
                            </div>
                        )}
                    </div>

                    <div className="form-row">
                        <div className="form-group">
                            <label>AI Provider:</label>
                            <select
                                name="llmProvider"
                                value={ragForm.llmProvider}
                                onChange={(e) => {
                                    const provider = e.target.value;
                                    setRagForm({
                                        ...ragForm,
                                        llmProvider: provider,
                                        llmModel: provider === 'gemini' ? 'gemini-1.5-flash' : 'mistral-small-latest'
                                    });
                                }}
                                className="form-control"
                            >
                                <option value="gemini">Google Gemini</option>
                                <option value="mistral">Mistral AI</option>
                            </select>
                        </div>
                        <div className="form-group">
                            <label>Model:</label>
                            <select
                                name="llmModel"
                                value={ragForm.llmModel}
                                onChange={(e) => setRagForm({ ...ragForm, llmModel: e.target.value })}
                                className="form-control"
                            >
                                {ragForm.llmProvider === 'gemini' ? (
                                    <>
                                        <option value="gemini-1.5-flash">Gemini 1.5 Flash (Fast)</option>
                                        <option value="gemini-2.0-flash">Gemini 2.0 Flash (New)</option>
                                        <option value="gemini-1.5-pro">Gemini 1.5 Pro (Old)</option>
                                    </>
                                ) : (
                                    <>
                                        <option value="mistral-small-latest">Mistral Small</option>
                                        <option value="mistral-medium-latest">Mistral Medium</option>
                                    </>
                                )}
                            </select>
                        </div>
                    </div>

                    <div className="form-group">
                        <label>Focus Topic (optional)</label>
                        <input
                            type="text"
                            value={ragForm.topic}
                            onChange={(e) => setRagForm({ ...ragForm, topic: e.target.value })}
                            placeholder="e.g., Newton's Laws, Chemical Reactions"
                        />
                    </div>

                    <div className="form-row">
                        <div className="form-group">
                            <label>Max Score</label>
                            <input
                                type="number"
                                value={ragForm.maxScore}
                                onChange={(e) => setRagForm({ ...ragForm, maxScore: parseInt(e.target.value) })}
                                min={10}
                            />
                        </div>
                        <div className="form-group">
                            <label>Number of Questions</label>
                            <input
                                type="number"
                                value={ragForm.numQuestions}
                                onChange={(e) => setRagForm({ ...ragForm, numQuestions: parseInt(e.target.value) })}
                                min={1}
                                max={20}
                            />
                        </div>
                    </div>

                    <button type="submit" className="btn btn-primary" disabled={generating}>
                        {generating ? '⏳ Generating...' : '📚 Generate from Documents'}
                    </button>
                </form>
            )}

            {showForm && (
                <form className="form-card" onSubmit={onSubmit}>
                    <div className="form-group">
                        <label>Title *</label>
                        <input
                            type="text"
                            value={form.title}
                            onChange={(e) => setForm({ ...form, title: e.target.value })}
                            placeholder="Assignment title"
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label>Description</label>
                        <textarea
                            value={form.description}
                            onChange={(e) => setForm({ ...form, description: e.target.value })}
                            placeholder="Detailed instructions for students"
                            rows={4}
                        />
                    </div>
                    <div className="form-row">
                        <div className="form-group">
                            <label>Max Score</label>
                            <input
                                type="number"
                                value={form.max_score}
                                onChange={(e) => setForm({ ...form, max_score: parseInt(e.target.value) })}
                                min={1}
                            />
                        </div>
                        <div className="form-group">
                            <label>Due Date</label>
                            <input
                                type="datetime-local"
                                value={form.due_date}
                                onChange={(e) => setForm({ ...form, due_date: e.target.value })}
                            />
                        </div>
                    </div>
                    <button type="submit" className="btn btn-primary">Create Assignment</button>
                </form>
            )}

            <div className="assignment-list">
                {assignments.length > 0 ? (
                    assignments.map(assignment => (
                        <div key={assignment.id} className="assignment-card">
                            <div className="assignment-info">
                                <div className="assignment-header-row" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                                    <h4 style={{ margin: 0 }}>{assignment.title}</h4>
                                    <span className={`badge ${assignment.is_active ? 'badge-published' : 'badge-draft'}`}>
                                        {assignment.is_active ? 'Published' : 'Draft'}
                                    </span>
                                </div>
                                <p>{assignment.description}</p>
                                <div className="assignment-meta">
                                    <span>Max: {assignment.max_score} pts</span>
                                    <span>Due: {assignment.due_date ? new Date(assignment.due_date).toLocaleDateString() : 'No Deadline'}</span>
                                </div>
                            </div>
                            <div className="assignment-actions" style={{ display: 'flex', gap: '10px', marginTop: '15px' }}>
                                <button
                                    className="btn btn-secondary btn-sm"
                                    onClick={() => setViewingAssignment(assignment)}
                                    title="View assignment"
                                >
                                    View
                                </button>
                                <button
                                    className={`btn ${assignment.is_active ? 'btn-warning' : 'btn-success'} btn-sm`}
                                    onClick={() => handleTogglePublish(assignment.id, assignment.is_active)}
                                    disabled={publishing === assignment.id}
                                >
                                    {publishing === assignment.id ? '...' : assignment.is_active ? 'Unforward' : 'Forward'}
                                </button>
                                <span className="submission-count" style={{ marginLeft: 'auto', alignSelf: 'center', fontSize: '0.9em', color: '#888' }}>
                                    {assignment.submission_count || 0} submissions
                                </span>
                            </div>
                        </div>
                    ))
                ) : (
                    <p className="empty-state">No assignments yet. Create one for your students!</p>
                )}
            </div>

            {/* Assignment Viewer Modal */}
            {viewingAssignment && (
                <div className="modal-overlay" onClick={() => setViewingAssignment(null)}>
                    <div className="modal-content" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>{viewingAssignment.title}</h2>
                            <button className="close-btn" onClick={() => setViewingAssignment(null)}>×</button>
                        </div>
                        <div className="modal-body">
                            <div className="assignment-info-bar" style={{ display: 'flex', gap: '15px', marginBottom: '20px', padding: '10px', background: '#f5f5f5', borderRadius: '5px', color: '#333' }}>
                                <span><strong>Max Score:</strong> {viewingAssignment.max_score}</span>
                                <span><strong>Status:</strong> {viewingAssignment.is_active ? 'Published' : 'Draft'}</span>
                                <span><strong>Submissions:</strong> {viewingAssignment.submission_count || 0}</span>
                            </div>
                            <h3>Description / Instructions</h3>
                            <div className="assignment-description" style={{ whiteSpace: 'pre-wrap', lineHeight: '1.6', fontSize: '1.1em' }}>
                                {viewingAssignment.description}
                            </div>
                        </div>
                        <div className="modal-footer" style={{ marginTop: '20px', textAlign: 'right' }}>
                            <button className="btn btn-secondary" onClick={() => setViewingAssignment(null)}>Close</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

// Students Tab Component
const StudentsTab = ({ courseId }) => {
    const [students, setStudents] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadStudents();
    }, [courseId]);

    const [analysisResult, setAnalysisResult] = useState(null);
    const [analyzing, setAnalyzing] = useState(null);

    const loadStudents = async () => {
        try {
            const response = await teacherAPI.getStudents(courseId);
            setStudents(response.data);
        } catch (error) {
            console.error('Error loading students:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleAnalyzeRisk = async (student) => {
        setAnalyzing(student.id);
        try {
            const response = await teacherAPI.predictDifficulty(student.id, courseId);
            setAnalysisResult({ ...response.data, studentName: student.username });
        } catch (error) {
            alert("Analysis failed: " + (error.response?.data?.detail || error.message));
        } finally {
            setAnalyzing(null);
        }
    };

    if (loading) return <div className="loading">Loading students...</div>;

    return (
        <div className="students-tab">
            <div className="tab-header">
                <h3>Enrolled Students ({students.length})</h3>
            </div>

            {analysisResult && (
                <div className="modal-overlay">
                    <div className="modal-content" style={{ maxWidth: '500px' }}>
                        <div className="modal-header">
                            <h3>🤖 AI Performance Analysis</h3>
                            <button className="close-btn" onClick={() => setAnalysisResult(null)}>×</button>
                        </div>
                        <div className="modal-body">
                            <h4>Student: {analysisResult.studentName}</h4>

                            <div className="analysis-card" style={{ padding: '15px', background: '#f8f9fa', borderRadius: '8px', margin: '15px 0', color: '#333' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                                    <strong>Rec. Quiz Difficulty:</strong>
                                    <span className={`risk-badge ${analysisResult.recommended_difficulty === 'hard' ? 'high' : analysisResult.recommended_difficulty === 'medium' ? 'medium' : 'low'}`}>
                                        {analysisResult.recommended_difficulty?.toUpperCase()}
                                    </span>
                                </div>
                                <p><strong>Confidence:</strong> {(analysisResult.confidence * 100).toFixed(1)}%</p>
                                <hr style={{ margin: '10px 0', borderColor: '#ddd' }} />
                                <p><strong>AI Reasoning:</strong></p>
                                <p style={{ fontStyle: 'italic', color: '#555' }}>"{analysisResult.reasoning}"</p>
                                <div style={{ marginTop: '10px', fontSize: '0.9em' }}>
                                    <strong>Stats used:</strong> Quiz Avg: {analysisResult.student_stats?.recent_average}, Assign Avg: {analysisResult.student_stats?.assignment_average}
                                </div>
                            </div>

                            <button className="btn btn-primary btn-full" onClick={() => setAnalysisResult(null)}>
                                Close Report
                            </button>
                        </div>
                    </div>
                </div>
            )}

            <div className="students-table">
                <table>
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Student</th>
                            <th>Quiz Avg</th>
                            <th>Assignment Avg</th>
                            <th>Status</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {students.map((student, idx) => (
                            <tr key={student.id}>
                                <td><span className="rank-badge">#{idx + 1}</span></td>
                                <td>{student.username}</td>
                                <td>{student.quiz_avg?.toFixed(1) || 0}%</td>
                                <td>{student.assignment_avg?.toFixed(1) || 0}%</td>
                                <td>
                                    <span className={`risk-badge ${student.risk_level || 'low'}`}>
                                        {student.risk_level === 'high' ? '! At Risk' :
                                            student.risk_level === 'medium' ? '~ Watch' : '+ Good'}
                                    </span>
                                </td>
                                <td>
                                    <button
                                        className="btn btn-sm btn-outline"
                                        onClick={() => handleAnalyzeRisk(student)}
                                    >
                                        🤖 AI Analysis
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default TeacherDashboard;
