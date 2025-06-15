#!/usr/bin/env python3
"""
Authentication Routes
Flask routes for user authentication and account management
"""

from flask import Blueprint, request, jsonify, g
from auth_service import AuthService, AuthenticationError
from auth_middleware import token_required, optional_auth, verified_user_required, get_current_user, extract_user_info
from marshmallow import Schema, fields, ValidationError
import logging

logger = logging.getLogger(__name__)

# Create authentication blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# =====================================================
# VALIDATION SCHEMAS
# =====================================================

class RegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=lambda x: len(x) >= 8)
    first_name = fields.Str(required=False, allow_none=True)
    last_name = fields.Str(required=False, allow_none=True)
    agency_name = fields.Str(required=False, allow_none=True)
    license_number = fields.Str(required=False, allow_none=True)
    phone = fields.Str(required=False, allow_none=True)

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class ChangePasswordSchema(Schema):
    current_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=lambda x: len(x) >= 8)

class ResetPasswordSchema(Schema):
    reset_token = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=lambda x: len(x) >= 8)

class UpdateProfileSchema(Schema):
    first_name = fields.Str(required=False, allow_none=True)
    last_name = fields.Str(required=False, allow_none=True)
    phone = fields.Str(required=False, allow_none=True)
    agency_name = fields.Str(required=False, allow_none=True)
    license_number = fields.Str(required=False, allow_none=True)
    bio = fields.Str(required=False, allow_none=True)
    website = fields.Str(required=False, allow_none=True)

