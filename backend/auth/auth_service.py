#!/usr/bin/env python3
"""
Authentication Service
Business logic for user authentication and authorization
"""

from sqlalchemy.orm import Session
from auth_models import User, UserSession
from database_config import get_db_session
from datetime import datetime, timedelta
import secrets
import uuid
from typing import Optional, Dict, Any, Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthenticationError(Exception):
    """Custom authentication exception"""
    pass

class AuthService:
    """Authentication service class"""
    
    @staticmethod
    def register_user(
        email: str,
        password: str,
        first_name: str = None,
        last_name: str = None,
        agency_name: str = None,
        license_number: str = None,
        phone: str = None
    ) -> Tuple[User, str]:
        """
        Register a new user
        Returns: (User object, JWT token)
        """
        with next(get_db_session()) as db:
            # Validate email format
            if not User.validate_email(email):
                raise AuthenticationError("Invalid email format")
            
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == email.lower()).first()
            if existing_user:
                raise AuthenticationError("User with this email already exists")
            
            # Validate password strength
            if not User.validate_password_strength(password):
                raise AuthenticationError(
                    "Password must be at least 8 characters long and contain "
                    "uppercase, lowercase, digit, and special character"
                )
            
            # Create new user
            user = User(
                email=email.lower().strip(),
                password=password,
                first_name=first_name,
                last_name=last_name,
                agency_name=agency_name,
                license_number=license_number,
                phone=phone,
                email_verification_token=secrets.token_urlsafe(32)
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Generate JWT token
            token = user.generate_jwt_token()
            
            logger.info(f"New user registered: {email}")
            return user, token
    
    @staticmethod
    def authenticate_user(email: str, password: str, ip_address: str = None, user_agent: str = None) -> Tuple[User, str, str]:
        """
        Authenticate user with email and password
        Returns: (User object, access_token, refresh_token)
        """
        with next(get_db_session()) as db:
            # Find user by email
            user = db.query(User).filter(User.email == email.lower()).first()
            
            if not user:
                logger.warning(f"Login attempt with non-existent email: {email}")
                raise AuthenticationError("Invalid email or password")
            
            # Check if account is locked
            if user.is_account_locked():
                logger.warning(f"Login attempt on locked account: {email}")
                raise AuthenticationError("Account is temporarily locked due to multiple failed login attempts")
            
            # Check if account is active
            if not user.is_active:
                logger.warning(f"Login attempt on inactive account: {email}")
                raise AuthenticationError("Account is deactivated")
            
            # Verify password
            if not user.check_password(password):
                user.record_failed_login()
                db.commit()
                logger.warning(f"Failed login attempt for: {email}")
                raise AuthenticationError("Invalid email or password")
            
            # Successful login
            user.record_successful_login()
            
            # Generate tokens
            access_token = user.generate_jwt_token()
            refresh_token = user.generate_refresh_token()
            
            # Create session record
            session = UserSession(
                user_id=user.id,
                session_token=access_token,
                refresh_token=refresh_token,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=datetime.utcnow() + timedelta(hours=24)
            )
            
            db.add(session)
            db.commit()
            
            logger.info(f"Successful login: {email}")
            return user, access_token, refresh_token
    
    @staticmethod
    def verify_token(token: str) -> Optional[User]:
        """Verify JWT token and return user"""
        payload = User.verify_jwt_token(token)
        if not payload:
            return None
        
        with next(get_db_session()) as db:
            user = db.query(User).filter(User.id == payload['user_id']).first()
            
            if not user or not user.is_active:
                return None
            
            return user
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> Optional[str]:
        """Generate new access token from refresh token"""
        payload = User.verify_jwt_token(refresh_token)
        if not payload or payload.get('type') != 'refresh':
            return None
        
        with next(get_db_session()) as db:
            user = db.query(User).filter(User.id == payload['user_id']).first()
            
            if not user or not user.is_active:
                return None
            
            # Check if refresh token exists in sessions
            session = db.query(UserSession).filter(
                UserSession.refresh_token == refresh_token,
                UserSession.is_active == True
            ).first()
            
            if not session or session.is_expired():
                return None
            
            # Generate new access token
            new_access_token = user.generate_jwt_token()
            
            # Update session
            session.session_token = new_access_token
            session.extend_session()
            db.commit()
            
            return new_access_token
    
    @staticmethod
    def logout_user(token: str) -> bool:
        """Logout user by invalidating session"""
        with next(get_db_session()) as db:
            session = db.query(UserSession).filter(
                UserSession.session_token == token,
                UserSession.is_active == True
            ).first()
            
            if session:
                session.is_active = False
                db.commit()
                logger.info(f"User logged out: user_id={session.user_id}")
                return True
            
            return False
    
    @staticmethod
    def logout_all_sessions(user_id: int) -> int:
        """Logout user from all sessions"""
        with next(get_db_session()) as db:
            sessions = db.query(UserSession).filter(
                UserSession.user_id == user_id,
                UserSession.is_active == True
            ).all()
            
            count = 0
            for session in sessions:
                session.is_active = False
                count += 1
            
            db.commit()
            logger.info(f"Logged out from {count} sessions: user_id={user_id}")
            return count
    
    @staticmethod
    def change_password(user_id: int, current_password: str, new_password: str) -> bool:
        """Change user password"""
        with next(get_db_session()) as db:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                raise AuthenticationError("User not found")
            
            # Verify current password
            if not user.check_password(current_password):
                raise AuthenticationError("Current password is incorrect")
            
            # Validate new password
            if not User.validate_password_strength(new_password):
                raise AuthenticationError(
                    "New password must be at least 8 characters long and contain "
                    "uppercase, lowercase, digit, and special character"
                )
            
            # Set new password
            user.set_password(new_password)
            db.commit()
            
            # Logout from all other sessions for security
            AuthService.logout_all_sessions(user_id)
            
            logger.info(f"Password changed for user: {user.email}")
            return True
    
    @staticmethod
    def request_password_reset(email: str) -> Optional[str]:
        """Request password reset token"""
        with next(get_db_session()) as db:
            user = db.query(User).filter(User.email == email.lower()).first()
            
            if not user:
                # Don't reveal if email exists
                logger.warning(f"Password reset requested for non-existent email: {email}")
                return None
            
            # Generate reset token
            reset_token = secrets.token_urlsafe(32)
            user.password_reset_token = reset_token
            user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
            
            db.commit()
            
            logger.info(f"Password reset requested for: {email}")
            return reset_token
    
    @staticmethod
    def reset_password(reset_token: str, new_password: str) -> bool:
        """Reset password using reset token"""
        with next(get_db_session()) as db:
            user = db.query(User).filter(
                User.password_reset_token == reset_token
            ).first()
            
            if not user:
                raise AuthenticationError("Invalid reset token")
            
            # Check if token is expired
            if not user.password_reset_expires or datetime.utcnow() > user.password_reset_expires:
                raise AuthenticationError("Reset token has expired")
            
            # Validate new password
            if not User.validate_password_strength(new_password):
                raise AuthenticationError(
                    "Password must be at least 8 characters long and contain "
                    "uppercase, lowercase, digit, and special character"
                )
            
            # Set new password and clear reset token
            user.set_password(new_password)
            user.password_reset_token = None
            user.password_reset_expires = None
            user.unlock_account()  # Unlock account if it was locked
            
            db.commit()
            
            # Logout from all sessions for security
            AuthService.logout_all_sessions(user.id)
            
            logger.info(f"Password reset completed for: {user.email}")
            return True
    
    @staticmethod
    def verify_email(verification_token: str) -> bool:
        """Verify user email with verification token"""
        with next(get_db_session()) as db:
            user = db.query(User).filter(
                User.email_verification_token == verification_token
            ).first()
            
            if not user:
                return False
            
            user.email_verified = True
            user.is_verified = True
            user.email_verification_token = None
            
            db.commit()
            
            logger.info(f"Email verified for: {user.email}")
            return True
    
    @staticmethod
    def get_user_sessions(user_id: int) -> list:
        """Get all active sessions for user"""
        with next(get_db_session()) as db:
            sessions = db.query(UserSession).filter(
                UserSession.user_id == user_id,
                UserSession.is_active == True
            ).order_by(UserSession.last_activity.desc()).all()
            
            return [session.to_dict() for session in sessions]
    
    @staticmethod
    def update_user_profile(
        user_id: int,
        first_name: str = None,
        last_name: str = None,
        phone: str = None,
        agency_name: str = None,
        license_number: str = None,
        bio: str = None,
        website: str = None
    ) -> User:
        """Update user profile information"""
        with next(get_db_session()) as db:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                raise AuthenticationError("User not found")
            
            # Update provided fields
            if first_name is not None:
                user.first_name = first_name
            if last_name is not None:
                user.last_name = last_name
            if phone is not None:
                user.phone = phone
            if agency_name is not None:
                user.agency_name = agency_name
            if license_number is not None:
                user.license_number = license_number
            if bio is not None:
                user.bio = bio
            if website is not None:
                user.website = website
            
            db.commit()
            db.refresh(user)
            
            logger.info(f"Profile updated for: {user.email}")
            return user
    
    @staticmethod
    def deactivate_user(user_id: int) -> bool:
        """Deactivate user account"""
        with next(get_db_session()) as db:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return False
            
            user.is_active = False
            db.commit()
            
            # Logout from all sessions
            AuthService.logout_all_sessions(user_id)
            
            logger.info(f"User deactivated: {user.email}")
            return True
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """Get user by ID"""
        with next(get_db_session()) as db:
            return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email"""
        with next(get_db_session()) as db:
            return db.query(User).filter(User.email == email.lower()).first()