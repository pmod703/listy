#!/usr/bin/env python3
"""
Authentication Models and Utilities
Enhanced user authentication for Real Estate Open Home Optimizer
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from database_models import Base
import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import re

class User(Base):
    """Enhanced User model with authentication features"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    agency_name = Column(String(255))
    license_number = Column(String(100))
    
    # Authentication fields
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    failed_login_attempts = Column(Integer, default=0)
    last_failed_login = Column(DateTime)
    account_locked_until = Column(DateTime)
    
    # Profile fields
    profile_image_url = Column(String(500))
    bio = Column(Text)
    website = Column(String(255))
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime)
    
    # Verification tokens
    email_verification_token = Column(String(255))
    password_reset_token = Column(String(255))
    password_reset_expires = Column(DateTime)
    
    def __init__(self, **kwargs):
        # Hash password if provided
        if 'password' in kwargs:
            self.set_password(kwargs.pop('password'))
        super().__init__(**kwargs)
    
    def set_password(self, password: str) -> None:
        """Hash and set password"""
        if not password:
            raise ValueError("Password cannot be empty")
        
        # Validate password strength
        if not self.validate_password_strength(password):
            raise ValueError("Password does not meet security requirements")
        
        # Hash password with bcrypt
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """Verify password against hash"""
        if not password or not self.password_hash:
            return False
        
        try:
            return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
        except Exception:
            return False
    
    @staticmethod
    def validate_password_strength(password: str) -> bool:
        """Validate password meets security requirements"""
        if len(password) < 8:
            return False
        
        # Check for at least one uppercase, lowercase, digit, and special character
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'\d', password):
            return False
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False
        
        return True
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def generate_jwt_token(self, expires_delta: Optional[timedelta] = None) -> str:
        """Generate JWT token for user"""
        if expires_delta is None:
            expires_delta = timedelta(hours=24)  # Default 24 hours
        
        expire = datetime.utcnow() + expires_delta
        
        payload = {
            'user_id': self.id,
            'email': self.email,
            'exp': expire,
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        
        secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
        return jwt.encode(payload, secret_key, algorithm='HS256')
    
    def generate_refresh_token(self) -> str:
        """Generate refresh token for user"""
        expire = datetime.utcnow() + timedelta(days=30)  # 30 days
        
        payload = {
            'user_id': self.id,
            'exp': expire,
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }
        
        secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
        return jwt.encode(payload, secret_key, algorithm='HS256')
    
    @staticmethod
    def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def is_account_locked(self) -> bool:
        """Check if account is locked due to failed login attempts"""
        if self.account_locked_until:
            return datetime.utcnow() < self.account_locked_until
        return False
    
    def lock_account(self, duration_minutes: int = 30) -> None:
        """Lock account for specified duration"""
        self.account_locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
        self.failed_login_attempts = 0  # Reset counter
    
    def unlock_account(self) -> None:
        """Unlock account and reset failed attempts"""
        self.account_locked_until = None
        self.failed_login_attempts = 0
    
    def record_failed_login(self) -> None:
        """Record failed login attempt"""
        self.failed_login_attempts += 1
        self.last_failed_login = datetime.utcnow()
        
        # Lock account after 5 failed attempts
        if self.failed_login_attempts >= 5:
            self.lock_account()
    
    def record_successful_login(self) -> None:
        """Record successful login"""
        self.last_login = datetime.utcnow()
        self.failed_login_attempts = 0
        self.account_locked_until = None
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name or ''} {self.last_name or ''}".strip()
    
    @property
    def is_email_verified(self) -> bool:
        """Check if email is verified"""
        return self.email_verified
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'phone': self.phone,
            'agency_name': self.agency_name,
            'license_number': self.license_number,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'email_verified': self.email_verified,
            'profile_image_url': self.profile_image_url,
            'bio': self.bio,
            'website': self.website,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        
        if include_sensitive:
            data.update({
                'failed_login_attempts': self.failed_login_attempts,
                'account_locked_until': self.account_locked_until.isoformat() if self.account_locked_until else None,
                'last_failed_login': self.last_failed_login.isoformat() if self.last_failed_login else None
            })
        
        return data
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.full_name}')>"

class UserSession(Base):
    """User session tracking"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    session_token = Column(String(255), unique=True, nullable=False)
    refresh_token = Column(String(255), unique=True)
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(Text)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())
    last_activity = Column(DateTime, default=func.now())
    
    def is_expired(self) -> bool:
        """Check if session is expired"""
        return datetime.utcnow() > self.expires_at
    
    def extend_session(self, hours: int = 24) -> None:
        """Extend session expiration"""
        self.expires_at = datetime.utcnow() + timedelta(hours=hours)
        self.last_activity = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'is_active': self.is_active,
            'expires_at': self.expires_at.isoformat(),
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat()
        }

# Password validation rules
PASSWORD_RULES = {
    'min_length': 8,
    'require_uppercase': True,
    'require_lowercase': True,
    'require_digit': True,
    'require_special': True,
    'forbidden_patterns': [
        'password', '123456', 'qwerty', 'admin', 'user'
    ]
}

# Account lockout settings
LOCKOUT_SETTINGS = {
    'max_attempts': 5,
    'lockout_duration_minutes': 30,
    'reset_attempts_after_hours': 24
}