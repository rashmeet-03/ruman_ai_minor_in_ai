import React, { useState, useEffect } from 'react';
import { studentAPI } from '../api';
import './Assignment.css';

const Assignments = ({ courseId }) => {
    const [assignments, setAssignments] = useState([]);
    const [selectedAssignment, setSelectedAssignment] = useState(null);
    const [content, setContent] = useState('');
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        loadAssignments();
    }, [courseId]);

    const loadAssignments = async () => {
        try {
            const { data } = await studentAPI.getAssignments(courseId);
            setAssignments(data);
        } catch (error) {
            console.error('Failed to load assignments', error);
        }
    };

    const handleSubmit = async () => {
        if (!content.trim()) {
            alert('Please write your answer');
            return;
        }

        setSubmitting(true);
        try {
            const { data } = await studentAPI.submitAssignment(selectedAssignment.id, content);
            alert(`Assignment submitted! ${data.note}\n\nAI Preliminary Score: ${data.ai_preliminary_score || 'N/A'}\n\n${data.ai_feedback || ''}`);
            setSelectedAssignment(null);
            setContent('');
            loadAssignments();
        } catch (error) {
            alert(error.response?.data?.detail || 'Failed to submit assignment');
        } finally {
            setSubmitting(false);
        }
    };

    if (selectedAssignment && !selectedAssignment.submitted) {
        return (
            <div className="assignment-container">
                <div className="assignment-submit card">
                    <button
                        onClick={() => setSelectedAssignment(null)}
                        className="btn btn-secondary mb-2"
                    >
                        ← Back
                    </button>

                    <h2 className="assignment-title">{selectedAssignment.title}</h2>
                    <p className="assignment-description">{selectedAssignment.description}</p>

                    <div className="assignment-meta">
                        <span>📚 Max Score: {selectedAssignment.max_score} points</span>
                        <span>📅 Due: {new Date(selectedAssignment.due_date).toLocaleDateString()}</span>
                    </div>

                    <div className="form-group">
                        <label className="form-label">Your Answer</label>
                        <textarea
                            className="input assignment-textarea"
                            rows="15"
                            value={content}
                            onChange={(e) => setContent(e.target.value)}
                            placeholder="Write your assignment answer here..."
                            disabled={submitting}
                        />
                    </div>

                    <button
                        onClick={handleSubmit}
                        className="btn btn-primary btn-full"
                        disabled={submitting || !content.trim()}
                    >
                        {submitting ? 'Submitting...' : 'Submit Assignment'}
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="assignment-container">
            <h2 className="section-title">Assignments</h2>

            <div className="assignments-list">
                {assignments.map(assignment => (
                    <div key={assignment.id} className="assignment-card card">
                        <div className="assignment-header">
                            <div>
                                <h3 className="assignment-title">{assignment.title}</h3>
                                <p className="assignment-description">{assignment.description}</p>
                            </div>
                            <span className={`status-badge ${assignment.submitted ? 'submitted' : 'pending'}`}>
                                {assignment.submitted ? '✓ Submitted' : '⏳ Pending'}
                            </span>
                        </div>

                        <div className="assignment-meta">
                            <span>📚 Max Score: {assignment.max_score} points</span>
                            <span>📅 Due: {new Date(assignment.due_date).toLocaleDateString()}</span>
                        </div>

                        {assignment.submitted && (
                            <div className="submission-info">
                                {assignment.score !== null ? (
                                    <>
                                        <div className="score-display">
                                            <span className="badge badge-yellow">
                                                Score: {assignment.score} / {assignment.max_score}
                                            </span>
                                        </div>
                                        {assignment.feedback && (
                                            <div className="feedback-box">
                                                <strong>Feedback:</strong>
                                                <p>{assignment.feedback}</p>
                                            </div>
                                        )}
                                    </>
                                ) : (
                                    <p className="pending-grade">⏳ Awaiting teacher grading</p>
                                )}
                            </div>
                        )}

                        {!assignment.submitted && (
                            <button
                                onClick={() => setSelectedAssignment(assignment)}
                                className="btn btn-primary"
                            >
                                Start Assignment
                            </button>
                        )}
                    </div>
                ))}
            </div>

            {assignments.length === 0 && (
                <p className="empty-state">No assignments available for this course</p>
            )}
        </div>
    );
};

export default Assignments;
