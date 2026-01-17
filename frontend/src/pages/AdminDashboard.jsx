import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './AdminDashboard.css';

const AdminDashboard = () => {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showCreateUser, setShowCreateUser] = useState(false);
    const [newUser, setNewUser] = useState({
        username: '',
        email: '',
        password: '',
        role: 'student'
    });

    useEffect(() => {
        loadUsers();
    }, []);

    const loadUsers = async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem('token');
            const response = await axios.get('/api/admin/users', {
                headers: { Authorization: `Bearer ${token}` }
            });
            setUsers(response.data);
        } catch (error) {
            console.error('Error loading users:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateUser = async (e) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem('token');
            await axios.post('/api/admin/users', newUser, {
                headers: { Authorization: `Bearer ${token}` }
            });
            alert('User created successfully!');
            setShowCreateUser(false);
            setNewUser({ username: '', email: '', password: '', role: 'student' });
            loadUsers();
        } catch (error) {
            alert('Error creating user: ' + (error.response?.data?.detail || 'Unknown error'));
        }
    };

    const handleDeleteUser = async (userId) => {
        if (!confirm('Are you sure you want to delete this user?')) return;

        try {
            const token = localStorage.getItem('token');
            await axios.delete(`/api/admin/users/${userId}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            alert('User deleted successfully!');
            loadUsers();
        } catch (error) {
            alert('Error deleting user: ' + (error.response?.data?.detail || 'Unknown error'));
        }
    };

    const usersByRole = {
        admin: users.filter(u => u.role === 'admin'),
        teacher: users.filter(u => u.role === 'teacher'),
        student: users.filter(u => u.role === 'student')
    };

    if (loading) {
        return <div className="loading">Loading...</div>;
    }

    return (
        <div className="admin-dashboard">
            <div className="dashboard-header">
                <h1>🔧 Admin Dashboard</h1>
                <p>Manage users, courses, and system settings</p>
            </div>

            <div className="admin-stats">
                <div className="stat-card">
                    <div className="stat-icon">👑</div>
                    <div className="stat-content">
                        <h3>{usersByRole.admin.length}</h3>
                        <p>Admins</p>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon">👨‍🏫</div>
                    <div className="stat-content">
                        <h3>{usersByRole.teacher.length}</h3>
                        <p>Teachers</p>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon">👨‍🎓</div>
                    <div className="stat-content">
                        <h3>{usersByRole.student.length}</h3>
                        <p>Students</p>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon">📊</div>
                    <div className="stat-content">
                        <h3>{users.length}</h3>
                        <p>Total Users</p>
                    </div>
                </div>
            </div>

            <div className="admin-actions">
                <button
                    className="btn btn-primary"
                    onClick={() => setShowCreateUser(!showCreateUser)}
                >
                    {showCreateUser ? '✖ Cancel' : '➕ Create New User'}
                </button>
            </div>

            {showCreateUser && (
                <div className="card create-user-form">
                    <h2>Create New User</h2>
                    <form onSubmit={handleCreateUser}>
                        <div className="form-group">
                            <label>Username</label>
                            <input
                                type="text"
                                value={newUser.username}
                                onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label>Email</label>
                            <input
                                type="email"
                                value={newUser.email}
                                onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label>Password</label>
                            <input
                                type="password"
                                value={newUser.password}
                                onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                                required
                                minLength="6"
                            />
                        </div>
                        <div className="form-group">
                            <label>Role</label>
                            <select
                                value={newUser.role}
                                onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
                            >
                                <option value="student">Student</option>
                                <option value="teacher">Teacher</option>
                                <option value="admin">Admin</option>
                            </select>
                        </div>
                        <button type="submit" className="btn btn-primary">Create User</button>
                    </form>
                </div>
            )}

            <div className="users-section">
                <h2>👨‍🏫 Teachers ({usersByRole.teacher.length})</h2>
                <div className="users-table">
                    <table>
                        <thead>
                            <tr>
                                <th>Username</th>
                                <th>Email</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {usersByRole.teacher.map(user => (
                                <tr key={user.id}>
                                    <td>{user.username}</td>
                                    <td>{user.email}</td>
                                    <td>
                                        <span className={`badge ${user.is_active ? 'badge-success' : 'badge-danger'}`}>
                                            {user.is_active ? 'Active' : 'Inactive'}
                                        </span>
                                    </td>
                                    <td>
                                        <button
                                            className="btn btn-danger btn-sm"
                                            onClick={() => handleDeleteUser(user.id)}
                                        >
                                            Delete
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            <div className="users-section">
                <h2>👨‍🎓 Students ({usersByRole.student.length})</h2>
                <div className="users-table">
                    <table>
                        <thead>
                            <tr>
                                <th>Username</th>
                                <th>Email</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {usersByRole.student.slice(0, 10).map(user => (
                                <tr key={user.id}>
                                    <td>{user.username}</td>
                                    <td>{user.email}</td>
                                    <td>
                                        <span className={`badge ${user.is_active ? 'badge-success' : 'badge-danger'}`}>
                                            {user.is_active ? 'Active' : 'Inactive'}
                                        </span>
                                    </td>
                                    <td>
                                        <button
                                            className="btn btn-danger btn-sm"
                                            onClick={() => handleDeleteUser(user.id)}
                                        >
                                            Delete
                                        </button>
                                    </td>
                                </tr>
                            ))}
                            {usersByRole.student.length > 10 && (
                                <tr>
                                    <td colSpan="4" className="text-center">
                                        ... and {usersByRole.student.length - 10} more students
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default AdminDashboard;
