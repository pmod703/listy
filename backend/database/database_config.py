#!/usr/bin/env python3
"""
Database Configuration for Real Estate Open Home Optimizer
Centralized database settings and connection management
"""

import os
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

class DatabaseConfig:
    """Database configuration class"""
    
    def __init__(self):
        # Database connection parameters
        self.DB_HOST = os.getenv('DB_HOST', 'localhost')
        self.DB_PORT = os.getenv('DB_PORT', '5432')
        self.DB_NAME = os.getenv('DB_NAME', 'realestate_optimizer')
        self.DB_USER = os.getenv('DB_USER', 'postgres')
        self.DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
        
        # Connection pool settings
        self.POOL_SIZE = int(os.getenv('DB_POOL_SIZE', '5'))
        self.MAX_OVERFLOW = int(os.getenv('DB_MAX_OVERFLOW', '10'))
        self.POOL_TIMEOUT = int(os.getenv('DB_POOL_TIMEOUT', '30'))
        self.POOL_RECYCLE = int(os.getenv('DB_POOL_RECYCLE', '3600'))
        
        # Environment settings
        self.ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
        self.DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
        
    @property
    def database_url(self) -> str:
        """Get the complete database URL"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def async_database_url(self) -> str:
        """Get the async database URL"""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    def get_engine(self, echo: Optional[bool] = None):
        """Create and return SQLAlchemy engine"""
        if echo is None:
            echo = self.DEBUG
            
        engine_kwargs = {
            'echo': echo,
            'pool_size': self.POOL_SIZE,
            'max_overflow': self.MAX_OVERFLOW,
            'pool_timeout': self.POOL_TIMEOUT,
            'pool_recycle': self.POOL_RECYCLE,
        }
        
        # For testing, use in-memory SQLite
        if self.ENVIRONMENT == 'testing':
            return create_engine(
                "sqlite:///:memory:",
                echo=echo,
                poolclass=StaticPool,
                connect_args={"check_same_thread": False}
            )
        
        return create_engine(self.database_url, **engine_kwargs)
    
    def get_session_factory(self):
        """Get SQLAlchemy session factory"""
        engine = self.get_engine()
        return sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Global configuration instance
db_config = DatabaseConfig()

# Convenience functions
def get_database_url() -> str:
    """Get database URL"""
    return db_config.database_url

def get_engine():
    """Get SQLAlchemy engine"""
    return db_config.get_engine()

def get_session_factory():
    """Get session factory"""
    return db_config.get_session_factory()

def get_db_session():
    """Get database session (context manager)"""
    SessionLocal = get_session_factory()
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

# Environment-specific configurations
class DevelopmentConfig(DatabaseConfig):
    """Development environment configuration"""
    def __init__(self):
        super().__init__()
        self.DEBUG = True

class ProductionConfig(DatabaseConfig):
    """Production environment configuration"""
    def __init__(self):
        super().__init__()
        self.DEBUG = False
        self.POOL_SIZE = 20
        self.MAX_OVERFLOW = 30

class TestingConfig(DatabaseConfig):
    """Testing environment configuration"""
    def __init__(self):
        super().__init__()
        self.ENVIRONMENT = 'testing'
        self.DEBUG = True
        self.DB_NAME = 'test_realestate_optimizer'

def get_config():
    """Get configuration based on environment"""
    env = os.getenv('ENVIRONMENT', 'development').lower()
    
    if env == 'production':
        return ProductionConfig()
    elif env == 'testing':
        return TestingConfig()
    else:
        return DevelopmentConfig()

# Example environment variables file content
ENV_TEMPLATE = """
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=realestate_optimizer
DB_USER=postgres
DB_PASSWORD=your_password_here

# Connection Pool Settings
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# Application Settings
ENVIRONMENT=development
DEBUG=True

# For production, also set:
# SECRET_KEY=your_secret_key_here
# FLASK_ENV=production
"""

if __name__ == "__main__":
    # Print current configuration
    config = get_config()
    
    print("🔧 Database Configuration")
    print("=" * 50)
    print(f"Environment: {config.ENVIRONMENT}")
    print(f"Host: {config.DB_HOST}:{config.DB_PORT}")
    print(f"Database: {config.DB_NAME}")
    print(f"User: {config.DB_USER}")
    print(f"Debug: {config.DEBUG}")
    print(f"Pool Size: {config.POOL_SIZE}")
    print(f"Max Overflow: {config.MAX_OVERFLOW}")
    print("=" * 50)
    print(f"Database URL: {config.database_url}")
    print("")
    
    # Test connection
    try:
        engine = config.get_engine()
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("✅ Database connection successful!")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("")
        print("💡 Create a .env file with the following content:")
        print(ENV_TEMPLATE)