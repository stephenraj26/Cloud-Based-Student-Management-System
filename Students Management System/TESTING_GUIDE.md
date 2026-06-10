# 🧪 Testing & Verification Guide

Complete step-by-step guide to test all features of the Student Data Management System.

---

## ✅ Pre-Testing Checklist

Before you start testing, make sure:

- [ ] Virtual environment is activated
- [ ] PostgreSQL is running
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] FastAPI server is running (`uvicorn main:app --reload`)
- [ ] Terminal showing: "Uvicorn running on http://127.0.0.1:8000"

---

## 🧪 Testing Steps

### Step 1: Health Check
Verify the server is running

```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{"status": "ok", "message": "Server is running"}
```

---

### Step 2: Register Admin User

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin_user",
    "email": "admin@example.com",
    "full_name": "System Administrator",
    "password": "Admin@12345",
    "role": "admin"
  }'
```

**Expected Response (201 Created):**
```json
{
    "id": 1,
    "username": "admin_user",
    "email": "admin@example.com",
    "full_name": "System Administrator",
    "role": "admin",
    "is_active": true,
    "created_at": "2025-01-15T10:30:00",
    "last_login": null
}
```

**✅ Success**: Admin user created!

---

### Step 3: Register Teacher User

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "teacher_user",
    "email": "teacher@example.com",
    "full_name": "Dr. Ramesh Kumar",
    "password": "Teacher@12345",
    "role": "teacher"
  }'
```

**Expected Response (201 Created):**
```json
{
    "id": 2,
    "username": "teacher_user",
    "email": "teacher@example.com",
    "full_name": "Dr. Ramesh Kumar",
    "role": "teacher",
    "is_active": true,
    "created_at": "2025-01-15T10:31:00",
    "last_login": null
}
```

**✅ Success**: Teacher user created!

---

### Step 4: Register Student User

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "student_user",
    "email": "student@example.com",
    "full_name": "Arjun Singh",
    "password": "Student@12345",
    "role": "student"
  }'
```

**Expected Response (201 Created):**
```json
{
    "id": 3,
    "username": "student_user",
    "email": "student@example.com",
    "full_name": "Arjun Singh",
    "role": "student",
    "is_active": true,
    "created_at": "2025-01-15T10:32:00",
    "last_login": null
}
```

**✅ Success**: Student user created!

---

### Step 5: Login as Teacher

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "teacher_user",
    "password": "Teacher@12345"
  }'
```

**Expected Response (200 OK):**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
        "id": 2,
        "username": "teacher_user",
        "email": "teacher@example.com",
        "full_name": "Dr. Ramesh Kumar",
        "role": "teacher",
        "is_active": true,
        "created_at": "2025-01-15T10:31:00",
        "last_login": "2025-01-15T10:35:00"
    }
}
```

**💾 IMPORTANT**: Copy the `access_token` value. You'll need it for the next steps!

Let's call it: `TEACHER_TOKEN`

---

### Step 6: Get Teacher's Profile

```bash
curl -X GET http://localhost:8000/users/me \
  -H "Authorization: Bearer YOUR_TEACHER_TOKEN"
```

Replace `YOUR_TEACHER_TOKEN` with the token from Step 5.

**Expected Response (200 OK):**
```json
{
    "id": 2,
    "username": "teacher_user",
    "email": "teacher@example.com",
    "full_name": "Dr. Ramesh Kumar",
    "role": "teacher",
    "is_active": true,
    "created_at": "2025-01-15T10:31:00",
    "last_login": "2025-01-15T10:35:00"
}
```

**✅ Success**: Authentication working!

---

### Step 7: Create First Student Record

```bash
curl -X POST http://localhost:8000/students \
  -H "Authorization: Bearer YOUR_TEACHER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "roll_number": "2023001",
    "name": "Rahul Sharma",
    "email": "rahul.sharma@college.com",
    "phone": "9876543210",
    "department": "Computer Science",
    "semester": 3,
    "gpa": "3.8",
    "address": "123 Main Street",
    "city": "Chennai",
    "state": "Tamil Nadu",
    "pincode": "600001"
  }'
