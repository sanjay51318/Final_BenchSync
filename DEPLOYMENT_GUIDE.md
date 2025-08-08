# Local Deployment Guide

## Prerequisites

Before deploying the application locally, ensure you have the following installed:

1. **Python 3.8+** - For the FastAPI backend
2. **Node.js 18+** - For the React frontend

## Quick Start

### 1. Backend Setup

#### Install Python Dependencies

```bash
# Navigate to project root
cd "c:/Users/Sanjay N/langchain-mcp-agents"

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Initialize Database

```bash
# Run database initialization
python init_complete_database.py

# Verify database setup
python test_database_integration.py
```

### 4. Frontend Setup

#### Install Node.js Dependencies

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
# or if you prefer yarn:
yarn install
```

### 5. Start the Application

#### Option A: Start Services Individually

**Terminal 1 - Backend:**

```bash
# From project root
cd "c:/Users/Sanjay N/langchain-mcp-agents"
python simple_backend.py
```

**Terminal 2 - Frontend:**

```bash
# From frontend directory
cd frontend
npm run dev
```

#### Option B: Use Start Scripts (Create them first)

Create `start_fullstack.bat` in project root:

```batch
@echo off
echo Starting Consultant Bench Management System...

echo Starting Backend...
start cmd /k "cd /d "%~dp0" && python simple_backend.py"

timeout /t 5

echo Starting Frontend...
start cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo Both services are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
pause
```

## Access Points

Once deployed successfully:

- **Frontend Application**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Profile Page**: http://localhost:3000/profile

## Verification Steps

1. **Check Backend Health**:

   ```bash
   curl http://localhost:8000/health
   ```

2. **Check Frontend Loading**:
   Open http://localhost:3000 in your browser

3. **Test Profile System**:
   - Navigate to http://localhost:3000/profile
   - For consultants: Should see enhanced profile with resume upload
   - For admins: Should see admin profile interface

## Common Issues & Solutions

### Backend Issues

**Port Already in Use:**

```bash
# Find process using port 8000
netstat -ano | findstr :8000
# Kill the process
taskkill /PID <process_id> /F
```

**Database Connection Error:**

- Verify PostgreSQL is running
- Check database credentials in `.env`
- Ensure database exists

**Import Errors:**

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Frontend Issues

**Node Modules Issues:**

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Port 3000 in Use:**

```bash
# Frontend will automatically use next available port (3001, 3002, etc.)
# Or specify a different port:
npm run dev -- --port 3001
```

### Database Issues

**Connection Refused:**

- Start PostgreSQL service
- Check if database server is running on port 5432

**Permission Denied:**

- Verify user permissions
- Check database name and credentials

## Development Workflow

1. **Start Development Environment**:

   ```bash
   # Terminal 1: Backend with auto-reload
   uvicorn simple_backend:app --reload --host 0.0.0.0 --port 8000

   # Terminal 2: Frontend with hot reload
   cd frontend && npm run dev
   ```

2. **Database Updates**:

   ```bash
   # After model changes
   python recreate_database.py
   ```

3. **Testing**:

   ```bash
   # Backend tests
   python -m pytest tests/

   # Frontend tests (if configured)
   cd frontend && npm test
   ```

## Production Considerations

For production deployment:

1. **Environment Variables**:

   - Set `DEBUG=False`
   - Use secure `SECRET_KEY`
   - Configure proper CORS origins

2. **Database**:

   - Use production PostgreSQL instance
   - Enable SSL connections
   - Regular backups

3. **Frontend**:

   ```bash
   npm run build
   npm run preview
   ```

4. **Reverse Proxy**:
   - Use Nginx or Apache
   - SSL certificates
   - Load balancing if needed

## Support

If you encounter issues:

1. Check the logs in the `logs/` directory
2. Verify all prerequisites are installed
3. Ensure environment variables are set correctly
4. Check that all services are running on expected ports