# =====================================================
# AUTHENTICATION ROUTES
# =====================================================

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        # Validate request data
        schema = RegisterSchema()
        data = schema.load(request.get_json())
        
        # Extract user info for logging
        user_info = extract_user_info()
        
        # Register user
        user, token = AuthService.register_user(
            email=data['email'],
            password=data['password'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            agency_name=data.get('agency_name'),
            license_number=data.get('license_number'),
            phone=data.get('phone')
        )
        
        logger.info(f"User registered successfully: {user.email} from {user_info['ip_address']}")
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'access_token': token,
            'token_type': 'Bearer'
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    except AuthenticationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return tokens"""
    try:
        # Validate request data
        schema = LoginSchema()
        data = schema.load(request.get_json())
        
        # Extract user info for logging
        user_info = extract_user_info()
        
        # Authenticate user
        user, access_token, refresh_token = AuthService.authenticate_user(
            email=data['email'],
            password=data['password'],
            ip_address=user_info['ip_address'],
            user_agent=user_info['user_agent']
        )
        
        logger.info(f"User logged in successfully: {user.email} from {user_info['ip_address']}")
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer'
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    except AuthenticationError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """Refresh access token using refresh token"""
    try:
        data = request.get_json()
        refresh_token = data.get('refresh_token')
        
        if not refresh_token:
            return jsonify({'error': 'Refresh token is required'}), 400
        
        # Generate new access token
        new_access_token = AuthService.refresh_access_token(refresh_token)
        
        if not new_access_token:
            return jsonify({'error': 'Invalid or expired refresh token'}), 401
        
        return jsonify({
            'access_token': new_access_token,
            'token_type': 'Bearer'
        }), 200
        
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return jsonify({'error': 'Token refresh failed'}), 500

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """Logout current user"""
    try:
        current_user = get_current_user()
        token = g.token
        
        # Logout user
        success = AuthService.logout_user(token)
        
        if success:
            logger.info(f"User logged out: {current_user.email}")
            return jsonify({'message': 'Logout successful'}), 200
        else:
            return jsonify({'error': 'Logout failed'}), 400
            
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({'error': 'Logout failed'}), 500

@auth_bp.route('/logout-all', methods=['POST'])
@token_required
def logout_all():
    """Logout user from all sessions"""
    try:
        current_user = get_current_user()
        
        # Logout from all sessions
        count = AuthService.logout_all_sessions(current_user.id)
        
        logger.info(f"User logged out from all sessions: {current_user.email}")
        return jsonify({
            'message': f'Logged out from {count} sessions',
            'sessions_closed': count
        }), 200
        
    except Exception as e:
        logger.error(f"Logout all error: {e}")
        return jsonify({'error': 'Logout failed'}), 500

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user_info():
    """Get current user information"""
    try:
        current_user = get_current_user()
        
        return jsonify({
            'user': current_user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Get user info error: {e}")
        return jsonify({'error': 'Failed to get user information'}), 500

@auth_bp.route('/me', methods=['PUT'])
@token_required
def update_profile():
    """Update user profile"""
    try:
        current_user = get_current_user()
        
        # Validate request data
        schema = UpdateProfileSchema()
        data = schema.load(request.get_json())
        
        # Update profile
        updated_user = AuthService.update_user_profile(
            user_id=current_user.id,
            **data
        )
        
        logger.info(f"Profile updated: {current_user.email}")
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': updated_user.to_dict()
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    except AuthenticationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        return jsonify({'error': 'Profile update failed'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password():
    """Change user password"""
    try:
        current_user = get_current_user()
        
        # Validate request data
        schema = ChangePasswordSchema()
        data = schema.load(request.get_json())
        
        # Change password
        success = AuthService.change_password(
            user_id=current_user.id,
            current_password=data['current_password'],
            new_password=data['new_password']
        )
        
        if success:
            logger.info(f"Password changed: {current_user.email}")
            return jsonify({'message': 'Password changed successfully'}), 200
        else:
            return jsonify({'error': 'Password change failed'}), 400
            
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    except AuthenticationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Password change error: {e}")
        return jsonify({'error': 'Password change failed'}), 500

@auth_bp.route('/request-password-reset', methods=['POST'])
def request_password_reset():
    """Request password reset"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Request password reset
        reset_token = AuthService.request_password_reset(email)
        
        # Always return success to prevent email enumeration
        return jsonify({
            'message': 'If the email exists, a password reset link has been sent'
        }), 200
        
    except Exception as e:
        logger.error(f"Password reset request error: {e}")
        return jsonify({'error': 'Password reset request failed'}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password using reset token"""
    try:
        # Validate request data
        schema = ResetPasswordSchema()
        data = schema.load(request.get_json())
        
        # Reset password
        success = AuthService.reset_password(
            reset_token=data['reset_token'],
            new_password=data['new_password']
        )
        
        if success:
            logger.info("Password reset completed")
            return jsonify({'message': 'Password reset successful'}), 200
        else:
            return jsonify({'error': 'Password reset failed'}), 400
            
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    except AuthenticationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        return jsonify({'error': 'Password reset failed'}), 500

@auth_bp.route('/verify-email/<verification_token>', methods=['GET'])
def verify_email(verification_token):
    """Verify user email"""
    try:
        success = AuthService.verify_email(verification_token)
        
        if success:
            return jsonify({'message': 'Email verified successfully'}), 200
        else:
            return jsonify({'error': 'Invalid verification token'}), 400
            
    except Exception as e:
        logger.error(f"Email verification error: {e}")
        return jsonify({'error': 'Email verification failed'}), 500

@auth_bp.route('/sessions', methods=['GET'])
@token_required
def get_user_sessions():
    """Get user's active sessions"""
    try:
        current_user = get_current_user()
        
        sessions = AuthService.get_user_sessions(current_user.id)
        
        return jsonify({
            'sessions': sessions,
            'total_sessions': len(sessions)
        }), 200
        
    except Exception as e:
        logger.error(f"Get sessions error: {e}")
        return jsonify({'error': 'Failed to get sessions'}), 500

@auth_bp.route('/validate-token', methods=['GET'])
@optional_auth
def validate_token():
    """Validate token and return user info if valid"""
    try:
        current_user = get_current_user()
        
        if current_user:
            return jsonify({
                'valid': True,
                'user': current_user.to_dict()
            }), 200
        else:
            return jsonify({
                'valid': False,
                'message': 'Token is invalid or expired'
            }), 401
            
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        return jsonify({
            'valid': False,
            'error': 'Token validation failed'
        }), 500

# =====================================================
# ADMIN ROUTES (Optional)
# =====================================================

@auth_bp.route('/admin/users', methods=['GET'])
@token_required
def list_users():
    """List all users (admin only)"""
    try:
        current_user = get_current_user()
        
        # Simple admin check - you can enhance this
        if not current_user.email.endswith('@admin.com'):  # Example admin check
            return jsonify({'error': 'Admin access required'}), 403
        
        # In a real application, implement proper pagination
        # This is a simplified version
        return jsonify({
            'message': 'Admin endpoint - implement user listing',
            'note': 'This would return paginated user list'
        }), 200
        
    except Exception as e:
        logger.error(f"List users error: {e}")
        return jsonify({'error': 'Failed to list users'}), 500

# =====================================================
# ERROR HANDLERS
# =====================================================

@auth_bp.errorhandler(ValidationError)
def handle_validation_error(e):
    """Handle marshmallow validation errors"""
    return jsonify({'error': 'Validation failed', 'details': e.messages}), 400

@auth_bp.errorhandler(AuthenticationError)
def handle_auth_error(e):
    """Handle authentication errors"""
    return jsonify({'error': str(e)}), 401

@auth_bp.errorhandler(Exception)
def handle_general_error(e):
    """Handle general errors"""
    logger.error(f"Unhandled error in auth routes: {e}")
    return jsonify({'error': 'Internal server error'}), 500