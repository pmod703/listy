# 🗄️ Database Documentation - Real Estate Open Home Optimizer

## Overview

This document provides comprehensive information about the database schema, setup, and usage for the Real Estate Open Home Optimizer application.

## 📊 Database Schema

### **Entity Relationship Diagram**

```
┌─────────────┐    ┌─────────────────┐    ┌─────────────────────┐
│    Users    │    │   Properties    │    │ Property Inspections│
│             │    │                 │    │                     │
│ • id (PK)   │◄──┤ • user_id (FK)  │◄──┤ • property_id (FK)  │
│ • email     │    │ • suburb_id(FK) │    │ • inspection_date   │
│ • password  │    │ • bedrooms      │    │ • start_time        │
│ • name      │    │ • bathrooms     │    │ • end_time          │
│ • agency    │    │ • car_spaces    │    │ • competition_level │
└─────────────┘    │ • property_type │    └─────────────────────┘
                   │ • listing_price │
                   └─────────────────┘
                           │
                           ▼
                   ┌─────────────────┐
                   │    Suburbs      │
                   │                 │
                   │ • id (PK)       │
                   │ • name          │
                   │ • postcode      │
                   │ • latitude      │
                   │ • longitude     │
                   │ • median_price  │
                   └─────────────────┘

┌─────────────────────────┐    ┌─────────────────────┐
│ Similar Property        │    │ Analysis Results    │
│ Criteria                │    │                     │
│                         │    │ • id (PK)           │
│ • id (PK)               │◄──┤ • criteria_id (FK)  │
│ • user_id (FK)          │    │ • property_id (FK)  │
│ • property_id (FK)      │    │ • user_id (FK)      │
│ • bedrooms_criteria     │    │ • analysis_date     │
│ • bathrooms_criteria    │    │ • time_slot_analysis│
│ • car_spaces_criteria   │    │ • recommendations   │
│ • bedrooms_min/max      │    │ • data_source       │
│ • bathrooms_min/max     │    └─────────────────────┘
│ • car_spaces_min/max    │
└─────────────────────────┘
```

## 🏗️ Table Structures

### **1. Users Table**
Stores real estate agent information and authentication data.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    agency_name VARCHAR(255),
    license_number VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

### **2. Suburbs Table**
Master data for suburbs with market information.

