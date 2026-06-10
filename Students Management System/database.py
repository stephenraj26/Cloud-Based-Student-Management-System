# database.py
"""
Database Connection Configuration
This file handles all database-related setup and connections.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config

# Get database URL from .env file
# Format: postgresql://username:password@host:port/database_name
# decouple automatically loads from .env file
DATABASE_URL = config(
    'DATABASE_URL',
    default='postgresql://student_admin:admin123@localhost/student_management_db'
)

# Explanation of create_engine:
# - DATABASE_URL: Connection string to your PostgreSQL database
# - echo=False: Set to True for debugging (prints SQL queries)
# - pool_pre_ping=True: Tests connection before using it (prevents stale connections)
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,  # Number of connections to maintain
    max_overflow=20  # Additional connections if needed
)

# SessionLocal is used to create database sessions
# A session is like a "conversation" with the database
# Each request gets its own session
SessionLocal = sessionmaker(
    autocommit=False,  # Don't auto-commit, we control transactions
    autoflush=False,   # Don't auto-flush, we control flushing
    bind=engine
)

# Base class for all database models
# Any model that inherits from this will be a database table
Base = declarative_base()

# Dependency function for FastAPI
# This is called automatically for each request that needs database access
def get_db():
    """
    Database session dependency for FastAPI
    
    Usage in route:
        @app.get("/students")
        def get_students(db: Session = Depends(get_db)):
            return db.query(Student).all()
    
    The 'finally' block ensures the session is closed even if an error occurs
    """
    db = SessionLocal()
    try:
        yield db  # Provide the session to the route
    finally:
        db.close()  # Always close the session when done

# Function to create all tables
def create_tables():
    """
    Creates all database tables defined by models
    Call this once at startup to initialize the database
    """
    Base.metadata.create_all(bind=engine)

# Function to test database connection
def test_database_connection():
    """
    Tests if we can connect to the database
    Useful for debugging connection issues
    """
    try:
        db = SessionLocal()
        result = db.execute("SELECT 1")
        db.close()
        return True, "Database connection successful"
    except Exception as e:
        return False, f"Database connection failed: {str(e)}"