```

**Expected Response (201 Created):**
```json
{
    "id": 1,
    "roll_number": "2023001",
    "name": "Rahul Sharma",
    "email": "rahul.sharma@college.com",
    "phone": "9876543210",
    "department": "Computer Science",
    "semester": 3,
    "gpa": "3.8",
    "address": "123 Main Street",
    "city": "Chennai",
    "state": "Tamil Nadu",
    "pincode": "600001",
    "is_active": true,
    "enrollment_date": "2025-01-15T10:36:00",
    "created_at": "2025-01-15T10:36:00",
    "updated_at": "2025-01-15T10:36:00",
    "created_by": 2
}
```

**✅ Success**: Student record created!

---

### Step 8: Create More Student Records

Create 2-3 more students with different departments:

```bash
# Student 2 - Electronics Department
curl -X POST http://localhost:8000/students \
  -H "Authorization: Bearer YOUR_TEACHER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "roll_number": "2023002",
    "name": "Priya Patel",
    "email": "priya.patel@college.com",
    "phone": "9876543211",
    "department": "Electronics Engineering",
    "semester": 2,
    "gpa": "3.9",
    "city": "Mumbai"
  }'

# Student 3 - Mechanical Department
curl -X POST http://localhost:8000/students \
  -H "Authorization: Bearer YOUR_TEACHER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "roll_number": "2023003",
    "name": "Arun Kumar",
    "email": "arun.kumar@college.com",
    "phone": "9876543212",
    "department": "Mechanical Engineering",
    "semester": 4,
    "gpa": "3.6",
    "city": "Bangalore"
  }'
```

---

### Step 9: Get All Students

```bash
curl -X GET http://localhost:8000/students \
  -H "Authorization: Bearer YOUR_TEACHER_TOKEN"
```

**Expected Response (200 OK):**
```json
{
    "total": 3,
    "count": 3,
    "students": [
        {
            "id": 1,
            "roll_number": "2023001",
            "name": "Rahul Sharma",
            ...
        },
        {
            "id": 2,
            "roll_number": "2023002",
            "name": "Priya Patel",
            ...
        },
        {
            "id": 3,
            "roll_number": "2023003",
            "name": "Arun Kumar",
            ...
        }
    ]
}
```

**✅ Success**: Retrieved all students!

---

### Step 10: Get Students with Pagination

```bash
curl -X GET "http://localhost:8000/students?skip=0&limit=2" \
  -H "Authorization: Bearer YOUR_TEACHER_TOKEN"
```

**Expected Response**: Only 2 students returned

**✅ Success**: Pagination working!

---

### Step 11: Filter Students by Department

```bash
curl -X GET "http://localhost:8000/students?department=Computer" \
  -H "Authorization: Bearer YOUR_TEACHER_TOKEN"
```

**Expected Response**: Only Computer Science students

**✅ Success**: Filtering working!

---

### Step 12: Get Specific Student

```bash
curl -X GET http://localhost:8000/students/1 \
  -H "Authorization: Bearer YOUR_TEACHER_TOKEN"
```

**Expected Response (200 OK):**
```json
{
    "id": 1,
    "roll_number": "2023001",
    "name": "Rahul Sharma",
    ...
}
```

**✅ Success**: Retrieved specific student!

---

### Step 13: Update Student Record

```bash
curl -X PATCH http://localhost:8000/students/1 \
  -H "Authorization: Bearer YOUR_TEACHER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "semester": 4,
    "gpa": "3.9",
    "phone": "9999999999"
  }'
```

**Expected Response (200 OK):**
- `semester` changed to 4
- `gpa` changed to 3.9
- `phone` changed to 9999999999
- `updated_at` shows current time

**✅ Success**: Student updated!

---

### Step 14: Get Students by Department Endpoint

```bash
curl -X GET "http://localhost:8000/students/department/Computer%20Science" \
  -H "Authorization: Bearer YOUR_TEACHER_TOKEN"
```

**Expected Response (200 OK):**
```json
{
    "department": "Computer Science",
    "count": 1,
    "students": [
        {
            "id": 1,
            "roll_number": "2023001",
            ...
        }
    ]
}
```

**✅ Success**: Department filter endpoint working!

---

### Step 15: Login as Admin

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin_user",
    "password": "Admin@12345"
  }'
```

**Copy the `access_token` and call it: `ADMIN_TOKEN`**

---

### Step 16: Admin - Get All Users

```bash
curl -X GET http://localhost:8000/users \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**Expected Response**: List of all 3 users (admin, teacher, student)

**✅ Success**: Admin can view all users!

---

### Step 17: Admin - Delete a Student

```bash
curl -X DELETE http://localhost:8000/students/3 \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**Expected Response (204 No Content)**

