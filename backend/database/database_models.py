#!/usr/bin/env python3
"""
Database Models for Real Estate Open Home Optimizer
Using SQLAlchemy ORM for Python integration
"""

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Date, Time, Text, DECIMAL, ForeignKey, ARRAY, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime, date, time
import os
from typing import List, Optional

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://username:password@localhost:5432/realestate_optimizer')

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# =====================================================
# DATABASE MODELS
# =====================================================

class User(Base):
    """Real estate agents and users of the system"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    agency_name = Column(String(255))
    license_number = Column(String(100))
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime)
    
    # Relationships
    properties = relationship("Property", back_populates="user", cascade="all, delete-orphan")
    criteria = relationship("SimilarPropertyCriteria", back_populates="user", cascade="all, delete-orphan")
    analysis_results = relationship("AnalysisResult", back_populates="user", cascade="all, delete-orphan")
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def __repr__(self):
        return f"<User(email='{self.email}', name='{self.full_name}')>"

class Suburb(Base):
    """Suburb/location master data with market information"""
    __tablename__ = "suburbs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    postcode = Column(String(10), nullable=False)
    state = Column(String(10), nullable=False, default='NSW')
    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(11, 8))
    median_price = Column(DECIMAL(12, 2))
    market_trend = Column(String(20))  # 'rising', 'stable', 'declining'
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    properties = relationship("Property", back_populates="suburb")
    
    def __repr__(self):
        return f"<Suburb(name='{self.name}', postcode='{self.postcode}')>"

class Property(Base):
    """Property listings with detailed information"""
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    suburb_id = Column(Integer, ForeignKey("suburbs.id"))
    
    # Address Information
    street_number = Column(String(20))
    street_name = Column(String(255), nullable=False)
    unit_number = Column(String(20))
    full_address = Column(Text, nullable=False)
    
    # Property Details
    property_type = Column(String(50), nullable=False)  # 'house', 'apartment', 'townhouse', 'villa', 'studio'
    bedrooms = Column(Integer, nullable=False)
    bathrooms = Column(Integer, nullable=False)
    car_spaces = Column(Integer, default=0)
    land_size = Column(DECIMAL(10, 2))  # in square meters
    building_size = Column(DECIMAL(10, 2))  # in square meters
    
    # Property Features
    has_pool = Column(Boolean, default=False)
    has_garage = Column(Boolean, default=False)
    has_garden = Column(Boolean, default=False)
    has_balcony = Column(Boolean, default=False)
    year_built = Column(Integer)
    
    # Listing Information
    listing_price = Column(DECIMAL(12, 2))
    price_range_min = Column(DECIMAL(12, 2))
    price_range_max = Column(DECIMAL(12, 2))
    listing_status = Column(String(20), default='active')  # 'active', 'sold', 'withdrawn'
    listing_date = Column(Date)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="properties")
    suburb = relationship("Suburb", back_populates="properties")
    inspections = relationship("PropertyInspection", back_populates="property_ref", cascade="all, delete-orphan")
    criteria = relationship("SimilarPropertyCriteria", back_populates="property", cascade="all, delete-orphan")
    analysis_results = relationship("AnalysisResult", back_populates="property", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Property(address='{self.full_address}', type='{self.property_type}')>"

class PropertyInspection(Base):
    """Scheduled and completed property inspections"""
    __tablename__ = "property_inspections"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    
    # Inspection Details
    inspection_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    
    # Status and Tracking
    status = Column(String(20), default='scheduled')  # 'scheduled', 'completed', 'cancelled'
    attendee_count = Column(Integer, default=0)
    feedback_score = Column(DECIMAL(3, 2))  # 1.00 to 5.00
    notes = Column(Text)
    
    # Competition Data (from analysis)
    competing_inspections_count = Column(Integer, default=0)
    competition_level = Column(String(20))  # 'low', 'medium', 'high', 'very-high'
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    property_ref = relationship("Property", back_populates="inspections")
    
    @property
    def duration_minutes(self):
        """Calculate duration in minutes"""
        if self.start_time and self.end_time:
            start_seconds = self.start_time.hour * 3600 + self.start_time.minute * 60
            end_seconds = self.end_time.hour * 3600 + self.end_time.minute * 60
            return (end_seconds - start_seconds) // 60
        return 0
    
    def __repr__(self):
        return f"<PropertyInspection(date='{self.inspection_date}', time='{self.start_time}-{self.end_time}')>"

class SimilarPropertyCriteria(Base):
    """User-defined criteria for finding similar properties"""
    __tablename__ = "similar_property_criteria"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    
    # Criteria Settings (user input)
    bedrooms_criteria = Column(String(20), nullable=False)  # '3', '3-4', '3+', etc.
    bathrooms_criteria = Column(String(20), nullable=False)
    car_spaces_criteria = Column(String(20), nullable=False)
    
    # Parsed Criteria (for faster querying)
    bedrooms_min = Column(Integer)
    bedrooms_max = Column(Integer)  # NULL for unlimited (e.g., '3+')
    bathrooms_min = Column(Integer)
    bathrooms_max = Column(Integer)
    car_spaces_min = Column(Integer)
    car_spaces_max = Column(Integer)
    
    # Additional Filters
    property_types = Column(ARRAY(String))  # Array of property types to include
    price_range_percentage = Column(DECIMAL(5, 2), default=20.00)  # ±20% of listing price
    radius_km = Column(DECIMAL(5, 2), default=5.00)  # Search radius in kilometers
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="criteria")
    property = relationship("Property", back_populates="criteria")
    analysis_results = relationship("AnalysisResult", back_populates="criteria")
    
    def parse_criteria(self):
        """Parse criteria strings into min/max values"""
        def parse_single_criteria(criteria_str):
            if '+' in criteria_str:
                min_val = int(criteria_str.replace('+', ''))
                max_val = None  # Unlimited
            elif '-' in criteria_str:
                parts = criteria_str.split('-')
                min_val = int(parts[0])
                max_val = int(parts[1])
            else:
                val = int(criteria_str)
                min_val = max_val = val
            return min_val, max_val
        
        # Parse all criteria
        self.bedrooms_min, self.bedrooms_max = parse_single_criteria(self.bedrooms_criteria)
        self.bathrooms_min, self.bathrooms_max = parse_single_criteria(self.bathrooms_criteria)
        self.car_spaces_min, self.car_spaces_max = parse_single_criteria(self.car_spaces_criteria)
    
    def __repr__(self):
        return f"<SimilarPropertyCriteria(bed='{self.bedrooms_criteria}', bath='{self.bathrooms_criteria}', car='{self.car_spaces_criteria}')>"

class AnalysisResult(Base):
    """Results from competition analysis runs"""
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    criteria_id = Column(Integer, ForeignKey("similar_property_criteria.id", ondelete="SET NULL"))
    
    # Analysis Parameters
    analysis_date = Column(Date, nullable=False)
    time_window_start = Column(Time, nullable=False)
    time_window_end = Column(Time, nullable=False)
    search_radius_km = Column(DECIMAL(5, 2), nullable=False)
    
    # Results Summary
    total_properties_found = Column(Integer, default=0)
    similar_properties_count = Column(Integer, default=0)
    filter_efficiency_percentage = Column(DECIMAL(5, 2))  # similar/total * 100
    
    # Competition Analysis (JSON format for flexibility)
    time_slot_analysis = Column(JSON)  # Array of time slots with competition data
    recommendations = Column(JSON)  # Top recommended time slots
    
    # Market Insights
    peak_competition_time = Column(Time)
    lowest_competition_time = Column(Time)
    average_competition_level = Column(DECIMAL(3, 2))
    
    # Data Source Information
    data_source = Column(String(50), default='mock_data')  # 'mock_data', 'domain_api', 'manual'
    api_response_time_ms = Column(Integer)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="analysis_results")
    property = relationship("Property", back_populates="analysis_results")
    criteria = relationship("SimilarPropertyCriteria", back_populates="analysis_results")
    
    @property
    def filter_efficiency(self):
        """Calculate filter efficiency percentage"""
        if self.total_properties_found > 0:
            return (self.similar_properties_count / self.total_properties_found) * 100
        return 0
    
    def __repr__(self):
        return f"<AnalysisResult(date='{self.analysis_date}', similar={self.similar_properties_count}/{self.total_properties_found})>"

# =====================================================
# DATABASE UTILITY FUNCTIONS
# =====================================================

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """Drop all tables in the database"""
    Base.metadata.drop_all(bind=engine)

def init_sample_data():
    """Initialize database with sample data"""
    db = SessionLocal()
    try:
        # Create sample suburbs
        suburbs_data = [
            {"name": "Bondi", "postcode": "2026", "latitude": -33.8915, "longitude": 151.2767, "median_price": 1500000.00, "market_trend": "rising"},
            {"name": "Surry Hills", "postcode": "2010", "latitude": -33.8886, "longitude": 151.2094, "median_price": 1200000.00, "market_trend": "stable"},
            {"name": "Paddington", "postcode": "2021", "latitude": -33.8848, "longitude": 151.2299, "median_price": 1800000.00, "market_trend": "rising"},
            {"name": "Newtown", "postcode": "2042", "latitude": -33.8978, "longitude": 151.1794, "median_price": 1100000.00, "market_trend": "rising"},
            {"name": "Manly", "postcode": "2095", "latitude": -33.7969, "longitude": 151.2767, "median_price": 1600000.00, "market_trend": "stable"},
        ]
        
        for suburb_data in suburbs_data:
            existing = db.query(Suburb).filter(Suburb.name == suburb_data["name"], Suburb.postcode == suburb_data["postcode"]).first()
            if not existing:
                suburb = Suburb(**suburb_data)
                db.add(suburb)
        
        # Create sample user
        existing_user = db.query(User).filter(User.email == "agent@realestate.com").first()
        if not existing_user:
            user = User(
                email="agent@realestate.com",
                password_hash="$2b$12$example_hash",
                first_name="John",
                last_name="Smith",
                agency_name="Premium Real Estate",
                license_number="RE123456"
            )
            db.add(user)
        
        db.commit()
        print("✅ Sample data initialized successfully")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error initializing sample data: {e}")
    finally:
        db.close()

# =====================================================
# BUSINESS LOGIC FUNCTIONS
# =====================================================

class PropertyService:
    """Service class for property-related operations"""
    
    @staticmethod
    def create_property(db, user_id: int, property_data: dict) -> Property:
        """Create a new property"""
        property_obj = Property(user_id=user_id, **property_data)
        db.add(property_obj)
        db.commit()
        db.refresh(property_obj)
        return property_obj
    
    @staticmethod
    def get_properties_by_user(db, user_id: int) -> List[Property]:
        """Get all properties for a user"""
        return db.query(Property).filter(Property.user_id == user_id).all()
    
    @staticmethod
    def find_similar_properties(db, property_id: int, criteria: SimilarPropertyCriteria) -> List[Property]:
        """Find properties similar to the given property based on criteria"""
        query = db.query(Property).filter(
            Property.id != property_id,
            Property.listing_status == 'active'
        )
        
        # Apply bedroom criteria
        if criteria.bedrooms_max:
            query = query.filter(Property.bedrooms.between(criteria.bedrooms_min, criteria.bedrooms_max))
        else:
            query = query.filter(Property.bedrooms >= criteria.bedrooms_min)
        
        # Apply bathroom criteria
        if criteria.bathrooms_max:
            query = query.filter(Property.bathrooms.between(criteria.bathrooms_min, criteria.bathrooms_max))
        else:
            query = query.filter(Property.bathrooms >= criteria.bathrooms_min)
        
        # Apply car spaces criteria
        if criteria.car_spaces_max:
            query = query.filter(Property.car_spaces.between(criteria.car_spaces_min, criteria.car_spaces_max))
        else:
            query = query.filter(Property.car_spaces >= criteria.car_spaces_min)
        
        # Apply property type filter if specified
        if criteria.property_types:
            query = query.filter(Property.property_type.in_(criteria.property_types))
        
        return query.all()

class AnalysisService:
    """Service class for analysis-related operations"""
    
    @staticmethod
    def create_analysis_result(db, analysis_data: dict) -> AnalysisResult:
        """Create a new analysis result"""
        analysis = AnalysisResult(**analysis_data)
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        return analysis
    
    @staticmethod
    def get_latest_analysis(db, property_id: int) -> Optional[AnalysisResult]:
        """Get the latest analysis for a property"""
        return db.query(AnalysisResult).filter(
            AnalysisResult.property_id == property_id
        ).order_by(AnalysisResult.created_at.desc()).first()
    
    @staticmethod
    def get_analysis_history(db, user_id: int, limit: int = 10) -> List[AnalysisResult]:
        """Get analysis history for a user"""
        return db.query(AnalysisResult).filter(
            AnalysisResult.user_id == user_id
        ).order_by(AnalysisResult.created_at.desc()).limit(limit).all()

# =====================================================
# EXAMPLE USAGE
# =====================================================

if __name__ == "__main__":
    # Create tables
    create_tables()
    
    # Initialize sample data
    init_sample_data()
    
    print("✅ Database models and sample data created successfully!")
    print("📊 Available tables:")
    print("  - users")
    print("  - suburbs") 
    print("  - properties")
    print("  - property_inspections")
    print("  - similar_property_criteria")
    print("  - analysis_results")
    print("")
    print("🔗 Connection string format:")
    print("  postgresql://username:password@localhost:5432/realestate_optimizer")
    print("")
    print("💡 Update DATABASE_URL environment variable with your connection details")