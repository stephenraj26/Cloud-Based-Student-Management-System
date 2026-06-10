# models.py
"""
Database Models
These define the structure of tables in our PostgreSQL database.
Each class represents a table, each attribute represents a column.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum

# ============================================
# ENUMS (Fixed list of values)
# ============================================

class UserRole(str, enum.Enum):
    """
    Defines the roles users can have in the system
    
    - ADMIN: Full access to all features
    - TEACHER: Can view and manage student data
    - STUDENT: Can only view their own data
    """
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"


# ============================================
# USER MODEL
# ============================================

class User(Base):
    """
    Represents a user in the system (Admin, Teacher, or Student)
    
    Example:
        User(
            username="john_doe",
            email="john@example.com",
            hashed_password="hashed_value",
            role=UserRole.TEACHER,
            is_active=True
        )
    """
    
    __tablename__ = "users"  # Table name in database
    
    # Columns
    id = Column(Integer, primary_key=True, index=True)  # Unique identifier
    username = Column(String(50), unique=True, index=True, nullable=False)  # Login username
    email = Column(String(100), unique=True, index=True, nullable=False)  # Email address
    hashed_password = Column(String(255), nullable=False)  # Encrypted password (never store plain text!)
    full_name = Column(String(100), nullable=True)  # Full name of user
    role = Column(Enum(UserRole), default=UserRole.STUDENT, nullable=False)  # User's role
    is_active = Column(Boolean, default=True)  # Can this user login?
    created_at = Column(DateTime, default=datetime.utcnow)  # When account was created
    last_login = Column(DateTime, nullable=True)  # Last successful login
    
    # Relationships (these don't create columns, just connect tables)
    students = relationship("Student", back_populates="created_by_user")  # Users can create many students
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"


# ============================================
# STUDENT MODEL
# ============================================

class Student(Base):
    """
    Represents a student in the system
    
    Example:
        Student(
            roll_number="2023001",
            name="Arjun Kumar",
            email="arjun@college.com",
            phone="9876543210",
            department="Computer Science",
            semester=3,
            gpa=3.8,
            created_by=1  # Created by user with id=1
        )
    """
    
    __tablename__ = "students"  # Table name in database
    
    # Basic Information
    id = Column(Integer, primary_key=True, index=True)  # Unique student ID
    roll_number = Column(String(20), unique=True, index=True, nullable=False)  # Unique roll number
    name = Column(String(100), nullable=False)  # Student's full name
    email = Column(String(100), unique=True, index=True, nullable=False)  # Student's email
    phone = Column(String(15), nullable=True)  # Contact number
    
    # Academic Information
    department = Column(String(50), nullable=False)  # Department (CSE, ECE, etc.)
    semester = Column(Integer, nullable=False)  # Current semester (1-8)
    gpa = Column(String(10), nullable=True)  # Grade Point Average
    
    # Address Information
    address = Column(Text, nullable=True)  # Full address
    city = Column(String(50), nullable=True)  # City name
    state = Column(String(50), nullable=True)  # State name
    pincode = Column(String(10), nullable=True)  # Postal code
    
    # Status
    is_active = Column(Boolean, default=True)  # Is student currently enrolled?
    enrollment_date = Column(DateTime, default=datetime.utcnow)  # When joined
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # Which user created this record
    created_at = Column(DateTime, default=datetime.utcnow)  # When record was created
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Last update time
    
    # Relationships
    created_by_user = relationship("User", back_populates="students")  # Link to the User who created this
    
    def __repr__(self):
        return f"<Student(id={self.id}, roll={self.roll_number}, name={self.name})>"


# ============================================
# IMPORTANT CONCEPTS EXPLAINED
# ============================================

"""
PRIMARY KEY:
    - Uniquely identifies each row
    - Can't be NULL or duplicate
    - Usually an integer ID

FOREIGN KEY:
    - Links to a column in another table
    - Maintains data integrity
    - created_by in Student links to id in User

UNIQUE:
    - No two rows can have the same value
    - Example: email can't be repeated

INDEX:
    - Makes queries faster
    - Like an index in a book

DEFAULT:
    - Automatically set if not provided
    - Example: created_at = datetime.utcnow

NULLABLE:
    - Can the column be empty (NULL)?
    - False = must always have a value
    - True = can be empty
"""
