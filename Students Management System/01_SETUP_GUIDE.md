# Cloud-Based Student Data Management System - Setup Guide

## 📋 Project Overview
This is a **secure, role-based student data management system** built with:
- **Backend**: FastAPI (Python web framework)
- **Database**: PostgreSQL (local)
- **Authentication**: JWT tokens
- **Authorization**: Role-based access (Admin, Teacher, Student)

---

## 🔧 Prerequisites
Before starting, install these on your system:

1. **Python 3.8+** - Download from python.org
2. **PostgreSQL** - Download from postgresql.org
3. **Git** - Download from git-scm.com

---

## 📦 Step 1: Install Dependencies

### 1.1 Create a Project Folder
```bash
mkdir student-data-management
cd student-data-management
```

### 1.2 Create a Virtual Environment
A virtual environment keeps your project dependencies isolated.

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 1.3 Install Required Libraries
Create a file called `requirements.txt` and add:

```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose==3.3.0
passlib==1.7.4
python-multipart==0.0.6
python-dotenv==1.0.0
```

Then install them:
```bash
pip install -r requirements.txt
```

---

## 🗄️ Step 2: Set Up PostgreSQL Database

### 2.1 Start PostgreSQL Service
- **Windows**: PostgreSQL runs as a service automatically
- **Mac**: `brew services start postgresql`
- **Linux**: `sudo service postgresql start`

### 2.2 Create Database and User

**IMPORTANT**: Run these queries **exactly in this order** in PostgreSQL terminal!

#### **Open PostgreSQL Terminal**

**Windows** (PowerShell):
```bash
psql -U postgres
```

**Mac/Linux**:
```bash
sudo -u postgres psql
```

If asked for password, use your PostgreSQL admin password.

---

#### **Run These Queries (Copy & Paste ALL of them)**

```sql
-- ============================================
-- STEP 1: CREATE DATABASE
-- ============================================
CREATE DATABASE student_management_db;

-- ============================================
-- STEP 2: CREATE USER
-- ============================================
CREATE USER student_admin WITH PASSWORD 'admin123';

-- ============================================
-- STEP 3: GRANT PRIVILEGES TO USER
-- ============================================
ALTER USER student_admin WITH CREATEDB CREATEROLE SUPERUSER;

-- ============================================
-- STEP 4: GRANT DATABASE PRIVILEGES
-- ============================================
GRANT ALL PRIVILEGES ON DATABASE student_management_db TO student_admin;

-- ============================================
-- STEP 5: SWITCH TO THE DATABASE
-- ============================================
\c student_management_db

-- ============================================
-- STEP 6: GRANT SCHEMA PERMISSIONS (FIXES "permission denied" ERROR!)
-- ============================================
GRANT ALL ON SCHEMA public TO student_admin;
GRANT CREATE ON SCHEMA public TO student_admin;

-- ============================================
-- STEP 7: GRANT DEFAULT PRIVILEGES (FOR FUTURE OBJECTS)
-- ============================================
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO student_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO student_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO student_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TYPES TO student_admin;

-- ============================================
-- STEP 8: GRANT ALL EXISTING PRIVILEGES
-- ============================================
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO student_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO student_admin;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO student_admin;

-- ============================================
-- STEP 9: SET DATABASE OWNER
-- ============================================
ALTER DATABASE student_management_db OWNER TO student_admin;

-- ============================================
-- STEP 10: VERIFY PERMISSIONS (Optional)
-- ============================================
-- If you want to check permissions, run this:
SELECT grantee, privilege_type 
FROM information_schema.role_table_grants 
WHERE table_name='public';
```

---

#### **⚠️ CRITICAL INSTRUCTIONS**

