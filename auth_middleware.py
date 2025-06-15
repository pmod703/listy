#!/usr/bin/env python3
"""
Authentication Middleware
Flask decorators and middleware for protecting routes
"""

from functools import wraps
from flask import request, jsonify, g
from auth_service import AuthService
from auth_models import User
import logging

logger = logging.getLogger(__name__)

def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                # Expected format: "Bearer <token>"
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Invalid authorization header format'}), 401
        
        # Check for token in query parameters (fallback)
        if not token:
            token = request.args.get('token')
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            # Verify token and get user
            current_user = AuthService.verify_token(token)
            if not current_user:
                return jsonify({'error': 'Token is invalid or expired'}), 401
            
            # Store user in Flask's g object for use in route
            g.current_user = current_user
            g.token = token
            
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return jsonify({'error': 'Token verification failed'}), 401
        
        return f(*args, **kwargs)
    
    return decorated

def optional_auth(f):
    """Decorator for optional authentication (user can be None)"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                pass
        
        # Check for token in query parameters
        if not token:
            token = request.args.get('token')
        
        g.current_user = None
        g.token = None
        
        if token:
            try:
                current_user = AuthService.verify_token(token)
                if current_user:
                    g.current_user = current_user
                    g.token = token
            except Exception as e:
                logger.warning(f"Optional auth token verification failed: {e}")
        
        return f(*args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # First check for valid token
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Invalid authorization header format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            current_user = AuthService.verify_token(token)
            if not current_user:
                return jsonify({'error': 'Token is invalid or expired'}), 401
            
            # Check if user has admin privileges
            # Note: You'll need to add an is_admin field to your User model
            # For now, we'll check if user has a specific email domain or license
            if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
                return jsonify({'error': 'Admin privileges required'}), 403
            
            g.current_user = current_user
            g.token = token
            
        except Exception as e:
            logger.error(f"Admin auth error: {e}")
            return jsonify({'error': 'Authentication failed'}), 401
        
        return f(*args, **kwargs)
    
    return decorated

def verified_user_required(f):
    """Decorator to require verified user (email verified)"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # First apply token_required logic
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Invalid authorization header format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            current_user = AuthService.verify_token(token)
            if not current_user:
                return jsonify({'error': 'Token is invalid or expired'}), 401
            
            # Check if user is verified
            if not current_user.is_email_verified:
                return jsonify({
                    'error': 'Email verification required',
                    'message': 'Please verify your email address to access this feature'
                }), 403
            
            g.current_user = current_user
            g.token = token
            
        except Exception as e:
            logger.error(f"Verified user auth error: {e}")
            return jsonify({'error': 'Authentication failed'}), 401
        
        return f(*args, **kwargs)
    
    return decorated

def rate_limit(max_requests: int = 100, window_minutes: int = 60):
    """Simple rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Get client IP
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            
            # For production, you'd want to use Redis or similar for rate limiting
            # This is a simple in-memory implementation for demonstration
            
            # In a real application, implement proper rate limiting with Redis
            # For now, we'll just log the request
            logger.info(f"Rate limit check for IP: {client_ip}")
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator

def get_current_user():
    """Helper function to get current user from Flask g object"""
    return getattr(g, 'current_user', None)

def get_current_token():
    """Helper function to get current token from Flask g object"""
    return getattr(g, 'token', None)

def extract_user_info():
    """Extract user information from request for logging"""
    user_info = {
        'ip_address': request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
        'user_agent': request.headers.get('User-Agent', ''),
        'method': request.method,
        'endpoint': request.endpoint,
        'url': request.url
    }
    
    current_user = get_current_user()
    if current_user:
        user_info.update({
            'user_id': current_user.id,
            'user_email': current_user.email
        })
    
    return user_info

class AuthMiddleware:
    """Authentication middleware class for Flask app"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize middleware with Flask app"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    def before_request(self):
        """Process request before handling"""
        # Log request information
        user_info = extract_user_info()
        logger.info(f"Request: {user_info['method']} {user_info['endpoint']} from {user_info['ip_address']}")
        
        # Add CORS headers for preflight requests
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            return response
    
    def after_request(self, response):
        """Process response after handling"""
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Add CORS headers
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        
        return response

# Custom exceptions for authentication
class AuthenticationRequired(Exception):
    """Exception raised when authentication is required"""
    pass

class InsufficientPermissions(Exception):
    """Exception raised when user lacks required permissions"""
    pass

class AccountLocked(Exception):
    """Exception raised when account is locked"""
    pass

class EmailNotVerified(Exception):
    """Exception raised when email verification is required"""
    pass