// Quick navigation component for testing AI features
import React from 'react';
import { Link } from 'react-router-dom';
import './QuickNav.css';

const QuickNav = ({ userRole }) => {
    if (userRole === 'student') {
        return (
            <div className="quick-nav">
                <Link to="/student" className="nav-btn">📊 Dashboard</Link>
                <Link to="/student/chatbot" className="nav-btn primary">🤖 AI Tutor</Link>
            </div>
        );
    }

    if (userRole === 'teacher') {
        return (
            <div className="quick-nav">
                <Link to="/teacher" className="nav-btn">📊 Dashboard</Link>
                <Link to="/teacher/quiz-generator" className="nav-btn primary">✨ Generate Quiz</Link>
            </div>
        );
    }

    return null;
};

export default QuickNav;