1. **Copy ALL 10 queries above** (don't skip any!)
2. **Paste into PostgreSQL terminal** one by one, or all at once
3. **Wait for each to complete** before moving to next
4. **Make sure you see `student_management_db=#`** before running steps 6-9
5. **If you get errors**, check troubleshooting section below

---

#### **Expected Output**

Each query should respond with:
```
CREATE DATABASE
CREATE ROLE
ALTER ROLE
GRANT
\c student_management_db
GRANT
...
```

**No errors should appear!** If you see errors, see troubleshooting below.

### 2.3 Verify Connection

```bash
psql -U student_admin -d student_management_db -h localhost
```

**Expected output**: You should see `student_management_db=#` prompt

Type `\q` to exit if successful.

---

### 2.4 Troubleshooting PostgreSQL Errors

#### **Error: "permission denied for schema public"**

If you get this error when running the app, it means permissions weren't set correctly.

**Solution**: Run this in PostgreSQL:

```sql
-- Connect to the database first
\c student_management_db

-- Then run these:
GRANT ALL ON SCHEMA public TO student_admin;
GRANT CREATE ON SCHEMA public TO student_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TYPES TO student_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO student_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO student_admin;

-- Verify
\dp public
```

---

#### **Error: "role 'student_admin' does not exist"**

**Solution**: Create the user first:

```sql
-- Create user
CREATE USER student_admin WITH PASSWORD 'admin123';

-- Give privileges
ALTER USER student_admin WITH CREATEDB CREATEROLE SUPERUSER;

-- Grant database access
GRANT ALL PRIVILEGES ON DATABASE student_management_db TO student_admin;
```

---

#### **Error: "database 'student_management_db' does not exist"**

**Solution**: Create the database:

```sql
-- Create database
CREATE DATABASE student_management_db;

-- Set owner
ALTER DATABASE student_management_db OWNER TO student_admin;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE student_management_db TO student_admin;
```

---

#### **Error: "password authentication failed"**

This means the password is wrong or the user doesn't exist.

**Solution**: Reset the user password:

```sql
-- Change password
ALTER USER student_admin WITH PASSWORD 'admin123';

-- Verify user exists
\du

-- You should see: student_admin | ... in the list
```

---

#### **Starting Fresh (Clean Installation)**

If everything is broken, start fresh:

```sql
-- Drop everything (CAREFUL!)
DROP DATABASE IF EXISTS student_management_db;
DROP USER IF EXISTS student_admin;

-- Create from scratch
CREATE DATABASE student_management_db;
CREATE USER student_admin WITH PASSWORD 'admin123';
ALTER USER student_admin WITH CREATEDB CREATEROLE SUPERUSER;
GRANT ALL PRIVILEGES ON DATABASE student_management_db TO student_admin;

-- Connect and set permissions
\c student_management_db

GRANT ALL ON SCHEMA public TO student_admin;
GRANT CREATE ON SCHEMA public TO student_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TYPES TO student_admin;
```

---

#### **Verify Everything Works**

```sql
-- Check if user exists and has permissions
\du student_admin

-- Check database permissions
\l student_management_db

-- Connect to database
\c student_management_db

-- Check schema permissions
\dn

-- Should show: public | student_admin | ...
```

If you see `student_admin` with full permissions, you're good! ✅

---

## 📁 Step 3: Project Structure

Create these files in your project folder:

```
student-data-management/
├── main.py                 # Main application file
├── database.py            # Database configuration
├── models.py              # Database models (Student, User, etc.)
├── schemas.py             # Input/Output data structures
├── auth.py                # Authentication logic
├── routes/
│   ├── __init__.py
│   ├── students.py        # Student endpoints
│   ├── users.py           # User management
│   └── auth.py            # Login/Register
├── .env                   # Environment variables (SECRET!)
├── requirements.txt       # Dependencies
└── README.md              # Documentation
```

---

## 🔐 Step 4: Create Environment File

Create `.env` file in your project root:

```
DATABASE_URL=postgresql://student_admin:admin123@localhost/student_management_db
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**⚠️ Important**: 
- Change `SECRET_KEY` to something secure
- Never commit `.env` to GitHub
- Add `.env` to `.gitignore`

---

## ▶️ Step 5: Running the Application

1. Make sure your virtual environment is activated
2. Make sure PostgreSQL is running
3. Run the server:

```bash
uvicorn main:app --reload
```

You should see:
```
Uvicorn running on http://127.0.0.1:8000
```

4. Open your browser and go to:
   - **API Docs (Interactive)**: http://localhost:8000/docs
   - **Alternative Docs**: http://localhost:8000/redoc

---

## 📝 What's Next?

Follow these steps in order:
1. ✅ Complete this setup guide
2. 📄 Copy `database.py` file
3. 🗄️ Copy `models.py` file
4. 🔐 Copy `auth.py` file
5. 📋 Copy `schemas.py` file
6. 🚀 Copy `main.py` file
7. 🧪 Test the API endpoints

---

## 🧪 Quick Test

Once running, test a simple endpoint:

```bash
# In a new terminal (venv still activated)
curl http://localhost:8000/health
```

You should get: `{"status":"ok"}`

---

## ❓ Common Issues

### "ModuleNotFoundError: No module named 'fastapi'"
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

### "psycopg2 error" or database connection fails
- Check PostgreSQL is running
- Verify credentials in `.env` match your database
- Check if database exists: `psql -l`

### Port 8000 already in use
```bash
uvicorn main:app --reload --port 8001
```

---

## 📚 Learning Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy ORM**: https://docs.sqlalchemy.org/
- **PostgreSQL**: https://www.postgresql.org/docs/

---

You're ready to start coding! Let's begin with `database.py` →
