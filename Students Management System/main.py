# main.py
"""
Cloud-Based Student Data Management System
Main FastAPI Application File

This file contains:
- Application initialization
- All API endpoints (routes)
- User management (register, login)
- Student management (CRUD operations)
- Role-based access control
"""

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

# Import our custom modules
from database import engine, get_db, create_tables
from models import Base, User, Student, UserRole
from schemas import (
    UserCreate, UserResponse, UserUpdate, LoginRequest, TokenResponse,
    StudentCreate, StudentResponse, StudentUpdate, StudentListResponse,
    ErrorResponse
)
from auth import (
    hash_password, verify_password, create_access_token,
    get_current_user, require_role, check_student_access
)

# ============================================
# APPLICATION SETUP
# ============================================

# Create FastAPI app instance
app = FastAPI(
    title="Student Data Management System",
    description="Secure, role-based student management API",
    version="1.0.0",
    docs_url="/docs",  # Interactive API documentation (Swagger)
    redoc_url="/redoc"  # Alternative documentation
)

# Allow requests from different domains (CORS)
# CORS = Cross-Origin Resource Sharing
# This lets frontend apps from different domains use our API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create all database tables on startup
create_tables()


# ============================================
# HEALTH CHECK ENDPOINT
# ============================================

@app.get("/health")
def health_check():
    """
    Simple endpoint to check if server is running
    
    Usage: curl http://localhost:8000/health
    
    Returns: {"status": "ok"}
    """
    return {"status": "ok", "message": "Server is running"}


# ============================================
# AUTHENTICATION ENDPOINTS
# ============================================

@app.post("/auth/register", response_model=UserResponse, status_code=201)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user (create account)
    
    This endpoint is public - anyone can register
    
    Request body:
    {
        "username": "john_doe",
        "email": "john@example.com",
        "full_name": "John Doe",
        "password": "securepass123",
        "role": "student"  // or "teacher"
    }
    
    Returns: Newly created user information (without password)
    
    Errors:
    - 400: Username or email already exists
    """
    
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{user_data.username}' already registered"
        )
    
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{user_data.email}' already registered"
        )
    
    # Create new user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hash_password(user_data.password),  # Hash the password!
        role=user_data.role,
        is_active=True
    )
    
    # Save to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Reload to get the ID
    
    return new_user


@app.post("/auth/login", response_model=TokenResponse)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login with username and password
    Returns JWT token for subsequent requests
    
    Request body:
    {
        "username": "john_doe",
        "password": "securepass123"
    }
    
    Returns:
    {
        "access_token": "eyJhbGc...",
        "token_type": "bearer",
        "user": {...}
    }
    
    Errors:
    - 401: Invalid username or password
    """
    
    # Find user by username
    user = db.query(User).filter(User.username == credentials.username).first()
    
    # Check if user exists and password is correct
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Create JWT token
    access_token = create_access_token(
        user_id=user.id,
        username=user.username,
        role=user.role
    )
    
    # Update last login time
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.commit()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


# ============================================
# USER MANAGEMENT ENDPOINTS
# ============================================