Verify deletion:
```bash
curl -X GET http://localhost:8000/students/3 \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Should get: `404 Not Found`

**✅ Success**: Student deleted!

---

## 🚫 Testing Error Cases

### Test 1: Invalid Credentials

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "teacher_user",
    "password": "WrongPassword"
  }'
```

**Expected Error (401 Unauthorized):**
```json
{"detail": "Invalid username or password"}
```

---

### Test 2: Duplicate Roll Number

```bash
curl -X POST http://localhost:8000/students \
  -H "Authorization: Bearer YOUR_TEACHER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "roll_number": "2023001",
    "name": "Duplicate Name",
    "email": "duplicate@college.com",
    "department": "CSE",
    "semester": 1
  }'
```

**Expected Error (400 Bad Request):**
```json
{"detail": "Roll number '2023001' already exists"}
```

---

### Test 3: Missing Required Fields

```bash
curl -X POST http://localhost:8000/students \
  -H "Authorization: Bearer YOUR_TEACHER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "roll_number": "2023099",
    "name": "Missing Fields"
  }'
```

**Expected Error (422 Unprocessable Entity):**
```json
{
    "detail": [
        {
            "loc": ["body", "email"],
            "msg": "field required",
            "type": "value_error.missing"
        }
    ]
}
```

---

### Test 4: Unauthorized Access (Student trying to manage students)

Login as student and try to create a student:

```bash
# 1. Login as student
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "student_user",
    "password": "Student@12345"
  }'

# 2. Try to create student (copy STUDENT_TOKEN from response)
curl -X POST http://localhost:8000/students \
  -H "Authorization: Bearer YOUR_STUDENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "roll_number": "2023099",
    "name": "Test",
    "email": "test@college.com",
    "department": "CSE",
    "semester": 1
  }'
```

**Expected Error (403 Forbidden):**
```json
{"detail": "Access denied. Required role: admin, teacher"}
```

---

### Test 5: Invalid Token

```bash
curl -X GET http://localhost:8000/users/me \
  -H "Authorization: Bearer InvalidToken123"
```

**Expected Error (401 Unauthorized):**
```json
{"detail": "Could not validate credentials"}
```

---

## 📊 Summary Table

| Test | Command | Expected Result | Status |
|------|---------|-----------------|--------|
| Health Check | GET /health | 200 OK | ✅ |
| Register Admin | POST /auth/register | 201 Created | ✅ |
| Register Teacher | POST /auth/register | 201 Created | ✅ |
| Register Student | POST /auth/register | 201 Created | ✅ |
| Login | POST /auth/login | 200 OK + token | ✅ |
| Get Profile | GET /users/me | 200 OK | ✅ |
| Create Student | POST /students | 201 Created | ✅ |
| Get All Students | GET /students | 200 OK | ✅ |
| Pagination | GET /students?limit=2 | 200 OK | ✅ |
| Filter by Dept | GET /students?department=CSE | 200 OK | ✅ |
| Get Student by ID | GET /students/1 | 200 OK | ✅ |
| Update Student | PATCH /students/1 | 200 OK | ✅ |
| Get by Department | GET /students/department/CSE | 200 OK | ✅ |
| Delete Student | DELETE /students/3 | 204 No Content | ✅ |
| Invalid Credentials | Login with wrong password | 401 Unauthorized | ✅ |
| Duplicate Roll | Create with same roll | 400 Bad Request | ✅ |
| Unauthorized Access | Student creates student | 403 Forbidden | ✅ |

---

## 🎯 Testing Conclusion

If all tests pass, you have a **fully functional, secure student management system**!

### What You've Verified:
✅ User registration and authentication  
✅ JWT token generation and verification  
✅ Password hashing and security  
✅ Role-based access control  
✅ CRUD operations for students  
✅ Pagination and filtering  
✅ Input validation  
✅ Error handling  
✅ Database operations  

---

## 📝 Next: Deploy & Share

Once testing is complete:

1. **Push to GitHub**: Create a repository and push your code
2. **Document Everything**: Add this guide to your GitHub README
3. **Deploy**: Deploy to Heroku/AWS/DigitalOcean
4. **Create Portfolio**: Add project link to your portfolio
5. **Interview Ready**: Discuss this project in interviews!

---

**Congratulations on completing the testing! 🎉**
