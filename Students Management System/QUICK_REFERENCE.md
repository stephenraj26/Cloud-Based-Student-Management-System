# 🚀 Quick Reference Guide

Fast lookup for the most common tasks.

---

## ⚡ 30-Second Quick Start

```bash
# 1. Activate virtual environment
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate  # Windows

# 2. Start server
uvicorn main:app --reload

# 3. Open in browser
http://localhost:8000/docs
```

---

## 🔐 Quick Authentication

### 1. Register
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"john","email":"john@test.com","password":"Pass123!","role":"teacher"}'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"john","password":"Pass123!"}'
```

**Copy the `access_token` from response!**

### 3. Use Token in Requests
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/users/me
```

---

## 📚 Common Endpoints

### Students - Create
```bash
POST /students
Authorization: Bearer TOKEN
{
  "roll_number": "2023001",
  "name": "Student Name",
  "email": "student@example.com",
  "department": "CSE",
  "semester": 3
}
```

### Students - Read
```bash
GET /students              # Get all
GET /students/1            # Get by ID
GET /students?department=CSE&semester=3  # Filter
```

### Students - Update
```bash
PATCH /students/1
{
  "semester": 4,
  "gpa": "3.9"
}
```

### Students - Delete
```bash
DELETE /students/1
```

---

## 👥 Roles & Permissions

| Endpoint | Admin | Teacher | Student |
|----------|-------|---------|---------|
| POST /students | ✅ | ✅ | ❌ |
| GET /students | ✅ | ✅ | Self only |
| PATCH /students | ✅ | ✅ | ❌ |
| DELETE /students | ✅ | ❌ | ❌ |
| GET /users | ✅ | ❌ | ❌ |
| DELETE /users | ✅ | ❌ | ❌ |

---

## 🧪 Testing Quick Commands

### Create test data
```bash
# Admin user
curl -X POST http://localhost:8000/auth/register -H "Content-Type: application/json" -d '{"username":"admin1","email":"admin@test.com","password":"Admin123","role":"admin"}'

# Teacher user  
curl -X POST http://localhost:8000/auth/register -H "Content-Type: application/json" -d '{"username":"teacher1","email":"teacher@test.com","password":"Teacher123","role":"teacher"}'

# Student user
curl -X POST http://localhost:8000/auth/register -H "Content-Type: application/json" -d '{"username":"student1","email":"student@test.com","password":"Student123","role":"student"}'
```

### Test each role
```bash
# Login teacher
TOKEN=$(curl -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d '{"username":"teacher1","password":"Teacher123"}' | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

# Use token
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/users/me
```

---

## 🛠️ Common Issues - Quick Fixes

