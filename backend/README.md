# Ruman Backend Setup

## Prerequisites
- Python 3.10 or higher ✅ (You have 3.13.5)
- pip

## Installation

### 1. Create Virtual Environment (Recommended)
```bash
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on Mac/Linux
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the backend directory:
```bash
cp .env.example .env
```

Then edit `.env` and add your Gemini API key:
```
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### 4. Initialize Database
```bash
python init_db.py
```

Choose option 1 to create a fresh database with sample data.

**Default Users Created:**
- **Admin**: username=`admin`, password=`admin123`
- **Teacher**: username=`teacher1`, password=`teacher123`
- **Student**: username=`student1`, password=`student123`

### 5. Run the Server
```bash
python app.py

# Or with uvicorn directly
uvicorn app:app --reload
```

The API will be available at: **http://localhost:8000**

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
backend/
├── ai_services/           # AI/ML services
│   ├── rag_system.py      # RAG implementation
│   └── ml_models.py       # ML models
├── routes/                # API endpoints
│   ├── auth.py           # Authentication routes
│   ├── teacher.py        # Teacher routes
│   └── student.py        # Student routes
├── app.py                # Main FastAPI application
├── models.py             # SQLAlchemy ORM models
├── schemas.py            # Pydantic schemas
├── database.py           # Database configuration
├── config.py             # Settings
├── init_db.py            # Database initialization
└── requirements.txt      # Python dependencies
```

## Database

The application uses **SQLite** by default (file: `ruman.db`).

To reset the database:
```bash
python init_db.py
# Choose option 2
```

## Testing

### Authentication Tests
```bash
# Run authentication test script
python test_auth.py
```

This will test:
- ✅ User registration
- ✅ Login with JWT token
- ✅ Token validation
- ✅ Error handling

### Manual Testing
Visit **http://localhost:8000/docs** for interactive API testing.

1. Click "Authorize" button
2. Login with default credentials
3. Test all endpoints

### Testing Dependencies
```bash
# Install testing dependencies (if not already installed)
pip install pytest httpx requests

# Run tests (when available)
pytest tests/
```

## Authentication

The system uses **JWT tokens** for authentication. See [AUTHENTICATION.md](../docs/AUTHENTICATION.md) for complete details.

### Quick Test:
```bash
# Test with curl (Windows PowerShell)
# Login
curl -X POST http://localhost:8000/api/auth/login `
  -H "Content-Type: application/x-www-form-urlencoded" `
  -d "username=admin&password=admin123"

# Copy the access_token from response, then:
curl -X GET http://localhost:8000/api/auth/me `
  -H "Authorization: Bearer <paste_token_here>"
```

## API Documentation

Once running, visit:

```bash
# Install testing dependencies (if not already installed)
pip install pytest httpx

# Run tests (when available)
pytest tests/
```

## Troubleshooting

### Module Import Errors
Make sure you're in the backend directory and the virtual environment is activated.

### Database Errors
Delete `ruman.db` and run `python init_db.py` again.

### Port Already in Use
Change the port in `app.py` or kill the process using port 8000:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Mac/Linux
lsof -t -i:8000 | xargs kill
```

## Next Steps

After Phase 3 (Authentication), you'll be able to:
1. Register new users
2. Login and receive JWT tokens
3. Access protected endpoints
