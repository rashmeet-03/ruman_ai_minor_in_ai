import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import { studentAPI } from '../api';
import './Chatbot.css';

const Chatbot = ({ courseId }) => {
    const [chatbots, setChatbots] = useState([]);
    const [selectedBot, setSelectedBot] = useState(null);
    const [messages, setMessages] = useState([]);
    const [question, setQuestion] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    useEffect(() => {
        loadChatbots();
    }, [courseId]);

    useEffect(() => {
        if (selectedBot) {
            loadHistory();
        }
    }, [selectedBot]);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const loadChatbots = async () => {
        try {
            const { data } = await studentAPI.getChatbots(courseId);
            setChatbots(data);
            if (data.length > 0) {
                setSelectedBot(data[0].id);
            }
        } catch (error) {
            console.error('Failed to load chatbots', error);
        }
    };

    const loadHistory = async () => {
        try {
            const { data } = await studentAPI.getChatHistory(selectedBot);
            setMessages(data);
        } catch (error) {
            console.error('Failed to load history', error);
        }
    };

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!question.trim() || loading) return;

        const userMessage = { role: 'user', content: question, created_at: new Date() };
        setMessages(prev => [...prev, userMessage]);
        setQuestion('');
        setLoading(true);

        try {
            const { data } = await studentAPI.queryChatbot(selectedBot, question);
            const assistantMessage = {
                role: 'assistant',
                content: data.answer,
                created_at: new Date()
            };
            setMessages(prev => [...prev, assistantMessage]);
        } catch (error) {
            const errorMessage = {
                role: 'assistant',
                content: '❌ Sorry, I encountered an error. Please try again.',
                created_at: new Date()
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="chatbot-container">
            <div className="chatbot-header card">
                <div>
                    <h2 className="chatbot-title">🤖 AI Tutor</h2>
                    <p className="chatbot-subtitle">Ask questions about your course materials</p>
                </div>
                {chatbots.length > 1 && (
                    <select
                        className="input chatbot-select"
                        value={selectedBot || ''}
                        onChange={(e) => setSelectedBot(Number(e.target.value))}
                    >
                        {chatbots.map(bot => (
                            <option key={bot.id} value={bot.id}>{bot.name}</option>
                        ))}
                    </select>
                )}
            </div>

            <div className="chat-messages card">
                {messages.length === 0 ? (
                    <div className="empty-chat">
                        <p>👋 Hi! I'm your AI tutor.</p>
                        <p>Ask me anything about the course materials!</p>
                    </div>
                ) : (
                    <>
                        {messages.map((msg, idx) => (
                            <div key={idx} className={`message message-${msg.role}`}>
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
                                        {new Date(msg.created_at).toLocaleTimeString()}
                                    </div>
                                </div>
                            </div>
                        ))}
                        {loading && (
                            <div className="message message-assistant">
                                <div className="message-avatar">🤖</div>
                                <div className="message-content">
                                    <div className="typing-indicator">
                                        <span></span><span></span><span></span>
                                    </div>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </>
                )}
            </div>

            <form onSubmit={handleSubmit} className="chat-input-form card">
                <input
                    type="text"
                    className="input chat-input"
                    placeholder="Type your question..."
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    disabled={loading}
                />
                <button type="submit" className="btn btn-primary" disabled={loading || !question.trim()}>
                    Send
                </button>
            </form>
        </div>
    );
};

export default Chatbot;