```sql
CREATE TABLE suburbs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    postcode VARCHAR(10) NOT NULL,
    state VARCHAR(10) NOT NULL DEFAULT 'NSW',
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    median_price DECIMAL(12, 2),
    market_trend VARCHAR(20), -- 'rising', 'stable', 'declining'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **3. Properties Table**
Property listings with detailed information.

```sql
CREATE TABLE properties (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    suburb_id INTEGER REFERENCES suburbs(id),
    
    -- Address Information
    street_number VARCHAR(20),
    street_name VARCHAR(255) NOT NULL,
    unit_number VARCHAR(20),
    full_address TEXT NOT NULL,
    
    -- Property Details
    property_type VARCHAR(50) NOT NULL,
    bedrooms INTEGER NOT NULL,
    bathrooms INTEGER NOT NULL,
    car_spaces INTEGER DEFAULT 0,
    land_size DECIMAL(10, 2),
    building_size DECIMAL(10, 2),
    
    -- Property Features
    has_pool BOOLEAN DEFAULT FALSE,
    has_garage BOOLEAN DEFAULT FALSE,
    has_garden BOOLEAN DEFAULT FALSE,
    has_balcony BOOLEAN DEFAULT FALSE,
    year_built INTEGER,
    
    -- Listing Information
    listing_price DECIMAL(12, 2),
    price_range_min DECIMAL(12, 2),
    price_range_max DECIMAL(12, 2),
    listing_status VARCHAR(20) DEFAULT 'active',
    listing_date DATE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **4. Property Inspections Table**
Scheduled and completed property inspections.

```sql
CREATE TABLE property_inspections (
    id SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES properties(id) ON DELETE CASCADE,
    
    inspection_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    
    status VARCHAR(20) DEFAULT 'scheduled',
    attendee_count INTEGER DEFAULT 0,
    feedback_score DECIMAL(3, 2),
    notes TEXT,
    
    -- Competition Data
    competing_inspections_count INTEGER DEFAULT 0,
    competition_level VARCHAR(20),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **5. Similar Property Criteria Table**
User-defined criteria for finding similar properties.

```sql
CREATE TABLE similar_property_criteria (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    property_id INTEGER REFERENCES properties(id) ON DELETE CASCADE,
    
    -- Criteria Settings (user input)
    bedrooms_criteria VARCHAR(20) NOT NULL,    -- '3', '3-4', '3+'
    bathrooms_criteria VARCHAR(20) NOT NULL,
    car_spaces_criteria VARCHAR(20) NOT NULL,
    
    -- Parsed Criteria (for querying)
    bedrooms_min INTEGER,
    bedrooms_max INTEGER,
    bathrooms_min INTEGER,
    bathrooms_max INTEGER,
    car_spaces_min INTEGER,
    car_spaces_max INTEGER,
    
    -- Additional Filters
    property_types TEXT[],
    price_range_percentage DECIMAL(5, 2) DEFAULT 20.00,
    radius_km DECIMAL(5, 2) DEFAULT 5.00,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **6. Analysis Results Table**
Results from competition analysis runs.

```sql
CREATE TABLE analysis_results (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    property_id INTEGER REFERENCES properties(id) ON DELETE CASCADE,
    criteria_id INTEGER REFERENCES similar_property_criteria(id),
    
    analysis_date DATE NOT NULL,
    time_window_start TIME NOT NULL,
    time_window_end TIME NOT NULL,
    search_radius_km DECIMAL(5, 2) NOT NULL,
    
    total_properties_found INTEGER DEFAULT 0,
    similar_properties_count INTEGER DEFAULT 0,
    filter_efficiency_percentage DECIMAL(5, 2),
    
    -- JSON data for flexibility
    time_slot_analysis JSONB,
    recommendations JSONB,
    
    peak_competition_time TIME,
    lowest_competition_time TIME,
    average_competition_level DECIMAL(3, 2),
    
    data_source VARCHAR(50) DEFAULT 'mock_data',
    api_response_time_ms INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🚀 Database Setup

### **Prerequisites**
- PostgreSQL 12+ installed
- Python 3.8+ with pip
- Virtual environment (recommended)

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Environment Configuration**
Create a `.env` file in your project root:

```bash
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
```

### **3. Database Initialization**

#### **Option 1: Full Initialization (Recommended)**
```bash
python database_migration.py init
```
This will:
- Create the database
- Create all tables
- Seed with sample data

#### **Option 2: Step by Step**
```bash
# Create database
python database_migration.py create-db

# Create tables
python database_migration.py create-tables

# Seed sample data
python database_migration.py seed
```

#### **Option 3: Using SQL File**
```bash
# Run the SQL schema file directly
python database_migration.py --sql database_schemas.sql
```

### **4. Verify Installation**
```bash
# Check database connection
python database_migration.py check

# Get table information
python database_migration.py info
```

## 🔧 Database Management

### **Migration Commands**

```bash
# Initialize everything
python database_migration.py init

# Check connection
python database_migration.py check

# Get table info and row counts
python database_migration.py info

# Create backup
python database_migration.py backup --file backup.sql

# Restore from backup
python database_migration.py restore --file backup.sql

# Reset database (drop and recreate)
python database_migration.py reset

# Drop all tables
python database_migration.py drop-tables
```

### **Using Python Models**

```python
from database_models import User, Property, SimilarPropertyCriteria
from database_config import get_db_session

# Create a new user
with get_db_session() as db:
    user = User(
        email="agent@example.com",
        password_hash="hashed_password",
        first_name="John",
        last_name="Doe",
        agency_name="Best Real Estate"
    )
    db.add(user)
    db.commit()

# Create a property
with get_db_session() as db:
    property = Property(
        user_id=1,
        full_address="123 Main St, Sydney NSW 2000",
        property_type="house",
        bedrooms=3,
        bathrooms=2,
        car_spaces=1,
        listing_price=800000.00
    )
    db.add(property)
    db.commit()

# Create similar property criteria
with get_db_session() as db:
    criteria = SimilarPropertyCriteria(
        user_id=1,
        property_id=1,
        bedrooms_criteria="3-4",
        bathrooms_criteria="2+",
        car_spaces_criteria="1-2"
    )
    criteria.parse_criteria()  # Parse criteria strings
    db.add(criteria)
    db.commit()
```

## 📊 Sample Queries

### **Find Similar Properties**
```sql
-- Find properties similar to a 3-bedroom house
SELECT p.full_address, p.bedrooms, p.bathrooms, p.car_spaces, p.listing_price
FROM properties p
JOIN suburbs s ON p.suburb_id = s.id
WHERE p.bedrooms BETWEEN 3 AND 4
  AND p.bathrooms >= 2
  AND p.car_spaces BETWEEN 1 AND 2
  AND p.listing_status = 'active'
ORDER BY p.listing_price;
```

### **Competition Analysis**
```sql
-- Get competition levels by time slot
SELECT 
    pi.start_time,
    COUNT(*) as inspection_count,
    CASE 
        WHEN COUNT(*) <= 2 THEN 'low'
        WHEN COUNT(*) <= 5 THEN 'medium'
        WHEN COUNT(*) <= 10 THEN 'high'
        ELSE 'very-high'
    END as competition_level
FROM property_inspections pi
WHERE pi.inspection_date = '2024-01-20'
  AND pi.status = 'scheduled'
GROUP BY pi.start_time
ORDER BY pi.start_time;
```

### **Market Insights**
```sql
-- Get market trends by suburb
SELECT 
    s.name as suburb,
    s.median_price,
    s.market_trend,
    COUNT(p.id) as active_listings,
    AVG(p.listing_price) as avg_listing_price
FROM suburbs s
LEFT JOIN properties p ON s.id = p.suburb_id AND p.listing_status = 'active'
GROUP BY s.id, s.name, s.median_price, s.market_trend
ORDER BY s.median_price DESC;
```

### **User Activity**
```sql
-- Get user analysis history
SELECT 
    u.first_name || ' ' || u.last_name as agent_name,
    COUNT(ar.id) as total_analyses,
    MAX(ar.created_at) as last_analysis,
    AVG(ar.similar_properties_count) as avg_similar_properties
FROM users u
LEFT JOIN analysis_results ar ON u.id = ar.user_id
GROUP BY u.id, agent_name
ORDER BY total_analyses DESC;
```

## 🔍 Views and Functions

### **Useful Views**

```sql
-- Property listings with suburb info
CREATE VIEW property_listings AS
SELECT 
    p.id, p.full_address, p.property_type,
    p.bedrooms, p.bathrooms, p.car_spaces,
    p.listing_price, s.name as suburb_name,
    u.first_name || ' ' || u.last_name as agent_name
FROM properties p
JOIN suburbs s ON p.suburb_id = s.id
JOIN users u ON p.user_id = u.id
WHERE p.listing_status = 'active';

-- Upcoming inspections
CREATE VIEW upcoming_inspections AS
SELECT 
    pi.inspection_date, pi.start_time, pi.end_time,
    p.full_address, p.bedrooms, p.bathrooms,
    pi.competition_level
FROM property_inspections pi
JOIN properties p ON pi.property_id = p.id
WHERE pi.inspection_date >= CURRENT_DATE
  AND pi.status = 'scheduled'
ORDER BY pi.inspection_date, pi.start_time;
```

### **Business Logic Functions**

```sql
-- Parse criteria strings
CREATE OR REPLACE FUNCTION parse_criteria(criteria_str VARCHAR(20))
RETURNS TABLE(min_val INTEGER, max_val INTEGER);

-- Find similar properties
CREATE OR REPLACE FUNCTION find_similar_properties(
    target_property_id INTEGER,
    criteria_id INTEGER
)
RETURNS TABLE(property_id INTEGER, similarity_score DECIMAL(3, 2));
```

## 🔒 Security Considerations

### **Database Security**
- Use strong passwords for database users
- Limit database user permissions
- Enable SSL connections in production
- Regular security updates for PostgreSQL

### **Application Security**
- Password hashing with bcrypt
- SQL injection prevention with parameterized queries
- Input validation and sanitization
- JWT tokens for authentication

### **Data Privacy**
- Personal information encryption
- GDPR compliance considerations
- Data retention policies
- Audit logging for sensitive operations

## 🚀 Performance Optimization

### **Indexes**
Key indexes are automatically created:
- `idx_users_email` - Fast user lookups
- `idx_properties_search` - Property search optimization
- `idx_inspections_date_time` - Time-based queries
- `idx_analysis_time_slots` - JSON analysis data

### **Query Optimization**
- Use EXPLAIN ANALYZE for slow queries
- Consider partitioning for large tables
- Regular VACUUM and ANALYZE operations
- Connection pooling for high traffic

### **Monitoring**
- Track slow queries
- Monitor connection pool usage
- Database size and growth trends
- Index usage statistics

## 🔄 Backup and Recovery

### **Backup Strategy**
```bash
# Daily backup
pg_dump -h localhost -U postgres realestate_optimizer > backup_$(date +%Y%m%d).sql

# Compressed backup
pg_dump -h localhost -U postgres realestate_optimizer | gzip > backup_$(date +%Y%m%d).sql.gz
```

### **Recovery**
```bash
# Restore from backup
psql -h localhost -U postgres -d realestate_optimizer < backup_20240120.sql
```

### **Point-in-Time Recovery**
Configure PostgreSQL for WAL archiving and point-in-time recovery in production.

## 📈 Scaling Considerations

### **Horizontal Scaling**
- Read replicas for query distribution
- Connection pooling (PgBouncer)
- Application-level caching (Redis)

### **Vertical Scaling**
- Increase PostgreSQL memory settings
- SSD storage for better I/O
- CPU optimization for complex queries

### **Data Archiving**
- Archive old analysis results
- Partition large tables by date
- Implement data lifecycle policies

## 🧪 Testing

### **Test Database Setup**
```bash
# Set environment for testing
export ENVIRONMENT=testing
python database_migration.py init
```

### **Sample Test Data**
```python
# Use factory_boy for test data generation
from factory_boy import Factory
from database_models import User, Property

class UserFactory(Factory):
    class Meta:
        model = User
    
    email = "test@example.com"
    first_name = "Test"
    last_name = "User"
```

This comprehensive database schema supports all the features of your Real Estate Open Home Optimizer, including the Similar Property Criteria functionality we implemented. The schema is designed for scalability, performance, and maintainability.