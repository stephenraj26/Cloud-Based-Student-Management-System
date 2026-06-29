# 📚 Cloud-Based Student Data Management System

A secure, production-ready REST API built with **FastAPI** and **PostgreSQL** for managing student records with role-based access control.

---

## 🎯 Project Overview

### Features
✅ **User Management** - Register, login, manage users
✅ **Role-Based Access Control** - Admin, Teacher, Student roles
✅ **Student Management** - Complete CRUD operations for student records
✅ **Security** - Password hashing, JWT authentication, role-based authorization
✅ **Database** - PostgreSQL with proper relationships and constraints
✅ **API Documentation** - Interactive Swagger/OpenAPI docs
✅ **Pagination & Filtering** - Efficient data retrieval
✅ **Error Handling** - Comprehensive error messages

### Tech Stack
- **Backend**: FastAPI (Python web framework)
- **Database**: PostgreSQL (relational database)
- **Authentication**: JWT (JSON Web Tokens)
- **Password Security**: Bcrypt hashing
- **Validation**: Pydantic (automatic input validation)

---

## 📋 Project Structure

```
student-data-management/
├── main.py                 # Main FastAPI application
├── database.py            # Database connection setup
├── models.py              # SQLAlchemy models (database tables)
├── schemas.py             # Pydantic schemas (request/response validation)
├── auth.py                # Authentication and authorization logic
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (SECRET - don't commit!)
├── .env.example          # Template for .env file
└── README.md             # This file
```

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8+
- PostgreSQL installed and running
- Git (optional)

### 2. Setup Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup PostgreSQL Database

Open PostgreSQL command line:
```sql
-- Create database
CREATE DATABASE student_management_db;

-- Create user
CREATE USER student_admin WITH PASSWORD 'admin123';

-- Grant permissions
ALTER ROLE student_admin WITH CREATEDB;
GRANT ALL PRIVILEGES ON DATABASE student_management_db TO student_admin;
```

### 5. Create .env File
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 6. Run the Application
```bash
uvicorn main:app --reload
```

You should see:
```
Uvicorn running on http://127.0.0.1:8000
```

### 7. Open Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📖 API Endpoints

### Health Check
```bash
GET /health
```

### Authentication

#### 1. Register New User
```bash
POST /auth/register
Content-Type: application/json

{
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "password": "securepass123",
    "role": "teacher"
}

Response: 201 Created
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "role": "teacher",
    "is_active": true,
    "created_at": "2025-01-15T10:30:00",
    "last_login": null
}
```

#### 2. Login
```bash
POST /auth/login
Content-Type: application/json

{
    "username": "john_doe",
    "password": "securepass123"
}

Response: 200 OK
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {...user data...}
}
```

**Save the access_token!** You'll need it for authenticated requests.

### User Management

#### 3. Get Current User Profile
```bash
GET /users/me
Authorization: Bearer <your_access_token>

Response: 200 OK
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    ...
}
```

#### 4. Get All Users (Admin Only)
```bash
GET /users
Authorization: Bearer <admin_token>

Response: 200 OK
[
    {
        "id": 1,
        "username": "john_doe",
        ...
    },
    {
        "id": 2,
        "username": "jane_smith",
        ...
    }
]
```

#### 5. Get User by ID (Admin Only)
```bash
GET /users/{user_id}
Authorization: Bearer <admin_token>
```

#### 6. Update User (Admin Only)
```bash
PATCH /users/{user_id}
Authorization: Bearer <admin_token>
Content-Type: application/json

{
    "full_name": "John Smith",
    "is_active": true
}
```

#### 7. Delete User (Admin Only)
```bash
DELETE /users/{user_id}
Authorization: Bearer <admin_token>

Response: 204 No Content
```

### Student Management

#### 8. Create Student (Admin/Teacher Only)
```bash
POST /students
Authorization: Bearer <teacher_token>
Content-Type: application/json

{
    "roll_number": "2023001",
    "name": "Arjun Kumar",
    "email": "arjun@college.com",
    "phone": "9876543210",
    "department": "Computer Science",
    "semester": 3,
    "gpa": "3.8",
    "address": "123 Main St",
    "city": "Chennai",
    "state": "Tamil Nadu",
    "pincode": "600001"
}

Response: 201 Created
{
    "id": 1,
    "roll_number": "2023001",
    "name": "Arjun Kumar",
    "email": "arjun@college.com",
    ...
    "created_by": 1,
    "created_at": "2025-01-15T10:30:00"
}
```

#### 9. Get All Students (With Pagination & Filtering)
```bash
GET /students?skip=0&limit=10&department=CSE&semester=3
Authorization: Bearer <token>

Response: 200 OK
{
    "total": 150,
    "count": 10,
    "students": [
        {
            "id": 1,
            "roll_number": "2023001",
            ...
        },
        ...
    ]
}
```

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Number of records to return (max: 100)
- `department`: Filter by department (optional)
- `semester`: Filter by semester (optional)

#### 10. Get Student by ID
```bash
GET /students/{student_id}
Authorization: Bearer <token>

Response: 200 OK
{
    "id": 1,
    "roll_number": "2023001",
    ...
}
```

**Rules:**
- ADMIN/TEACHER: Can access any student
- STUDENT: Can only access their own data

