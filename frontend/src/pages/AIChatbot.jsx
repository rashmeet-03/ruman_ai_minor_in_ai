import React, { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import { studentAPI } from '../api';
import './AIChatbot.css';

const AIChatbot = () => {
    const location = useLocation();
    const [courses, setCourses] = useState([]);
    const [selectedCourse, setSelectedCourse] = useState(location.state?.courseId || '');
    const [chatbots, setChatbots] = useState([]);
    const [selectedChatbot, setSelectedChatbot] = useState(null);
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    useEffect(() => {
        loadCourses();
    }, []);

    useEffect(() => {
        if (selectedCourse) {
            loadChatbots(selectedCourse);
        }
    }, [selectedCourse]);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const loadCourses = async () => {
        try {
            const response = await studentAPI.getCourses();
            setCourses(response.data);
        } catch (error) {
            console.error('Error loading courses:', error);
        }
    };

    const loadChatbots = async (courseId) => {
        try {
            const response = await studentAPI.getChatbots(courseId);
            setChatbots(response.data);

            // Check for pre-selected chatbot from navigation state
            const targetChatbotId = location.state?.chatbotId;
            let chatbotToSelect = null;

            if (targetChatbotId) {
                chatbotToSelect = response.data.find(c => c.id === targetChatbotId);
            }

            // Fallback to first one if no target or target not found
            if (!chatbotToSelect && response.data.length > 0) {
                chatbotToSelect = response.data[0];
            }

            if (chatbotToSelect) {
                setSelectedChatbot(chatbotToSelect);
                loadChatHistory(chatbotToSelect.id);
            } else {
                setSelectedChatbot(null);
                setMessages([]);
            }
        } catch (error) {
            console.error('Error loading chatbots:', error);
        }
    };

    const loadChatHistory = async (chatbotId) => {
        try {
            const response = await studentAPI.getChatHistory(chatbotId);
            const formattedMessages = response.data.map(msg => ({
                role: msg.role,
                content: msg.content,
                timestamp: msg.created_at
            }));
            setMessages(formattedMessages);
        } catch (error) {
            console.error('Error loading chat history:', error);
            setMessages([]);
        }
    };

    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (!inputMessage.trim() || !selectedChatbot) return;

        const userMessage = {
            role: 'user',
            content: inputMessage,
            timestamp: new Date().toISOString()
        };

        setMessages(prev => [...prev, userMessage]);
        setInputMessage('');
        setLoading(true);

        try {
            const response = await studentAPI.queryChatbot(selectedChatbot.id, inputMessage);
            const aiMessage = {
                role: 'assistant',
                content: response.data.answer,
                timestamp: new Date().toISOString()
            };
            setMessages(prev => [...prev, aiMessage]);
        } catch (error) {
            console.error('Error querying chatbot:', error);
            const errorMessage = {
                role: 'assistant',
                content: 'Sorry, I encountered an error. Please try again.',
                timestamp: new Date().toISOString()
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    const handleClearChat = async () => {
        if (!selectedChatbot || messages.length === 0) return;

        if (window.confirm('Are you sure you want to clear this entire conversation? This cannot be undone.')) {
            try {
                await studentAPI.clearChatHistory(selectedChatbot.id);
                setMessages([]);
            } catch (error) {
                console.error('Error clearing chat:', error);
                alert('Failed to clear chat history.');
            }
        }
    };

    return (
        <div className="ai-chatbot-page">
            <div className="chatbot-header">
                <h1>🤖 AI Tutor</h1>
                <p>Ask questions and get personalized help from your AI tutor</p>
            </div>

            <div className="chatbot-controls">
                <div className="control-group">
                    <label>Select Course:</label>
                    <select
                        value={selectedCourse}
                        onChange={(e) => setSelectedCourse(e.target.value)}
                        className="course-select"
                    >
                        <option value="">Choose a course...</option>
                        {courses.map(course => (
                            <option key={course.id} value={course.id}>
                                {course.name}
                            </option>
                        ))}
                    </select>
                </div>

                {chatbots.length > 0 && (
                    <div className="control-group">
                        <label>AI Tutor:</label>
                        <select
                            value={selectedChatbot?.id || ''}
                            onChange={(e) => {
                                const chatbot = chatbots.find(c => c.id === parseInt(e.target.value));
                                setSelectedChatbot(chatbot);
                                if (chatbot) loadChatHistory(chatbot.id);
                            }}
                            className="chatbot-select"
                        >
                            {chatbots.map(chatbot => (
                                <option key={chatbot.id} value={chatbot.id}>
                                    {chatbot.name}
                                </option>
                            ))}
                        </select>
                    </div>
                )}
            </div>

            {
                selectedChatbot ? (
                    <div className="chat-container card">
                        <div className="chat-header" style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            padding: '15px',
                            borderBottom: '1px solid var(--border-color)',
                            marginBottom: '10px'
                        }}>
                            <h3 style={{ margin: 0, fontSize: '1.2rem' }}>{selectedChatbot.name}</h3>
                            <button
                                onClick={handleClearChat}
                                className="btn-clear-chat"
                                disabled={messages.length === 0}
                            >
                                🗑️ Clear Chat
                            </button>
                        </div>
                        <div className="chat-messages">
                            {messages.length === 0 ? (
                                <div className="empty-state">
                                    <div className="empty-icon">💬</div>
                                    <p>Start a conversation with your AI tutor!</p>
                                    <p className="empty-subtitle">Ask questions, request explanations, or get help with homework</p>
                                </div>
                            ) : (
                                messages.map((msg, index) => (
                                    <div key={index} className={`message ${msg.role}`}>
                                        <div className="message-avatar">
                                            {msg.role === 'user' ? '👤' : '🤖'}
                                        </div>
                                        <div className="message-content">
                                            <div className="message-text markdown-content">
                                                <ReactMarkdown
                                                    remarkPlugins={[remarkGfm, remarkMath]}
                                                    rehypePlugins={[rehypeKatex]}
                                                >
                                                    {msg.content}
                                                </ReactMarkdown>
                                            </div>
                                            <div className="message-time">
                                                {new Date(msg.timestamp).toLocaleTimeString()}
                                            </div>
                                        </div>
                                    </div>
                                ))
                            )}
                            {loading && (
                                <div className="message assistant">
                                    <div className="message-avatar">🤖</div>
                                    <div className="message-content">
                                        <div className="typing-indicator">
                                            <span></span>
                                            <span></span>
                                            <span></span>
                                        </div>
                                    </div>
                                </div>
                            )}
                            <div ref={messagesEndRef} />
                        </div>

                        <form onSubmit={handleSendMessage} className="chat-input-form">
                            <input
                                type="text"
                                value={inputMessage}
                                onChange={(e) => setInputMessage(e.target.value)}
                                placeholder="Type your question..."
                                className="chat-input"
                                disabled={loading}
                            />
                            <button
                                type="submit"
                                className="btn btn-primary send-btn"
                                disabled={loading || !inputMessage.trim()}
                            >
                                {loading ? '⏳' : '📤'} Send
                            </button>
                        </form>
                    </div>
                ) : (
                    <div className="no-chatbot card">
                        <div className="empty-icon">🎓</div>
                        <p>Select a course to start chatting with your AI tutor</p>
                    </div>
                )
            }
        </div >
    );
};

export default AIChatbot;
