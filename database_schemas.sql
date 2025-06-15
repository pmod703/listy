-- =====================================================
-- Real Estate Open Home Optimizer - Database Schemas
-- =====================================================

-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS analysis_results CASCADE;
DROP TABLE IF EXISTS similar_property_criteria CASCADE;
DROP TABLE IF EXISTS property_inspections CASCADE;
DROP TABLE IF EXISTS properties CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS suburbs CASCADE;

-- =====================================================
-- 1. USERS TABLE
-- =====================================================
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

-- Index for faster email lookups
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active);

-- =====================================================
-- 2. SUBURBS TABLE
-- =====================================================
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

-- Unique constraint for suburb-postcode combination
CREATE UNIQUE INDEX idx_suburbs_name_postcode ON suburbs(name, postcode);
CREATE INDEX idx_suburbs_postcode ON suburbs(postcode);

-- =====================================================
-- 3. PROPERTIES TABLE
-- =====================================================
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
    property_type VARCHAR(50) NOT NULL, -- 'house', 'apartment', 'townhouse', 'villa', 'studio'
    bedrooms INTEGER NOT NULL,
    bathrooms INTEGER NOT NULL,
    car_spaces INTEGER DEFAULT 0,
    land_size DECIMAL(10, 2), -- in square meters
    building_size DECIMAL(10, 2), -- in square meters
    
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
    listing_status VARCHAR(20) DEFAULT 'active', -- 'active', 'sold', 'withdrawn'
    listing_date DATE,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_properties_user_id ON properties(user_id);
CREATE INDEX idx_properties_suburb_id ON properties(suburb_id);
CREATE INDEX idx_properties_type ON properties(property_type);
CREATE INDEX idx_properties_bedrooms ON properties(bedrooms);
CREATE INDEX idx_properties_status ON properties(listing_status);

