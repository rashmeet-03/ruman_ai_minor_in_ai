import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import Login from './pages/Login';
import Register from './pages/Register';
import StudentDashboard from './pages/StudentDashboard';
import TeacherDashboard from './pages/TeacherDashboard';
import AdminDashboard from './pages/AdminDashboard';
import AIChatbot from './pages/AIChatbot';
import QuizGenerator from './pages/QuizGenerator';
import Navbar from './components/Navbar';

const PrivateRoute = ({ children, role }) => {
    const { user, loading } = useAuth();

    if (loading) {
        return (
            <div className="flex-center" style={{ height: '100vh' }}>
                <div className="spinner"></div>
            </div>
        );
    }

    if (!user) {
        return <Navigate to="/login" />;
    }

    if (role && user.role !== role && user.role !== 'admin') {
        return <Navigate to="/" />;
    }

    return children;
};

const AppRoutes = () => {
    const { user } = useAuth();

    return (
        <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
            {user && <Navbar />}
            <div style={{ flex: 1 }}>
                <Routes>
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />

                    <Route
                        path="/student"
                        element={
                            <PrivateRoute role="student">
                                <StudentDashboard />
                            </PrivateRoute>
                        }
                    />

                    <Route
                        path="/student/chatbot"
                        element={
                            <PrivateRoute role="student">
                                <AIChatbot />
                            </PrivateRoute>
                        }
                    />

                    <Route
                        path="/teacher"
                        element={
                            <PrivateRoute role="teacher">
                                <TeacherDashboard />
                            </PrivateRoute>
                        }
                    />

                    <Route
                        path="/teacher/quiz-generator"
                        element={
                            <PrivateRoute role="teacher">
                                <QuizGenerator />
                            </PrivateRoute>
                        }
                    />

                    <Route
                        path="/admin/*"
                        element={
                            <PrivateRoute role="admin">
                                <AdminDashboard />
                            </PrivateRoute>
                        }
                    />

                    <Route path="/" element={
                        user
                            ? user.role === 'student'
                                ? <Navigate to="/student" />
                                : user.role === 'admin'
                                    ? <Navigate to="/admin" />
                                    : <Navigate to="/teacher" />
                            : <Navigate to="/login" />
                    } />
                </Routes>
            </div>
        </div>
    );
};

function App() {
    return (
        <ThemeProvider>
            <AuthProvider>
                <BrowserRouter>
                    <AppRoutes />
                </BrowserRouter>
            </AuthProvider>
        </ThemeProvider>
    );
}

export default App;
