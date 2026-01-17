import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { studentAPI } from '../api';
import './StudentDashboard.css';

const StudentDashboard = () => {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedCourse, setSelectedCourse] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const response = await studentAPI.getDashboard();
      setDashboard(response.data);
      if (response.data.courses?.length > 0) {
        setSelectedCourse(response.data.courses[0]);
      }
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading your dashboard...</p>
      </div>
    );
  }

  return (
    <div className="student-dashboard">
      {/* Sidebar with Gamification */}
      <div className="student-sidebar">
        <div className="profile-section">
          <div className="avatar">
            {dashboard?.student?.username?.charAt(0).toUpperCase() || 'U'}
          </div>
          <h3>{dashboard?.student?.username}</h3>
          <span className="level-badge">Level {dashboard?.progress?.level || 1}</span>
        </div>

        <div className="xp-section">
          <div className="xp-header">
            <span>* XP Points</span>
            <span className="xp-value">{dashboard?.progress?.xp_points || 0}</span>
          </div>
          <div className="xp-bar">
            <div
              className="xp-fill"
              style={{ width: `${((dashboard?.progress?.xp_points || 0) % 500) / 5}%` }}
            ></div>
          </div>
          <p className="xp-next">Next level: {500 - ((dashboard?.progress?.xp_points || 0) % 500)} XP</p>
        </div>

        <div className="streak-section">
          <div className="streak-icon">~</div>
          <div>
            <h4>{dashboard?.progress?.streak_days || 0} Day Streak</h4>
            <p>Keep learning daily!</p>
          </div>
        </div>

        <div className="quick-actions">
          <Link to="/student/chatbot" className="action-btn primary">
            AI Tutor
          </Link>
        </div>
      </div>

      {/* Main Content */}
      <div className="student-main">
        <div className="welcome-banner">
          <div className="welcome-text">
            <h1>Welcome back, {dashboard?.student?.username || 'Student'}!</h1>
            <p>Ready to continue your learning journey?</p>
          </div>
          <div className="quick-stats">
            <div className="quick-stat">
              <span className="stat-num">{dashboard?.courses?.length || 0}</span>
              <span className="stat-label">Courses</span>
            </div>
            <div className="quick-stat">
              <span className="stat-num">{dashboard?.progress?.badges_count || 0}</span>
              <span className="stat-label">Badges</span>
            </div>
          </div>
        </div>

        {/* Course Selector and Tabs */}
        {(!dashboard?.courses || dashboard.courses.length === 0) ? (
          <div className="empty-dashboard-state" style={{ textAlign: 'center', padding: '3rem', background: 'var(--bg-secondary)', borderRadius: '12px', marginTop: '2rem' }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📚</div>
            <h2>No Courses Found</h2>
            <p>You are not enrolled in any courses yet.</p>
            <p style={{ color: 'var(--text-secondary)' }}>Ask your teacher to enroll you to access chatbots, quizzes, and assignments.</p>
          </div>
        ) : (
          <div className="content-area">
            <div className="course-selector">
              <label>Select Course:</label>
              <select
                value={selectedCourse?.id || ''}
                onChange={(e) => {
                  const course = dashboard.courses.find(c => c.id === parseInt(e.target.value));
                  setSelectedCourse(course);
                }}
              >
                {dashboard?.courses?.map(course => (
                  <option key={course.id} value={course.id}>{course.name}</option>
                ))}
              </select>
            </div>

            <div className="tabs">
              <button className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
                onClick={() => setActiveTab('overview')}><span className="icon">📊</span> Overview</button>
              <button className={`tab ${activeTab === 'chatbots' ? 'active' : ''}`}
                onClick={() => setActiveTab('chatbots')}><span className="icon">💬</span> Chatbots</button>
              <button className={`tab ${activeTab === 'quizzes' ? 'active' : ''}`}
                onClick={() => setActiveTab('quizzes')}><span className="icon">📝</span> Quizzes</button>
              <button className={`tab ${activeTab === 'assignments' ? 'active' : ''}`}
                onClick={() => setActiveTab('assignments')}><span className="icon">📋</span> Assignments</button>
              <button className={`tab ${activeTab === 'achievements' ? 'active' : ''}`}
                onClick={() => setActiveTab('achievements')}><span className="icon">🏆</span> Achievements</button>
            </div>

            <div className="tab-content">
              {activeTab === 'overview' && (
                <OverviewTab
                  dashboard={dashboard}
                  selectedCourse={selectedCourse}
                />
              )}
              {activeTab === 'chatbots' && selectedCourse && (
                <ChatbotsTab course={selectedCourse} />
              )}
              {activeTab === 'quizzes' && selectedCourse && (
                <QuizzesTab courseId={selectedCourse.id} />
              )}
              {activeTab === 'assignments' && selectedCourse && (
                <AssignmentsTab courseId={selectedCourse.id} />
              )}
              {activeTab === 'achievements' && (
                <AchievementsTab achievements={dashboard?.achievements} />
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Overview Tab
const OverviewTab = ({ dashboard, selectedCourse }) => (
  <div className="overview-tab">
    <div className="course-info-card">
      <h3>[#] {selectedCourse?.name}</h3>
      <p>Teacher: {selectedCourse?.teacher}</p>
      <div className="course-stats">
        <span>Quizzes: {selectedCourse?.quiz_count || 0}</span>
        <span>Assignments: {selectedCourse?.assignment_count || 0}</span>
      </div>
    </div>

    <div className="recent-activity">
      <h3>Recent Quiz Attempts</h3>
      {dashboard?.recent_attempts?.length > 0 ? (
        <div className="attempts-list">
          {dashboard.recent_attempts.map((attempt, idx) => (
            <div key={idx} className="attempt-card">
              <div className="attempt-info">
                <h4>{attempt.quiz_title}</h4>
                <span className="attempt-date">
                  {new Date(attempt.started_at).toLocaleDateString()}
                </span>
              </div>
              <div className="attempt-score">
                <span className="score-value">
                  {attempt.score?.toFixed(0) || 0}/{attempt.max_score}
                </span>
                <span className={`score-percent ${(attempt.score / attempt.max_score * 100) >= 70 ? 'good' :
                  (attempt.score / attempt.max_score * 100) >= 50 ? 'ok' : 'poor'
                  }`}>
                  {((attempt.score / attempt.max_score) * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="empty-state">No quiz attempts yet. Start learning!</p>
      )}
    </div>
  </div>
);

// Quizzes Tab
const QuizzesTab = ({ courseId }) => {
  const [quizzes, setQuizzes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [takingQuiz, setTakingQuiz] = useState(null);
  const [quizData, setQuizData] = useState(null);
  const [answers, setAnswers] = useState({});

  useEffect(() => {
    loadQuizzes();
  }, [courseId]);

  const loadQuizzes = async () => {
    try {
      const response = await studentAPI.getQuizzes(courseId);
      setQuizzes(response.data);
    } catch (error) {
      console.error('Error loading quizzes:', error);
    } finally {
      setLoading(false);
    }
  };

  const startQuiz = async (quizId) => {
    try {
      const response = await studentAPI.startQuiz(quizId);
      setQuizData(response.data);
      setTakingQuiz(quizId);
      setAnswers({});
    } catch (error) {
      alert('Error: ' + (error.response?.data?.detail || 'Could not start quiz'));
    }
  };

  const submitQuiz = async () => {
    if (!quizData?.attempt_id) return;
    try {
      const response = await studentAPI.submitQuiz(quizData.attempt_id, answers);
      alert(`Quiz submitted! Score: ${response.data.score}/${response.data.max_score} (${response.data.percentage.toFixed(0)}%)`);
      setTakingQuiz(null);
      setQuizData(null);
      loadQuizzes();
    } catch (error) {
      alert('Error submitting: ' + (error.response?.data?.detail || 'Submission failed'));
    }
  };

  if (loading) return <div className="loading">Loading quizzes...</div>;

  // Quiz Taking Interface
  if (takingQuiz && quizData) {
    return (
      <div className="quiz-taking">
        <div className="quiz-header">
          <h2>{quizData.quiz_title}</h2>
          <div className="quiz-meta">
            <span>Time: {quizData.time_limit} min</span>
            <span>Questions: {quizData.questions?.length || 0}</span>
          </div>
        </div>

        <div className="questions-list">
          {quizData.questions?.map((q, idx) => (
            <div key={q.id} className="question-card">
              <div className="question-number">Q{idx + 1}</div>
              <div className="question-content">
                <p className="question-text">{q.question_text}</p>

                {q.question_type === 'mcq' && q.options && (
                  <div className="options-list">
                    {(Array.isArray(q.options) ? q.options : JSON.parse(q.options)).map((opt, i) => (
                      <label key={i} className="option-label">
                        <input
                          type="radio"
                          name={`q_${q.id}`}
                          checked={answers[q.id] === opt}
                          onChange={() => setAnswers({ ...answers, [q.id]: opt })}
                        />
                        <span>{opt}</span>
                      </label>
                    ))}
                  </div>
                )}

                {q.question_type === 'true_false' && (
                  <div className="options-list">
                    {['True', 'False'].map(opt => (
                      <label key={opt} className="option-label">
                        <input
                          type="radio"
                          name={`q_${q.id}`}
                          checked={answers[q.id] === opt}
                          onChange={() => setAnswers({ ...answers, [q.id]: opt })}
                        />
                        <span>{opt}</span>
                      </label>
                    ))}
                  </div>
                )}

                {q.question_type === 'short_answer' && (
                  <textarea
                    className="short-answer"
                    placeholder="Type your answer..."
                    value={answers[q.id] || ''}
                    onChange={(e) => setAnswers({ ...answers, [q.id]: e.target.value })}
                  />
                )}
              </div>
              <div className="question-points">{q.points} pts</div>
            </div>
          ))}
        </div>

        <div className="quiz-actions">
          <button className="btn btn-secondary" onClick={() => setTakingQuiz(null)}>
            Cancel
          </button>
          <button className="btn btn-primary" onClick={submitQuiz}>
            ✅ Submit Quiz
          </button>
        </div>
      </div>
    );
  }

  // Quiz List
  return (
    <div className="quizzes-tab">
      <h3>Available Quizzes</h3>
      {quizzes.length > 0 ? (
        <div className="quiz-list">
          {quizzes.map(quiz => (
            <div key={quiz.id} className="quiz-card">
              <div className="quiz-info">
                <h4>{quiz.title}</h4>
                <p>{quiz.description}</p>
                <div className="quiz-meta">
                  <span>⏱ {quiz.time_limit_minutes} min</span>
                  <span>📝 {quiz.question_count} questions</span>
                  <span>🎯 {quiz.attempts_remaining} attempts left</span>
                </div>
                <div className="quiz-action">
                  {quiz.active_attempt_id ? (
                    <button
                      onClick={() => startQuiz(quiz.id)}
                      className="btn btn-warning"
                    >
                      ▶️ Resume Quiz
                    </button>
                  ) : quiz.can_attempt ? (
                    <button
                      onClick={() => startQuiz(quiz.id)}
                      className="btn btn-primary"
                    >
                      ▶️ Start Quiz
                    </button>
                  ) : (
                    <button className="btn btn-disabled" disabled>
                      ❌ No attempts
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="empty-state">No quizzes available for this course yet.</p>
      )}
    </div>
  );
};

// Assignments Tab
const AssignmentsTab = ({ courseId }) => {
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(null);
  const [content, setContent] = useState('');
  const [file, setFile] = useState(null);
  const [submissionMode, setSubmissionMode] = useState('text'); // 'text' or 'file'

  useEffect(() => {
    loadAssignments();
  }, [courseId]);

  const loadAssignments = async () => {
    try {
      const response = await studentAPI.getAssignments(courseId);
      // Backend returns "submitted boolean" and submission details flattened mostly, 
      // but let's assume we map "submitted" properly in frontend or backend wrapper.
      // Based on student.py list_course_assignments: 
      // returns { id, title..., submitted: bool, score, feedback } 
      // But looking at JSX below: assignment.submission.score used. 
      // The backend returns "score" directly on the object, not nested in "submission".
      // Let's adjust access below or trust existing code? 
      // Existing code uses assignment.submission.score. Backend returns: { ..., score: ..., } 
      // So assignment.score would be the score. 
      // Wait, let's fix the mapping in loadAssignments just in case, or fix the JSX.
      // Actually, looking at existing code: assignment.submission ? ... assignment.submission.score
      // The backend returns: { ..., submitted: bool, score: ..., }
      // So "assignment.submission" is unlikely to be populated unless I map it.
      // The backend returns a flat object.
      // Let's stick to modifying the SUBMISSION LOGIC mostly, but the JSX for existing submission might be creating a weird object.
      // I'll assume response.data is what we use.
      setAssignments(response.data);
    } catch (error) {
      console.error('Error loading assignments:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (assignmentId) => {
    const formData = new FormData();

    if (submissionMode === 'text') {
      if (!content.trim()) {
        alert('Please enter your submission text');
        return;
      }
      formData.append('content', content);
    } else {
      if (!file) {
        alert('Please select a file to upload');
        return;
      }
      formData.append('file', file);
    }

    try {
      await studentAPI.submitAssignment(assignmentId, formData);
      alert('Assignment submitted! ' + (submissionMode === 'file' ? 'File uploaded.' : 'AI will evaluate text.'));
      setSubmitting(null);
      setContent('');
      setFile(null);
      loadAssignments();
    } catch (error) {
      alert('Error: ' + (error.response?.data?.detail || 'Submission failed'));
    }
  };

  if (loading) return <div className="loading">Loading assignments...</div>;

  return (
    <div className="assignments-tab">
      <h3>Assignments</h3>
      {assignments.length > 0 ? (
        <div className="assignment-list">
          {assignments.map(assignment => (
            <div key={assignment.id} className="assignment-card">
              <div className="assignment-info">
                <h4>{assignment.title}</h4>
                <div style={{ whiteSpace: 'pre-wrap', marginBottom: '10px' }}>{assignment.description}</div>
                <div className="assignment-meta">
                  <span>📊 Max: {assignment.max_score} pts</span>
                  <span>📅 Due: {assignment.due_date ? new Date(assignment.due_date).toLocaleDateString() : 'No Limit'}</span>
                </div>
              </div>

              {assignment.submitted ? (
                <div className="submission-status">
                  <span className="submitted">✅ Submitted</span>
                  {assignment.score !== null && (
                    <span className="score">
                      Score: {assignment.score}/{assignment.max_score}
                    </span>
                  )}
                  {assignment.feedback && <div className="feedback">Teacher Feedback: {assignment.feedback}</div>}
                </div>
              ) : (
                <>
                  {submitting === assignment.id ? (
                    <div className="submission-form" style={{ marginTop: '15px', padding: '15px', background: '#2a2a2a', borderRadius: '8px' }}>
                      <div className="mode-toggle" style={{ marginBottom: '10px', display: 'flex', gap: '15px' }}>
                        <label style={{ cursor: 'pointer' }}>
                          <input
                            type="radio"
                            checked={submissionMode === 'text'}
                            onChange={() => setSubmissionMode('text')}
                            style={{ marginRight: '5px' }}
                          />
                          Type Answer
                        </label>
                        <label style={{ cursor: 'pointer' }}>
                          <input
                            type="radio"
                            checked={submissionMode === 'file'}
                            onChange={() => setSubmissionMode('file')}
                            style={{ marginRight: '5px' }}
                          />
                          Upload File
                        </label>
                      </div>

                      {submissionMode === 'text' ? (
                        <textarea
                          value={content}
                          onChange={(e) => setContent(e.target.value)}
                          placeholder="Write your answer here..."
                          rows={5}
                          className="form-control"
                          style={{ width: '100%', marginBottom: '10px' }}
                        />
                      ) : (
                        <div className="file-upload-area" style={{ marginBottom: '10px', padding: '20px', border: '2px dashed #666', borderRadius: '5px', textAlign: 'center' }}>
                          <input
                            type="file"
                            onChange={(e) => setFile(e.target.files[0])}
                            accept=".pdf,.txt,.doc,.docx"
                          />
                          <p style={{ marginTop: '5px', fontSize: '0.9em', color: '#aaa' }}>Supported: PDF, Text, Doc</p>
                        </div>
                      )}

                      <div className="form-actions" style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                        <button className="btn btn-secondary" onClick={() => { setSubmitting(null); setContent(''); setFile(null); }}>
                          Cancel
                        </button>
                        <button className="btn btn-primary" onClick={() => handleSubmit(assignment.id)}>
                          Submit
                        </button>
                      </div>
                    </div>
                  ) : (
                    <button
                      className="btn btn-primary"
                      onClick={() => setSubmitting(assignment.id)}
                    >
                      📤 Submit Assignment
                    </button>
                  )}
                </>
              )}
            </div>
          ))}
        </div>
      ) : (
        <p className="empty-state">No assignments for this course yet.</p>
      )}
    </div>
  );
};

// Achievements Tab
const AchievementsTab = ({ achievements }) => (
  <div className="achievements-tab">
    <h3>🏆 Your Achievements</h3>
    {achievements?.length > 0 ? (
      <div className="achievements-grid">
        {achievements.map(achievement => (
          <div
            key={achievement.id}
            className={`achievement-card ${achievement.earned ? 'earned' : 'locked'}`}
          >
            <span className="achievement-icon">{achievement.badge_icon}</span>
            <h4>{achievement.name}</h4>
            <p>{achievement.description}</p>
            <span className="achievement-xp">+{achievement.xp_reward} XP</span>
          </div>
        ))}
      </div>
    ) : (
      <p className="empty-state">Complete activities to earn achievements!</p>
    )}
  </div>
);

// Chatbots Tab
const ChatbotsTab = ({ course }) => {
  const navigate = useNavigate();
  return (
    <div className="chatbots-tab">
      <div className="grid-container">
        {course.chatbots?.length > 0 ? (
          course.chatbots.map(bot => (
            <div key={bot.id} className="resource-card chatbot-card">
              <div className="card-header">
                <h3>{bot.name}</h3>
                <span className="badge ai-badge">{bot.provider}</span>
              </div>
              <p>{bot.description || 'Your AI tutor for this course.'}</p>
              <div className="card-footer">
                <button
                  className="btn btn-primary btn-full"
                  onClick={() => navigate('/student/chatbot', {
                    state: { courseId: course.id, chatbotId: bot.id }
                  })}
                >
                  Start Chat 💬
                </button>
              </div>
            </div>
          ))
        ) : (
          <div className="empty-state">
            <p>No AI chatbots assigned to this course yet.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default StudentDashboard;
