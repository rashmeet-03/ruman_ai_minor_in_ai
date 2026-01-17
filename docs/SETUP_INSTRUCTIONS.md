# Setup Instructions

## Backend Setup
1. Create virtual environment: `python -m venv venv`
2. Activate: `source venv/bin/activate`
3. Install: `pip install -r requirements.txt`
4. Run: `uvicorn app:app --reload`

## Frontend Setup
1. Install: `npm install`
2. Run: `npm start`

## Database
1. Create database: `createdb ruman_db`
2. Run migrations: `alembic upgrade head`

Access at http://localhost:3000