@app.get("/users/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current logged-in user's profile
    
    Requires: Bearer token in Authorization header
    
    Usage:
    curl -H "Authorization: Bearer <token>" http://localhost:8000/users/me
    
    Returns: Current user's information
    """
    return current_user


@app.get("/users", response_model=List[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Get list of all users (Admin only)
    
    Requires: ADMIN role
    
    Returns: List of all users in system
    """
    users = db.query(User).all()
    return users


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Get specific user by ID (Admin only)
    
    Requires: ADMIN role
    
    Args:
        user_id: ID of user to retrieve
        
    Returns: User information
    
    Errors:
    - 404: User not found
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return user


@app.patch("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Update user information (Admin only)
    
    Requires: ADMIN role
    
    Args:
        user_id: ID of user to update
        user_update: Fields to update
        
    Returns: Updated user information
    
    Errors:
    - 404: User not found
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Update only provided fields
    if user_update.full_name is not None:
        user.full_name = user_update.full_name
    if user_update.email is not None:
        user.email = user_update.email
    if user_update.password is not None:
        user.hashed_password = hash_password(user_update.password)
    if user_update.is_active is not None:
        user.is_active = user_update.is_active
    
    db.commit()
    db.refresh(user)
    
    return user


@app.delete("/users/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Delete a user (Admin only)
    
    Requires: ADMIN role
    
    Args:
        user_id: ID of user to delete
        
    Returns: No content (204)
    
    Errors:
    - 404: User not found
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    db.delete(user)
    db.commit()
    
    return None


# ============================================
# STUDENT MANAGEMENT ENDPOINTS
# ============================================

@app.post("/students", response_model=StudentResponse, status_code=201)
def create_student(
    student_data: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_role(UserRole.ADMIN, UserRole.TEACHER))
):
    """
    Create a new student record
    
    Requires: ADMIN or TEACHER role
    
    Request body:
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
    
    Returns: Created student information
    
    Errors:
    - 400: Roll number or email already exists
    """
    
    # Check if roll number already exists
    existing_roll = db.query(Student).filter(Student.roll_number == student_data.roll_number).first()
    if existing_roll:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Roll number '{student_data.roll_number}' already exists"
        )
    
    # Check if email already exists
    existing_email = db.query(Student).filter(Student.email == student_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{student_data.email}' already registered"
        )
    
    # Create new student
    new_student = Student(
        roll_number=student_data.roll_number,
        name=student_data.name,
        email=student_data.email,
        phone=student_data.phone,
        department=student_data.department,
        semester=student_data.semester,
        gpa=student_data.gpa,
        address=student_data.address,
        city=student_data.city,
        state=student_data.state,
        pincode=student_data.pincode,
        created_by=current_user.id  # Track who created this record
    )
    
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    
    return new_student


@app.get("/students", response_model=StudentListResponse)
def get_all_students(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    department: str = Query(None, description="Filter by department"),
    semester: int = Query(None, ge=1, le=8, description="Filter by semester")
):
    """
    Get list of students (with pagination and filtering)
    
    Requires: Authenticated user
    
    Rules:
    - ADMIN/TEACHER: Can view all students
    - STUDENT: Can only view their own record
    
    Query parameters:
    - skip: Number of records to skip (for pagination)
    - limit: Number of records to return (max 100)
    - department: Filter by department (optional)
    - semester: Filter by semester (optional)
    
    Example:
    GET /students?skip=0&limit=10&department=CSE
    
    Returns: Paginated list of students
    """
    
    # Build query
    query = db.query(Student)
    
    # Apply filters based on role
    if current_user.role == UserRole.STUDENT:
        # Students can only see their own data
        # Assuming student's email matches user's email
        query = query.filter(Student.email == current_user.email)
    
    # Apply department filter
    if department:
        query = query.filter(Student.department.ilike(f"%{department}%"))
    
    # Apply semester filter
    if semester:
        query = query.filter(Student.semester == semester)
    
    # Get total count before pagination
    total = query.count()
    
    # Apply pagination
    students = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "count": len(students),
        "students": students
    }


@app.get("/students/{student_id}", response_model=StudentResponse)
def get_student_by_id(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get specific student by ID
    
    Requires: Authenticated user
    
    Rules:
    - ADMIN/TEACHER: Can access any student
    - STUDENT: Can only access their own data
    
    Args:
        student_id: ID of student to retrieve
        
    Returns: Student information
    
    Errors:
    - 404: Student not found
    - 403: Access denied (student can't access others' data)
    """
    
    # Get student from database
    student = db.query(Student).filter(Student.id == student_id).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found"
        )
    
    # Check access permissions
    can_access, message = check_student_access(student_id, current_user, db)
    if not can_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message
        )
    
    return student


@app.patch("/students/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    student_update: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_role(UserRole.ADMIN, UserRole.TEACHER))
):
    """
    Update student information
    
    Requires: ADMIN or TEACHER role
    
    Args:
        student_id: ID of student to update
        student_update: Fields to update
        
    Returns: Updated student information
    
    Errors:
    - 404: Student not found
    """
    
    student = db.query(Student).filter(Student.id == student_id).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found"
        )
    
    # Update only provided fields
    update_data = student_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(student, field, value)
    
    db.commit()
    db.refresh(student)
    
    return student


@app.delete("/students/{student_id}", status_code=204)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Delete a student record (Admin only)
    
    Requires: ADMIN role
    
    Args:
        student_id: ID of student to delete
        
    Returns: No content (204)
    
    Errors:
    - 404: Student not found
    """
    
    student = db.query(Student).filter(Student.id == student_id).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found"
        )
    
    db.delete(student)
    db.commit()
    
    return None


@app.get("/students/department/{department}")
def get_students_by_department(
    department: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_role(UserRole.ADMIN, UserRole.TEACHER))
):
    """
    Get all students in a specific department
    
    Requires: ADMIN or TEACHER role
    
    Args:
        department: Department name
        
    Returns: List of students in that department
    """
    
    students = db.query(Student).filter(
        Student.department.ilike(f"%{department}%"),
        Student.is_active == True
    ).all()
    
    return {
        "department": department,
        "count": len(students),
        "students": students
    }


# ============================================
# ERROR HANDLING
# ============================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom error response format"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )


# ============================================
# ROOT ENDPOINT
# ============================================

@app.get("/")
def root():
    """Root endpoint - welcome message"""
    return {
        "message": "Welcome to Student Data Management System",
        "docs": "Visit http://localhost:8000/docs for API documentation",
        "version": "1.0.0"
    }


# ============================================
# RUN THE SERVER
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