#### 11. Update Student (Admin/Teacher Only)
```bash
PATCH /students/{student_id}
Authorization: Bearer <teacher_token>
Content-Type: application/json

{
    "semester": 4,
    "gpa": "3.9"
}

Response: 200 OK
{...updated student data...}
```

#### 12. Delete Student (Admin Only)
```bash
DELETE /students/{student_id}
Authorization: Bearer <admin_token>

Response: 204 No Content
```

#### 13. Get Students by Department (Admin/Teacher Only)
```bash
GET /students/department/Computer%20Science
Authorization: Bearer <teacher_token>

Response: 200 OK
{
    "department": "Computer Science",
    "count": 45,
    "students": [...]
}
```

---

## 🧪 Testing with curl

### Complete Testing Workflow

```bash
# 1. Register as admin
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin_user",
    "email": "admin@example.com",
    "full_name": "Admin User",
    "password": "admin123",
    "role": "admin"
  }'

# 2. Register as teacher
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "teacher_user",
    "email": "teacher@example.com",
    "full_name": "Teacher User",
    "password": "teacher123",
    "role": "teacher"
  }'

# 3. Login as teacher (save the access_token from response)
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "teacher_user",
    "password": "teacher123"
  }'

# 4. Create a student (replace TEACHER_TOKEN with actual token)
curl -X POST http://localhost:8000/students \
  -H "Authorization: Bearer TEACHER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "roll_number": "2023001",
    "name": "Rahul Singh",
    "email": "rahul@example.com",
    "phone": "9876543210",
    "department": "Computer Science",
    "semester": 3,
    "gpa": "3.8",
    "city": "Chennai"
  }'

# 5. Get all students
curl -X GET "http://localhost:8000/students?skip=0&limit=10" \
  -H "Authorization: Bearer TEACHER_TOKEN"

# 6. Get specific student
curl -X GET http://localhost:8000/students/1 \
  -H "Authorization: Bearer TEACHER_TOKEN"

# 7. Update student
curl -X PATCH http://localhost:8000/students/1 \
  -H "Authorization: Bearer TEACHER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"semester": 4, "gpa": "3.9"}'

# 8. Get current user
curl -X GET http://localhost:8000/users/me \
  -H "Authorization: Bearer TEACHER_TOKEN"
```

---

## 🔐 Security Features

### 1. Password Hashing
- Passwords are hashed using **Bcrypt** (one-way encryption)
- Plain passwords are never stored in database
- Even if database is compromised, passwords are safe

### 2. JWT Authentication
- Users login to get a token
- Token contains: user ID, username, role, expiration time
- Token is signed with a secret key
- Each API request must include the token in Authorization header

### 3. Role-Based Access Control (RBAC)
- **ADMIN**: Full access to all features
- **TEACHER**: Can create and manage student records
- **STUDENT**: Can only view their own data

### 4. Input Validation
- All inputs are validated using Pydantic
- Invalid data is automatically rejected
- Prevents SQL injection and other attacks

---

## 📚 Learning Concepts

### 1. REST API Principles
- **GET**: Retrieve data
- **POST**: Create new data
- **PATCH**: Update existing data
- **DELETE**: Remove data

### 2. HTTP Status Codes
- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Invalid credentials
- `403 Forbidden`: Access denied
- `404 Not Found`: Resource doesn't exist
- `500 Server Error`: Server error

### 3. Database Concepts
- **Primary Key**: Unique identifier for each row
- **Foreign Key**: Links between tables
- **Index**: Speeds up queries
- **UNIQUE Constraint**: No duplicate values
- **NOT NULL**: Field must have a value

### 4. Authentication
- **JWT**: Standard way to send tokens
- **Bearer Token**: Format = "Bearer <token>"
- **Expiration**: Token expires after set time
- **Refresh**: Can request new token

---

## 🐛 Common Issues & Solutions

### Issue: "psycopg2: error: connection refused"
**Solution**: Make sure PostgreSQL is running
```bash
# Windows
Services app → PostgreSQL → Start

# Mac
brew services start postgresql

# Linux
sudo service postgresql start
```

### Issue: "ModuleNotFoundError: No module named 'fastapi'"
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: "UNIQUE constraint failed"
**Solution**: The value you're trying to insert already exists. Use a different value.

### Issue: "Invalid token" error
**Solution**: 
- Token may have expired (login again)
- Token may be malformed (copy it correctly)
- Header format must be: `Authorization: Bearer <token>`

### Issue: "Access denied" on creating student
**Solution**: Make sure you're logged in as ADMIN or TEACHER, not STUDENT

---

## 📝 Next Steps to Improve

1. **File Upload**: Add ability to upload student documents
2. **Email Notifications**: Send emails on student creation
3. **Audit Logging**: Log all changes for compliance
4. **Advanced Search**: Full-text search on student names
5. **Attendance System**: Track attendance records
6. **Grades Management**: Store and manage grades
7. **Export to Excel**: Export student records as CSV/Excel
8. **Dashboard**: Frontend dashboard showing statistics
9. **Two-Factor Authentication**: Additional security layer
10. **Rate Limiting**: Prevent API abuse

---

## 📚 Useful Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **SQLAlchemy ORM**: https://docs.sqlalchemy.org/
- **Pydantic Validation**: https://docs.pydantic.dev/
- **PostgreSQL Tutorial**: https://www.postgresql.org/docs/
- **JWT Standard**: https://jwt.io/
- **HTTP Status Codes**: https://httpwg.org/specs/rfc9110.html

---
