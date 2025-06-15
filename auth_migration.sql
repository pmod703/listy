-- =====================================================
-- Authentication Tables Migration
-- Add authentication-specific tables and update users table
-- =====================================================

-- Update existing users table with authentication fields
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_failed_login TIMESTAMP;
ALTER TABLE users ADD COLUMN IF NOT EXISTS account_locked_until TIMESTAMP;
ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_image_url VARCHAR(500);
ALTER TABLE users ADD COLUMN IF NOT EXISTS bio TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS website VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verification_token VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_reset_token VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_reset_expires TIMESTAMP;

-- Create user_sessions table
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    refresh_token VARCHAR(255) UNIQUE,
    ip_address VARCHAR(45), -- IPv6 compatible
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraint
    CONSTRAINT fk_sessions_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_refresh_token ON user_sessions(refresh_token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_active ON user_sessions(is_active);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires ON user_sessions(expires_at);

-- Create indexes for authentication fields on users table
CREATE INDEX IF NOT EXISTS idx_users_email_verification ON users(email_verification_token);
CREATE INDEX IF NOT EXISTS idx_users_password_reset ON users(password_reset_token);
CREATE INDEX IF NOT EXISTS idx_users_account_locked ON users(account_locked_until);
CREATE INDEX IF NOT EXISTS idx_users_is_verified ON users(is_verified);

-- Create audit log table for security tracking
CREATE TABLE IF NOT EXISTS auth_audit_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    action VARCHAR(50) NOT NULL, -- 'login', 'logout', 'register', 'password_change', etc.
    ip_address VARCHAR(45),
    user_agent TEXT,
    success BOOLEAN NOT NULL,
    failure_reason VARCHAR(255),
    additional_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraint (nullable for failed login attempts on non-existent users)
    CONSTRAINT fk_audit_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Create indexes for audit log
CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON auth_audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_action ON auth_audit_log(action);
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON auth_audit_log(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_log_success ON auth_audit_log(success);
CREATE INDEX IF NOT EXISTS idx_audit_log_ip ON auth_audit_log(ip_address);

-- Create function to clean up expired sessions
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM user_sessions 
    WHERE expires_at < NOW() OR (is_active = FALSE AND created_at < NOW() - INTERVAL '30 days');
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    INSERT INTO auth_audit_log (action, success, additional_data, created_at)
    VALUES ('session_cleanup', TRUE, jsonb_build_object('deleted_sessions', deleted_count), NOW());
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Create function to log authentication events
CREATE OR REPLACE FUNCTION log_auth_event(
    p_user_id INTEGER,
    p_action VARCHAR(50),
    p_ip_address VARCHAR(45),
    p_user_agent TEXT,
    p_success BOOLEAN,
    p_failure_reason VARCHAR(255) DEFAULT NULL,
    p_additional_data JSONB DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO auth_audit_log (
        user_id, action, ip_address, user_agent, success, failure_reason, additional_data, created_at
    ) VALUES (
        p_user_id, p_action, p_ip_address, p_user_agent, p_success, p_failure_reason, p_additional_data, NOW()
    );
END;
$$ LANGUAGE plpgsql;

-- Create view for active user sessions
CREATE OR REPLACE VIEW active_user_sessions AS
SELECT 
    s.id,
    s.user_id,
    u.email,
    u.first_name,
    u.last_name,
    s.ip_address,
    s.created_at,
    s.last_activity,
    s.expires_at,
    EXTRACT(EPOCH FROM (s.expires_at - NOW())) / 3600 AS hours_until_expiry
FROM user_sessions s
JOIN users u ON s.user_id = u.id
WHERE s.is_active = TRUE 
  AND s.expires_at > NOW()
ORDER BY s.last_activity DESC;

-- Create view for authentication statistics
CREATE OR REPLACE VIEW auth_statistics AS
SELECT 
    DATE(created_at) as date,
    action,
    COUNT(*) as total_events,
    COUNT(*) FILTER (WHERE success = TRUE) as successful_events,
    COUNT(*) FILTER (WHERE success = FALSE) as failed_events,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(DISTINCT ip_address) as unique_ips
FROM auth_audit_log
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at), action
ORDER BY date DESC, action;

-- Create view for user security summary
CREATE OR REPLACE VIEW user_security_summary AS
SELECT 
    u.id,
    u.email,
    u.first_name,
    u.last_name,
    u.is_active,
    u.is_verified,
    u.email_verified,
    u.failed_login_attempts,
    u.last_failed_login,
    u.account_locked_until,
    u.last_login,
    u.created_at,
    COUNT(s.id) as active_sessions,
    MAX(s.last_activity) as last_session_activity,
    COUNT(al.id) FILTER (WHERE al.action = 'login' AND al.success = TRUE AND al.created_at >= NOW() - INTERVAL '30 days') as successful_logins_30d,
    COUNT(al.id) FILTER (WHERE al.action = 'login' AND al.success = FALSE AND al.created_at >= NOW() - INTERVAL '30 days') as failed_logins_30d
FROM users u
LEFT JOIN user_sessions s ON u.id = s.user_id AND s.is_active = TRUE AND s.expires_at > NOW()
LEFT JOIN auth_audit_log al ON u.id = al.user_id
GROUP BY u.id, u.email, u.first_name, u.last_name, u.is_active, u.is_verified, u.email_verified, 
         u.failed_login_attempts, u.last_failed_login, u.account_locked_until, u.last_login, u.created_at;

-- Insert sample admin user (password: AdminPass123!)
-- Note: In production, create admin users through the application
INSERT INTO users (
    email, 
    password_hash, 
    first_name, 
    last_name, 
    agency_name, 
    is_active, 
    is_verified, 
    email_verified
) VALUES (
    'admin@realestate.com',
    '$2b$12$LQv3c1yqBwlVHpPn7ToFNu.2E/.AqNF.jjO4.Iu1AXaQZKvFw/kem', -- AdminPass123!
    'Admin',
    'User',
    'System Administration',
    TRUE,
    TRUE,
    TRUE
) ON CONFLICT (email) DO NOTHING;

-- Create trigger to automatically log authentication events
CREATE OR REPLACE FUNCTION trigger_log_user_changes()
RETURNS TRIGGER AS $$
BEGIN
    -- Log when user login timestamp changes (successful login)
    IF TG_OP = 'UPDATE' AND OLD.last_login IS DISTINCT FROM NEW.last_login AND NEW.last_login IS NOT NULL THEN
        PERFORM log_auth_event(
            NEW.id,
            'login',
            NULL, -- IP will be logged separately by application
            NULL, -- User agent will be logged separately by application
            TRUE,
            NULL,
            jsonb_build_object('login_time', NEW.last_login)
        );
    END IF;
    
    -- Log when failed login attempts increase
    IF TG_OP = 'UPDATE' AND OLD.failed_login_attempts < NEW.failed_login_attempts THEN
        PERFORM log_auth_event(
            NEW.id,
            'failed_login',
            NULL,
            NULL,
            FALSE,
            'Invalid credentials',
            jsonb_build_object('attempt_count', NEW.failed_login_attempts)
        );
    END IF;
    
    -- Log when account gets locked
    IF TG_OP = 'UPDATE' AND OLD.account_locked_until IS NULL AND NEW.account_locked_until IS NOT NULL THEN
        PERFORM log_auth_event(
            NEW.id,
            'account_locked',
            NULL,
            NULL,
            TRUE,
            'Too many failed login attempts',
            jsonb_build_object('locked_until', NEW.account_locked_until)
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create the trigger
DROP TRIGGER IF EXISTS trigger_user_auth_events ON users;
CREATE TRIGGER trigger_user_auth_events
    AFTER UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION trigger_log_user_changes();

-- Create scheduled job function (requires pg_cron extension in production)
-- This is a placeholder - in production you'd set up a cron job or scheduled task
CREATE OR REPLACE FUNCTION schedule_maintenance()
RETURNS TEXT AS $$
BEGIN
    -- Clean up expired sessions daily
    PERFORM cleanup_expired_sessions();
    
    -- Clean up old audit logs (keep 90 days)
    DELETE FROM auth_audit_log WHERE created_at < NOW() - INTERVAL '90 days';
    
    -- Reset failed login attempts for unlocked accounts older than 24 hours
    UPDATE users 
    SET failed_login_attempts = 0, last_failed_login = NULL
    WHERE failed_login_attempts > 0 
      AND (account_locked_until IS NULL OR account_locked_until < NOW())
      AND (last_failed_login IS NULL OR last_failed_login < NOW() - INTERVAL '24 hours');
    
    RETURN 'Maintenance completed at ' || NOW()::TEXT;
END;
$$ LANGUAGE plpgsql;

-- Add comments for documentation
COMMENT ON TABLE user_sessions IS 'Active user sessions with JWT tokens';
COMMENT ON TABLE auth_audit_log IS 'Security audit log for authentication events';
COMMENT ON COLUMN users.failed_login_attempts IS 'Number of consecutive failed login attempts';
COMMENT ON COLUMN users.account_locked_until IS 'Account locked until this timestamp';
COMMENT ON COLUMN users.email_verification_token IS 'Token for email verification';
COMMENT ON COLUMN users.password_reset_token IS 'Token for password reset';
COMMENT ON COLUMN users.password_reset_expires IS 'Expiration time for password reset token';

-- Grant permissions (adjust based on your user setup)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON user_sessions TO app_user;
-- GRANT SELECT, INSERT ON auth_audit_log TO app_user;
-- GRANT EXECUTE ON FUNCTION cleanup_expired_sessions() TO app_user;
-- GRANT EXECUTE ON FUNCTION log_auth_event(INTEGER, VARCHAR, VARCHAR, TEXT, BOOLEAN, VARCHAR, JSONB) TO app_user;

COMMIT;