import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import './Navbar.css';

const Navbar = () => {
    const { user, logout } = useAuth();
    const { theme, toggleTheme } = useTheme();

    return (
        <nav className="navbar">
            <div className="container">
                <div className="navbar-content">
                    <Link to="/" className="navbar-brand">
                        <span className="logo">R</span>
                        <span className="brand-text">Ruman AI</span>
                    </Link>

                    {/* Navigation Links */}
                    <div className="navbar-links">
                        {user?.role === 'student' && (
                            <>
                                <Link to="/student" className="nav-link">Dashboard</Link>
                                <Link to="/student/chatbot" className="nav-link highlight">AI Tutor</Link>
                            </>
                        )}
                        {user?.role === 'teacher' && (
                            <>
                                <Link to="/teacher" className="nav-link">Dashboard</Link>
                                <Link to="/teacher/quiz-generator" className="nav-link highlight">AI Quiz</Link>
                            </>
                        )}
                        {user?.role === 'admin' && (
                            <>
                                <Link to="/admin" className="nav-link">Admin Panel</Link>
                            </>
                        )}
                    </div>

                    <div className="navbar-actions">
                        <button onClick={toggleTheme} className="theme-toggle btn-secondary btn">
                            {theme === 'light' ? 'Dark' : 'Light'}
                        </button>

                        <div className="user-info">
                            <span className="user-name">{user?.username}</span>
                            <span className="badge badge-yellow">{user?.role}</span>
                        </div>

                        <button onClick={logout} className="btn btn-secondary">
                            Logout
                        </button>
                    </div>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
