# Scholarly Insight Backend

This is the backend API for Scholarly Insight, a platform for exploring and interacting with scholarly articles from arXiv.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Setup](#setup)
  - [1. PostgreSQL Setup](#1-postgresql-setup)
  - [2. Firebase Setup](#2-firebase-setup)
  - [3. Environment Configuration](#3-environment-configuration)
  - [4. Database Migrations](#4-database-migrations)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)

## Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Firebase account (free tier works fine)

## Setup

### 1. PostgreSQL Setup

#### Installation

**macOS (using Homebrew):**
```bash
brew install postgresql
brew services start postgresql
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**Windows:**
Download and install from [PostgreSQL official website](https://www.postgresql.org/download/windows/)

#### Create Database and User

1. Access PostgreSQL command line:
```bash
# macOS/Linux
sudo -u postgres psql

# Windows
psql -U postgres
```

2. Create a database and user:
```sql
CREATE DATABASE scholarly;
CREATE USER myuser WITH ENCRYPTED PASSWORD 'mypassword';
GRANT ALL PRIVILEGES ON DATABASE scholarly TO myuser;
```

3. Make note of your database name, username, and password for the `.env` file

### 2. Firebase Setup

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project
3. Enable Email/Password Authentication:
   - In the Firebase console, go to "Authentication" > "Sign-in method"
   - Enable "Email/Password" provider
4. Generate Firebase Admin SDK credentials:
   - Go to "Project settings" > "Service accounts"
   - Click "Generate new private key"
   - Save the JSON file securely
5. Get Firebase Web API Key:
   - Go to "Project settings" > "General"
   - Copy the "Web API Key"

### 3. Environment Configuration

1. Create a `.env` file in the `backend` directory:
```bash
cp .env.example .env
```

2. Open the `.env` file and fill in your details:
```
DATABASE_URL=postgresql://myuser:mypassword@localhost:5432/scholarly
SECRET_KEY=your-generated-secret-key
FIREBASE_CREDENTIALS={"type": "service_account", "project_id": "...", "private_key_id": "...", ...}
FIREBASE_WEB_API_KEY=your-firebase-web-api-key
```

Notes:
- For `SECRET_KEY`, you can generate one with: `openssl rand -hex 32`
- For `FIREBASE_CREDENTIALS`, copy the entire content of the downloaded JSON file
- `FIREBASE_WEB_API_KEY` is from your Firebase project settings

### 4. Database Migrations

Initialize and run migrations using Alembic:

```bash
# Install requirements first
pip install -r requirements.txt

# Run migrations
alembic upgrade head
```

## Running the Application

1. Activate your virtual environment (if you're using one):
```bash
# Create virtual environment (if not already created)
python -m venv venv

# Activate virtual environment
# macOS/Linux
source venv/bin/activate
# Windows
venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

The API should now be running at http://localhost:8000

## API Documentation

Once the server is running, API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── alembic/                  # Database migration files
├── app/
│   ├── api/                  # API endpoints
│   │   └── v1/
│   │       └── endpoints/    # API route handlers
│   ├── core/                 # Core functionality
│   │   ├── config.py         # Application configuration
│   │   ├── database.py       # Database connection
│   │   └── firebase.py       # Firebase integration
│   ├── models/               # SQLAlchemy models
│   ├── schemas/              # Pydantic models/schemas
│   ├── services/             # Business logic
│   └── main.py               # FastAPI application
├── .env                      # Environment variables (create from .env.example)
├── .env.example              # Example environment variables
├── alembic.ini               # Alembic configuration
└── requirements.txt          # Python dependencies
```

## Modifying the Project

### Where to Make Changes

- **Add new models**: Create new files in `app/models/` directory
- **Add new API endpoints**: Add new files in `app/api/v1/endpoints/` and include them in `app/main.py`
- **Change database schema**: Create new migrations with `alembic revision --autogenerate -m "description"`
- **Add business logic**: Add new service functions in `app/services/` directory

### Common Tasks

#### Creating a New Endpoint

1. Create a new file in `app/api/v1/endpoints/`
2. Define your router and endpoints
3. Include the router in `app/main.py`

#### Adding a New Model

1. Create or update files in `app/models/`
2. Create a migration: `alembic revision --autogenerate -m "Add new model"`
3. Apply the migration: `alembic upgrade head`

#### Adding Firebase Authentication to a New Endpoint

Use the `get_current_user` dependency:

```python
from app.api.deps import get_current_user

@router.get("/protected-route")
async def protected_route(current_user = Depends(get_current_user)):
    return {"message": "This is protected", "user_id": current_user.id}
```
