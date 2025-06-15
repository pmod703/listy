#!/usr/bin/env python3
"""
Database Migration Script for Real Estate Open Home Optimizer
Handles database setup, migrations, and data seeding
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, text
from database_models import Base, SessionLocal, init_sample_data
import argparse

# Database configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'realestate_optimizer')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server (not to specific database)
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database='postgres'  # Connect to default postgres database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        exists = cursor.fetchone()
        
        if not exists:
            print(f"📊 Creating database '{DB_NAME}'...")
            cursor.execute(f'CREATE DATABASE "{DB_NAME}"')
            print(f"✅ Database '{DB_NAME}' created successfully")
        else:
            print(f"📊 Database '{DB_NAME}' already exists")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def run_sql_file(sql_file_path):
    """Run SQL commands from a file"""
    try:
        engine = create_engine(DATABASE_URL)
        
        with open(sql_file_path, 'r') as file:
            sql_content = file.read()
        
        # Split by semicolon and execute each statement
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        with engine.connect() as conn:
            for statement in statements:
                if statement:
                    try:
                        conn.execute(text(statement))
                        conn.commit()
                    except Exception as e:
                        print(f"⚠️  Warning executing statement: {e}")
                        continue
        
        print(f"✅ SQL file '{sql_file_path}' executed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error running SQL file: {e}")
        return False

def create_tables():
    """Create all tables using SQLAlchemy"""
    try:
        engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def drop_tables():
    """Drop all tables"""
    try:
        engine = create_engine(DATABASE_URL)
        Base.metadata.drop_all(bind=engine)
        print("✅ All tables dropped successfully")
        return True
    except Exception as e:
        print(f"❌ Error dropping tables: {e}")
        return False

def seed_data():
    """Seed the database with initial data"""
    try:
        init_sample_data()
        print("✅ Sample data seeded successfully")
        return True
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        return False

def check_connection():
    """Test database connection"""
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Database connection successful")
            print(f"📊 PostgreSQL version: {version}")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def get_table_info():
    """Get information about existing tables"""
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            # Get table names
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            
            if tables:
                print("📊 Existing tables:")
                for table in tables:
                    # Get row count for each table
                    count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = count_result.fetchone()[0]
                    print(f"  - {table}: {count} rows")
            else:
                print("📊 No tables found in database")
            
            return tables
    except Exception as e:
        print(f"❌ Error getting table info: {e}")
        return []

def backup_database(backup_file):
    """Create a database backup"""
    try:
        import subprocess
        
        cmd = [
            'pg_dump',
            '-h', DB_HOST,
            '-p', DB_PORT,
            '-U', DB_USER,
            '-d', DB_NAME,
            '-f', backup_file,
            '--no-password'
        ]
        
        env = os.environ.copy()
        env['PGPASSWORD'] = DB_PASSWORD
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Database backup created: {backup_file}")
            return True
        else:
            print(f"❌ Backup failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return False

def restore_database(backup_file):
    """Restore database from backup"""
    try:
        import subprocess
        
        cmd = [
            'psql',
            '-h', DB_HOST,
            '-p', DB_PORT,
            '-U', DB_USER,
            '-d', DB_NAME,
            '-f', backup_file
        ]
        
        env = os.environ.copy()
        env['PGPASSWORD'] = DB_PASSWORD
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Database restored from: {backup_file}")
            return True
        else:
            print(f"❌ Restore failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error restoring database: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Real Estate Database Migration Tool')
    parser.add_argument('command', choices=[
        'init', 'create-db', 'create-tables', 'drop-tables', 
        'seed', 'check', 'info', 'backup', 'restore', 'reset'
    ], help='Command to execute')
    parser.add_argument('--file', help='File path for backup/restore operations')
    parser.add_argument('--sql', help='SQL file to execute')
    
    args = parser.parse_args()
    
    print("🏠 Real Estate Database Migration Tool")
    print("=" * 50)
    print(f"📊 Database: {DB_NAME}")
    print(f"🔗 Host: {DB_HOST}:{DB_PORT}")
    print(f"👤 User: {DB_USER}")
    print("=" * 50)
    
    if args.command == 'init':
        print("🚀 Initializing database...")
        if create_database() and create_tables() and seed_data():
            print("\n✅ Database initialization completed successfully!")
        else:
            print("\n❌ Database initialization failed!")
            sys.exit(1)
    
    elif args.command == 'create-db':
        create_database()
    
    elif args.command == 'create-tables':
        create_tables()
    
    elif args.command == 'drop-tables':
        confirm = input("⚠️  Are you sure you want to drop all tables? (yes/no): ")
        if confirm.lower() == 'yes':
            drop_tables()
        else:
            print("❌ Operation cancelled")
    
    elif args.command == 'seed':
        seed_data()
    
    elif args.command == 'check':
        check_connection()
    
    elif args.command == 'info':
        get_table_info()
    
    elif args.command == 'backup':
        if not args.file:
            args.file = f"backup_{DB_NAME}_{os.getenv('USER', 'user')}.sql"
        backup_database(args.file)
    
    elif args.command == 'restore':
        if not args.file:
            print("❌ Please specify backup file with --file option")
            sys.exit(1)
        restore_database(args.file)
    
    elif args.command == 'reset':
        confirm = input("⚠️  Are you sure you want to reset the entire database? (yes/no): ")
        if confirm.lower() == 'yes':
            print("🔄 Resetting database...")
            if drop_tables() and create_tables() and seed_data():
                print("\n✅ Database reset completed successfully!")
            else:
                print("\n❌ Database reset failed!")
                sys.exit(1)
        else:
            print("❌ Operation cancelled")
    
    if args.sql:
        print(f"📄 Executing SQL file: {args.sql}")
        run_sql_file(args.sql)

if __name__ == "__main__":
    main()