-- =====================================================
-- 4. PROPERTY INSPECTIONS TABLE
-- =====================================================
CREATE TABLE property_inspections (
    id SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES properties(id) ON DELETE CASCADE,
    
    -- Inspection Details
    inspection_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    duration_minutes INTEGER GENERATED ALWAYS AS (
        EXTRACT(EPOCH FROM (end_time - start_time)) / 60
    ) STORED,
    
    -- Status and Tracking
    status VARCHAR(20) DEFAULT 'scheduled', -- 'scheduled', 'completed', 'cancelled'
    attendee_count INTEGER DEFAULT 0,
    feedback_score DECIMAL(3, 2), -- 1.00 to 5.00
    notes TEXT,
    
    -- Competition Data (from analysis)
    competing_inspections_count INTEGER DEFAULT 0,
    competition_level VARCHAR(20), -- 'low', 'medium', 'high', 'very-high'
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_inspections_property_id ON property_inspections(property_id);
CREATE INDEX idx_inspections_date ON property_inspections(inspection_date);
CREATE INDEX idx_inspections_status ON property_inspections(status);
CREATE INDEX idx_inspections_competition ON property_inspections(competition_level);

-- =====================================================
-- 5. SIMILAR PROPERTY CRITERIA TABLE
-- =====================================================
CREATE TABLE similar_property_criteria (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    property_id INTEGER REFERENCES properties(id) ON DELETE CASCADE,
    
    -- Criteria Settings
    bedrooms_criteria VARCHAR(20) NOT NULL, -- '3', '3-4', '3+', etc.
    bathrooms_criteria VARCHAR(20) NOT NULL,
    car_spaces_criteria VARCHAR(20) NOT NULL,
    
    -- Parsed Criteria (for faster querying)
    bedrooms_min INTEGER,
    bedrooms_max INTEGER, -- NULL for unlimited (e.g., '3+')
    bathrooms_min INTEGER,
    bathrooms_max INTEGER,
    car_spaces_min INTEGER,
    car_spaces_max INTEGER,
    
    -- Additional Filters
    property_types TEXT[], -- Array of property types to include
    price_range_percentage DECIMAL(5, 2) DEFAULT 20.00, -- ±20% of listing price
    radius_km DECIMAL(5, 2) DEFAULT 5.00, -- Search radius in kilometers
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_criteria_user_id ON similar_property_criteria(user_id);
CREATE INDEX idx_criteria_property_id ON similar_property_criteria(property_id);
CREATE INDEX idx_criteria_bedrooms_range ON similar_property_criteria(bedrooms_min, bedrooms_max);

-- =====================================================
-- 6. ANALYSIS RESULTS TABLE
-- =====================================================
CREATE TABLE analysis_results (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    property_id INTEGER REFERENCES properties(id) ON DELETE CASCADE,
    criteria_id INTEGER REFERENCES similar_property_criteria(id) ON DELETE SET NULL,
    
    -- Analysis Parameters
    analysis_date DATE NOT NULL,
    time_window_start TIME NOT NULL,
    time_window_end TIME NOT NULL,
    search_radius_km DECIMAL(5, 2) NOT NULL,
    
    -- Results Summary
    total_properties_found INTEGER DEFAULT 0,
    similar_properties_count INTEGER DEFAULT 0,
    filter_efficiency_percentage DECIMAL(5, 2), -- similar/total * 100
    
    -- Competition Analysis (JSON format for flexibility)
    time_slot_analysis JSONB, -- Array of time slots with competition data
    recommendations JSONB, -- Top recommended time slots
    
    -- Market Insights
    peak_competition_time TIME,
    lowest_competition_time TIME,
    average_competition_level DECIMAL(3, 2),
    
    -- Data Source Information
    data_source VARCHAR(50) DEFAULT 'mock_data', -- 'mock_data', 'domain_api', 'manual'
    api_response_time_ms INTEGER,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_analysis_user_id ON analysis_results(user_id);
CREATE INDEX idx_analysis_property_id ON analysis_results(property_id);
CREATE INDEX idx_analysis_date ON analysis_results(analysis_date);
CREATE INDEX idx_analysis_data_source ON analysis_results(data_source);

-- GIN index for JSONB columns
CREATE INDEX idx_analysis_time_slots ON analysis_results USING GIN (time_slot_analysis);
CREATE INDEX idx_analysis_recommendations ON analysis_results USING GIN (recommendations);

-- =====================================================
-- TRIGGERS FOR UPDATED_AT TIMESTAMPS
-- =====================================================

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to tables with updated_at columns
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_suburbs_updated_at BEFORE UPDATE ON suburbs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_properties_updated_at BEFORE UPDATE ON properties
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_inspections_updated_at BEFORE UPDATE ON property_inspections
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_criteria_updated_at BEFORE UPDATE ON similar_property_criteria
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- SAMPLE DATA INSERTS
-- =====================================================

-- Insert sample suburbs
INSERT INTO suburbs (name, postcode, state, latitude, longitude, median_price, market_trend) VALUES
('Bondi', '2026', 'NSW', -33.8915, 151.2767, 1500000.00, 'rising'),
('Surry Hills', '2010', 'NSW', -33.8886, 151.2094, 1200000.00, 'stable'),
('Paddington', '2021', 'NSW', -33.8848, 151.2299, 1800000.00, 'rising'),
('Newtown', '2042', 'NSW', -33.8978, 151.1794, 1100000.00, 'rising'),
('Manly', '2095', 'NSW', -33.7969, 151.2767, 1600000.00, 'stable'),
('Chatswood', '2067', 'NSW', -33.7969, 151.1816, 1400000.00, 'rising'),
('Parramatta', '2150', 'NSW', -33.8150, 151.0000, 900000.00, 'rising'),
('Cronulla', '2230', 'NSW', -34.0583, 151.1531, 1300000.00, 'stable');

-- Insert sample user
INSERT INTO users (email, password_hash, first_name, last_name, agency_name, license_number) VALUES
('agent@realestate.com', '$2b$12$example_hash', 'John', 'Smith', 'Premium Real Estate', 'RE123456');

-- =====================================================
-- USEFUL VIEWS
-- =====================================================

-- View for property listings with suburb information
CREATE VIEW property_listings AS
SELECT 
    p.id,
    p.full_address,
    p.property_type,
    p.bedrooms,
    p.bathrooms,
    p.car_spaces,
    p.listing_price,
    p.listing_status,
    s.name as suburb_name,
    s.postcode,
    s.median_price as suburb_median_price,
    u.first_name || ' ' || u.last_name as agent_name,
    u.agency_name
FROM properties p
JOIN suburbs s ON p.suburb_id = s.id
JOIN users u ON p.user_id = u.id
WHERE p.listing_status = 'active';

-- View for upcoming inspections
CREATE VIEW upcoming_inspections AS
SELECT 
    pi.id,
    pi.inspection_date,
    pi.start_time,
    pi.end_time,
    pi.status,
    pi.competing_inspections_count,
    pi.competition_level,
    p.full_address,
    p.property_type,
    p.bedrooms,
    p.bathrooms,
    s.name as suburb_name
FROM property_inspections pi
JOIN properties p ON pi.property_id = p.id
JOIN suburbs s ON p.suburb_id = s.id
WHERE pi.inspection_date >= CURRENT_DATE
AND pi.status = 'scheduled'
ORDER BY pi.inspection_date, pi.start_time;

-- View for competition analysis summary
CREATE VIEW competition_summary AS
SELECT 
    ar.analysis_date,
    s.name as suburb_name,
    COUNT(*) as total_analyses,
    AVG(ar.similar_properties_count) as avg_similar_properties,
    AVG(ar.filter_efficiency_percentage) as avg_filter_efficiency,
    AVG(ar.average_competition_level) as avg_competition_level
FROM analysis_results ar
JOIN properties p ON ar.property_id = p.id
JOIN suburbs s ON p.suburb_id = s.id
GROUP BY ar.analysis_date, s.name
ORDER BY ar.analysis_date DESC;

-- =====================================================
-- FUNCTIONS FOR BUSINESS LOGIC
-- =====================================================

-- Function to parse criteria strings into min/max values
CREATE OR REPLACE FUNCTION parse_criteria(criteria_str VARCHAR(20))
RETURNS TABLE(min_val INTEGER, max_val INTEGER) AS $$
BEGIN
    IF criteria_str LIKE '%+' THEN
        -- Handle cases like '2+', '3+'
        min_val := CAST(REPLACE(criteria_str, '+', '') AS INTEGER);
        max_val := NULL; -- Unlimited
    ELSIF criteria_str LIKE '%-%' THEN
        -- Handle cases like '3-4', '1-2'
        min_val := CAST(SPLIT_PART(criteria_str, '-', 1) AS INTEGER);
        max_val := CAST(SPLIT_PART(criteria_str, '-', 2) AS INTEGER);
    ELSE
        -- Handle exact values like '3', '2'
        min_val := CAST(criteria_str AS INTEGER);
        max_val := CAST(criteria_str AS INTEGER);
    END IF;
    
    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;

-- Function to find similar properties based on criteria
CREATE OR REPLACE FUNCTION find_similar_properties(
    target_property_id INTEGER,
    criteria_id INTEGER
)
RETURNS TABLE(
    property_id INTEGER,
    similarity_score DECIMAL(3, 2)
) AS $$
DECLARE
    criteria_rec RECORD;
    target_prop RECORD;
BEGIN
    -- Get the criteria and target property
    SELECT * INTO criteria_rec FROM similar_property_criteria WHERE id = criteria_id;
    SELECT * INTO target_prop FROM properties WHERE id = target_property_id;
    
    -- Find matching properties
    RETURN QUERY
    SELECT 
        p.id,
        -- Simple similarity score based on how well properties match criteria
        (
            CASE WHEN p.bedrooms BETWEEN criteria_rec.bedrooms_min AND COALESCE(criteria_rec.bedrooms_max, 999) THEN 1.0 ELSE 0.0 END +
            CASE WHEN p.bathrooms BETWEEN criteria_rec.bathrooms_min AND COALESCE(criteria_rec.bathrooms_max, 999) THEN 1.0 ELSE 0.0 END +
            CASE WHEN p.car_spaces BETWEEN criteria_rec.car_spaces_min AND COALESCE(criteria_rec.car_spaces_max, 999) THEN 1.0 ELSE 0.0 END
        ) / 3.0 as similarity_score
    FROM properties p
    JOIN suburbs s ON p.suburb_id = s.id
    WHERE p.id != target_property_id
    AND p.listing_status = 'active'
    AND p.bedrooms BETWEEN criteria_rec.bedrooms_min AND COALESCE(criteria_rec.bedrooms_max, 999)
    AND p.bathrooms BETWEEN criteria_rec.bathrooms_min AND COALESCE(criteria_rec.bathrooms_max, 999)
    AND p.car_spaces BETWEEN criteria_rec.car_spaces_min AND COALESCE(criteria_rec.car_spaces_max, 999)
    -- Add distance filter if coordinates are available
    AND (
        target_prop.suburb_id = p.suburb_id OR
        ST_DWithin(
            ST_Point(s.longitude, s.latitude)::geography,
            ST_Point(
                (SELECT longitude FROM suburbs WHERE id = target_prop.suburb_id),
                (SELECT latitude FROM suburbs WHERE id = target_prop.suburb_id)
            )::geography,
            criteria_rec.radius_km * 1000
        )
    )
    ORDER BY similarity_score DESC;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Composite indexes for common queries
CREATE INDEX idx_properties_search ON properties(property_type, bedrooms, bathrooms, car_spaces, listing_status);
CREATE INDEX idx_inspections_date_time ON property_inspections(inspection_date, start_time);
CREATE INDEX idx_analysis_user_date ON analysis_results(user_id, analysis_date);

-- =====================================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================================

COMMENT ON TABLE users IS 'Real estate agents and users of the system';
COMMENT ON TABLE suburbs IS 'Suburb/location master data with market information';
COMMENT ON TABLE properties IS 'Property listings with detailed information';
COMMENT ON TABLE property_inspections IS 'Scheduled and completed property inspections';
COMMENT ON TABLE similar_property_criteria IS 'User-defined criteria for finding similar properties';
COMMENT ON TABLE analysis_results IS 'Results from competition analysis runs';

COMMENT ON COLUMN similar_property_criteria.bedrooms_criteria IS 'User input like "3", "3-4", "3+"';
COMMENT ON COLUMN similar_property_criteria.bedrooms_min IS 'Parsed minimum value for querying';
COMMENT ON COLUMN similar_property_criteria.bedrooms_max IS 'Parsed maximum value, NULL for unlimited';
COMMENT ON COLUMN analysis_results.time_slot_analysis IS 'JSON array of time slots with competition data';
COMMENT ON COLUMN analysis_results.recommendations IS 'JSON array of recommended time slots';

-- =====================================================
-- GRANTS (Adjust based on your user setup)
-- =====================================================

-- Example grants for application user
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO app_user;