| Issue | Solution |
|-------|----------|
| Port 8000 in use | `uvicorn main:app --port 8001` |
| ModuleNotFoundError | `pip install -r requirements.txt` |
| Database connection error | Check PostgreSQL is running |
| Token invalid | Login again, copy token correctly |
| 403 Forbidden | Check user role (student can't create) |
| 404 Not Found | Resource doesn't exist, try ID=1 |

---

## 📋 Request/Response Templates

### Request Template
```bash
curl -X METHOD http://localhost:8000/ENDPOINT \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{...json data...}'
```

### Response Template
```json
{
  "id": 1,
  "field1": "value1",
  "field2": "value2",
  "created_at": "2025-01-15T10:00:00",
  "is_active": true
}
```

---

## 🔍 HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | GET successful |
| 201 | Created | POST successful |
| 204 | No Content | DELETE successful |
| 400 | Bad Request | Invalid data |
| 401 | Unauthorized | Invalid token |
| 403 | Forbidden | No permission |
| 404 | Not Found | Resource doesn't exist |
| 422 | Validation Error | Missing fields |
| 500 | Server Error | Bug in code |

---

## 🔐 JWT Token Structure

```
Header.Payload.Signature

Payload contains:
{
  "user_id": 1,
  "username": "john",
  "role": "teacher",
  "exp": 1234567890  # Expiration time
}
```

---

## 📊 Database Schema Quick Reference

### User Table
```
id (PK) | username | email | hashed_password | role | is_active | created_at
```

### Student Table  
```
id (PK) | roll_number | name | email | phone | department | semester | gpa | created_by (FK) | created_at
```

---

## 🎯 Common Workflows

### Workflow 1: Create and Manage Students
```bash
1. Register as teacher
2. Login to get token
3. POST /students to create
4. GET /students to list
5. PATCH /students/1 to update
```

### Workflow 2: Admin User Management
```bash
1. Register as admin
2. Login to get token
3. GET /users to list all users
4. PATCH /users/2 to update user
5. DELETE /users/3 to remove user
```

### Workflow 3: Student Views Own Data
```bash
1. Register as student
2. Login to get token
3. GET /students returns only their records
4. Can't create, update, or delete
```

---

## 📝 Useful SQL Queries

```sql
-- List all students
SELECT * FROM students WHERE is_active = true;

-- Students by department
SELECT * FROM students WHERE department = 'Computer Science';

-- Count students per department
SELECT department, COUNT(*) FROM students GROUP BY department;

-- Active users
SELECT * FROM users WHERE is_active = true;

-- Students created by teacher
SELECT * FROM students WHERE created_by = 2;
```

---

## 🔐 Password Requirements

- Minimum 8 characters
- No specific complexity required in this version
- But recommended: Mix of letters, numbers, special chars

**Examples:**
- ✅ `SecurePass123`
- ✅ `MyPassword@456`
- ✅ `Teacher2025!`
- ❌ `short` (too short)
- ❌ `12345678` (weak)

---

## 📱 API Documentation URLs

When server is running:

| URL | Purpose |
|-----|---------|
| http://localhost:8000/ | API root |
| http://localhost:8000/docs | Swagger UI (interactive) |
| http://localhost:8000/redoc | ReDoc (alternative docs) |
| http://localhost:8000/openapi.json | OpenAPI spec |

---

## 🎓 Key Concepts Summary

| Concept | Explanation |
|---------|------------|
| REST | Architecture style using HTTP methods |
| JWT | Token containing user info, expires after time |
| Bcrypt | Password hashing algorithm (one-way) |
| RBAC | Role-Based Access Control (Admin/Teacher/Student) |
| Foreign Key | Links student to user who created them |
| Pagination | Limiting/skipping results (skip=0&limit=10) |
| Bearer Token | Standard way to send JWT in Authorization header |

---

## 🚀 File Checklist

Before running, make sure you have:

- [ ] `main.py` - Main application
- [ ] `database.py` - Database setup
- [ ] `models.py` - Database tables
- [ ] `schemas.py` - Request/response validation
- [ ] `auth.py` - Authentication logic
- [ ] `requirements.txt` - Dependencies
- [ ] `.env` - Environment variables
- [ ] `venv/` - Virtual environment

---

## 🆘 Getting Help

1. **Check logs**: Server output shows errors
2. **Read comments**: Code has detailed explanations
3. **Use /docs**: Built-in API documentation
4. **Test slowly**: Try one endpoint at a time
5. **Verify data**: Check database directly with SQL

```bash
# Connect to database
psql -U student_admin -d student_management_db

# View tables
\dt

# View users
SELECT * FROM users;

# View students
SELECT * FROM students;
```

---

## 📞 Quick Support Commands

```bash
# Check Python version
python --version

# Check PostgreSQL
psql --version

# Check pip packages
pip list

# Restart server
# Press Ctrl+C in terminal, then:
uvicorn main:app --reload

# Activate virtual environment (if needed)
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate      # Windows
```

---

**💡 Tip**: Save this page and refer to it while developing!

---

**Ready to code? Let's go! 🚀**
