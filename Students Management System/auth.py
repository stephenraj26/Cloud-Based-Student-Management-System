# auth.py
"""
Authentication Module
Handles:
- Password hashing (securing passwords)
- JWT token creation (for login sessions)
- JWT token verification (for API requests)
- Permission checking (role-based access)
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from decouple import config

from models import User, UserRole
from schemas import TokenData
from database import get_db

# ============================================
# CONFIGURATION
# ============================================

# Load environment variables from .env file
# decouple automatically reads .env file
SECRET_KEY = config('SECRET_KEY', default='your-super-secret-key-change-this-in-production')
ALGORITHM = config('ALGORITHM', default='HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(config('ACCESS_TOKEN_EXPIRE_MINUTES', default='30'))

# ============================================
# PASSWORD HASHING
# ============================================

# CryptContext is used for hashing passwords
# "bcrypt" is a secure algorithm for password hashing
pwd_context = CryptContext(
    schemes=["bcrypt"],  # Algorithm to use for hashing
    deprecated="auto"    # Automatically handle deprecated algorithms
)


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt
    
    Why hash? Never store plain passwords!
    - Even if database is compromised, passwords are unreadable
    - Hashing is one-way (can't reverse it)
    
    Args:
        password: Plain text password
        
    Returns:
        hashed_password: Encrypted password
        
    Example:
        hashed = hash_password("mypassword123")
        # Returns: $2b$12$KIXxz8h1rq8BQvg7...
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify if a plain password matches the hashed password
    
    Args:
        plain_password: Password entered by user
        hashed_password: Password stored in database
        
    Returns:
        True if passwords match, False otherwise
        
    Example:
        is_valid = verify_password("mypassword123", "$2b$12$KIXxz8h1rq8BQvg7...")
        # Returns: True
    """
    return pwd_context.verify(plain_password, hashed_password)


# ============================================
# JWT TOKEN HANDLING
# ============================================

def create_access_token(
    user_id: int,
    username: str,
    role: UserRole,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT (JSON Web Token) for user authentication
    
    JWT is like a digital ID card:
    - User logs in → gets a token
    - User includes token in every API request
    - Server verifies token without querying database
    
    Args:
        user_id: User's database ID
        username: User's username
        role: User's role (admin, teacher, student)
        expires_delta: How long token is valid (optional)
        
    Returns:
        JWT token string
        
    Example:
        token = create_access_token(
            user_id=1,
            username="john_doe",
            role=UserRole.TEACHER
        )
        # Returns: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    
    # Determine expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Default: expires in 30 minutes
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Data to encode in the token
    to_encode = {
        "user_id": user_id,
        "username": username,
        "role": role.value,  # Convert enum to string
        "exp": expire  # Expiration time
    }
    
    # Create JWT token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def verify_access_token(token: str) -> TokenData:
    """
    Verify JWT token and extract user information
    
    Args:
        token: JWT token string
        
    Returns:
        TokenData with user_id, username, role
        
    Raises:
        HTTPException if token is invalid or expired
        
    Example:
        token_data = verify_access_token("eyJhbGc...")
        # Returns: TokenData(user_id=1, username="john_doe", role=<UserRole.TEACHER>)
    """
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode and verify the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract data from token
        user_id: int = payload.get("user_id")
        username: str = payload.get("username")
        role: str = payload.get("role")
        
        if user_id is None or username is None:
            raise credentials_exception
            
        token_data = TokenData(
            user_id=user_id,
            username=username,
            role=UserRole(role)
        )
        
    except JWTError:
        raise credentials_exception
    
    return token_data


# ============================================
# FASTAPI SECURITY
# ============================================

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency function to get current logged-in user
    
    This runs automatically before any endpoint that needs authentication
    
    Usage in route:
        @app.get("/me")
        def get_profile(current_user: User = Depends(get_current_user)):
            return current_user
    
    Args:
        credentials: HTTP Bearer token from request header
        db: Database session
        
    Returns:
        User object if token is valid
        
    Raises:
        HTTPException if token is invalid or user not found
    """
    
    token = credentials.credentials
    
    # Verify token and get user data
    token_data = verify_access_token(token)
    
    # Get user from database
    user = db.query(User).filter(User.id == token_data.user_id).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


# ============================================
# ROLE-BASED ACCESS CONTROL (RBAC)
# ============================================

def require_role(*allowed_roles: UserRole):
    """
    Creates a dependency that checks if user has required role
    
    Usage in route:
        @app.delete("/users/{user_id}")
        def delete_user(
            user_id: int,
            current_user: User = Depends(get_current_user),
            _ = Depends(require_role(UserRole.ADMIN))
        ):
            # Only admins can reach this code
            ...
    
    Args:
        *allowed_roles: One or more roles that are allowed
        
    Returns:
        Dependency function
    """
    
    async def check_role(current_user: User = Depends(get_current_user)):
        """Inner function that performs the check"""
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {', '.join([r.value for r in allowed_roles])}"
            )
        return current_user
    
    return check_role


def check_student_access(student_id: int, current_user: User, db: Session) -> Tuple[bool, str]:
    """
    Check if user can access a specific student's data
    
    Rules:
    - ADMIN: Can access any student
    - TEACHER: Can access any student
    - STUDENT: Can only access their own data
    
    Args:
        student_id: ID of student to access
        current_user: Current logged-in user
        db: Database session
        
    Returns:
        Tuple of (is_allowed, reason)
        
    Example:
        can_access, reason = check_student_access(123, current_user, db)
        if not can_access:
            raise HTTPException(status_code=403, detail=reason)
    """
    
    # Admins and teachers can access anyone
    if current_user.role in [UserRole.ADMIN, UserRole.TEACHER]:
        return True, "Access granted"
    
    # Students can only access their own data
    if current_user.role == UserRole.STUDENT:
        # Check if the student's user ID matches
        student = db.query(User).filter(
            User.id == student_id,
            User.username == current_user.username
        ).first()
        
        if student:
            return True, "Access granted"
        else:
            return False, "Students can only access their own data"
    
    return False, "Access denied"


# ============================================
# IMPORTANT CONCEPTS
# ============================================

"""
PASSWORD HASHING:
    - Never store plain passwords!
    - Bcrypt = one-way encryption
    - Same password → same hash (deterministic)
    - Even if DB is stolen, passwords are safe

JWT TOKEN:
    - Token contains: user_id, username, role, expiration
    - Signed with SECRET_KEY (only server knows it)
    - Client sends token in Authorization header
    - Server verifies signature without database lookup

BEARER AUTHENTICATION:
    - Standard way to send tokens in HTTP
    - Header format: Authorization: Bearer <token>
    - Example: Authorization: Bearer eyJhbGc...

ROLE-BASED ACCESS CONTROL (RBAC):
    - Different users have different permissions
    - Admin: Full access
    - Teacher: Can view/manage students
    - Student: Can only view own data
"""
