# schemas.py
"""
Pydantic Schemas
These define what data we accept as input and what we return as output.
Pydantic automatically validates the data types.

Think of schemas as the "contract" between client and server:
- When someone sends data to our API, we validate it against these schemas
- When we return data, we format it according to these schemas
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from models import UserRole

# ============================================
# USER SCHEMAS
# ============================================

class UserBase(BaseModel):
    """Base user schema with common fields"""
    username: str = Field(..., min_length=3, max_length=50, description="Username for login")
    email: EmailStr = Field(..., description="Valid email address")
    full_name: Optional[str] = Field(None, max_length=100, description="User's full name")
    role: UserRole = Field(default=UserRole.STUDENT, description="User's role in system")


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    
    # Example of what data should look like:
    # {
    #   "username": "john_doe",
    #   "email": "john@example.com",
    #   "full_name": "John Doe",
    #   "role": "teacher",
    #   "password": "securepass123"
    # }


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for returning user data to client"""
    id: int
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True  # Allows converting SQLAlchemy objects to this schema


# ============================================
# AUTHENTICATION SCHEMAS
# ============================================

class LoginRequest(BaseModel):
    """Schema for login request"""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")
    
    # Example:
    # {
    #   "username": "john_doe",
    #   "password": "securepass123"
    # }


class TokenResponse(BaseModel):
    """Schema for login response"""
    access_token: str = Field(..., description="JWT token for API requests")
    token_type: str = Field(default="bearer", description="Type of token")
    user: UserResponse = Field(..., description="Logged in user info")
    
    # Example response:
    # {
    #   "access_token": "eyJhbGciOiJIUzI1NiIs...",
    #   "token_type": "bearer",
    #   "user": {
    #     "id": 1,
    #     "username": "john_doe",
    #     "email": "john@example.com",
    #     "role": "teacher",
    #     ...
    #   }
    # }


class TokenData(BaseModel):
    """Schema for data inside JWT token"""
    user_id: int
    username: str
    role: UserRole


# ============================================
# STUDENT SCHEMAS
# ============================================

class StudentBase(BaseModel):
    """Base student schema with common fields"""
    roll_number: str = Field(..., min_length=1, description="Unique roll number")
    name: str = Field(..., min_length=1, max_length=100, description="Student's full name")
    email: EmailStr = Field(..., description="Student's email")
    phone: Optional[str] = Field(None, max_length=15, description="Contact number")
    department: str = Field(..., description="Department (CSE, ECE, etc.)")
    semester: int = Field(..., ge=1, le=8, description="Semester (1-8)")
    gpa: Optional[str] = Field(None, description="Grade Point Average")


class StudentCreate(StudentBase):
    """Schema for creating a new student"""
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    
    # Example:
    # {
    #   "roll_number": "2023001",
    #   "name": "Arjun Kumar",
    #   "email": "arjun@college.com",
    #   "phone": "9876543210",
    #   "department": "Computer Science",
    #   "semester": 3,
    #   "gpa": "3.8",
    #   "address": "123 Main St",
    #   "city": "Chennai",
    #   "state": "Tamil Nadu",
    #   "pincode": "600001"
    # }


class StudentUpdate(BaseModel):
    """Schema for updating student information"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    semester: Optional[int] = Field(None, ge=1, le=8)
    gpa: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    is_active: Optional[bool] = None


class StudentResponse(StudentBase):
    """Schema for returning student data to client"""
    id: int
    is_active: bool
    enrollment_date: datetime
    created_at: datetime
    updated_at: datetime
    created_by: int  # ID of the user who created this record
    
    class Config:
        from_attributes = True


# ============================================
# LIST RESPONSE SCHEMAS
# ============================================

class StudentListResponse(BaseModel):
    """Schema for returning multiple students"""
    total: int = Field(..., description="Total number of students")
    count: int = Field(..., description="Number returned in this request")
    students: List[StudentResponse] = Field(..., description="List of students")
    
    # Example:
    # {
    #   "total": 150,
    #   "count": 10,
    #   "students": [
    #     {...student1...},
    #     {...student2...},
    #     ...
    #   ]
    # }


class UserListResponse(BaseModel):
    """Schema for returning multiple users"""
    total: int
    count: int
    users: List[UserResponse]


# ============================================
# ERROR RESPONSE SCHEMAS
# ============================================

class ErrorResponse(BaseModel):
    """Schema for error messages"""
    detail: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")
    
    # Example:
    # {
    #   "detail": "Student not found",
    #   "status_code": 404
    # }


# ============================================
# IMPORTANT CONCEPTS
# ============================================

"""
BASEMODEL:
    - All schemas inherit from Pydantic's BaseModel
    - Automatically validates data types
    - Can be converted to/from JSON

FIELD:
    - Used to add validation and documentation
    - Field(...) = required
    - Field(None) or Field(default=...) = optional

EMAILSTR:
    - Special type that validates email format
    - Requires: pip install pydantic[email]

CONFIG:
    - from_attributes = True converts SQLAlchemy objects to Pydantic
    - Example: user_db (database object) → UserResponse (schema)

TYPING:
    - Optional[str] = can be str or None
    - List[StudentResponse] = array of students
"""
