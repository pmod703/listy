# Real Estate App - Project Structure

This document outlines the organized project structure following industry best practices.

## Directory Structure

```
real-estate-app/
├── frontend/                   # React frontend application
│   ├── src/                   # React source code
│   ├── public/                # Public assets
│   ├── package.json           # Frontend dependencies
│   └── tailwind.config.js     # Tailwind CSS configuration
│
├── backend/                   # Python backend services
│   ├── api/                   # Main API endpoints
│   │   ├── integrated_api.py  # Full-featured API server
│   │   ├── clean_api.py       # Clean API without scraping
│   │   ├── clean_api_with_database.py
│   │   ├── scraper_api.py     # Web scraping functionality
│   │   └── simple_auth_backend.py
│   ├── auth/                  # Authentication modules
│   │   ├── auth_integration.py
│   │   ├── auth_middleware.py
│   │   ├── auth_models.py
│   │   ├── auth_routes.py
│   │   └── auth_service.py
│   ├── database/              # Database configuration and schemas
│   │   ├── database_config.py
│   │   ├── database_migration.py
│   │   ├── database_models.py
│   │   ├── auth_migration.sql
│   │   └── database_schemas.sql
│   ├── utils/                 # Utility functions (empty, ready for use)
│   └── requirements.txt       # Python dependencies
│
├── scripts/                   # Startup and utility scripts
│   ├── start_app.sh          # Start full stack application
│   ├── start_backend.sh      # Start backend only
│   ├── start_clean_backend.sh # Start clean backend (no scraping)
│   └── start_frontend.sh     # Start frontend only
│
├── docs/                     # Project documentation
│   ├── README.md            # Main project documentation
│   ├── API_DOCUMENTATION.md
│   ├── AUTHENTICATION_DOCUMENTATION.md
│   ├── DATABASE_DOCUMENTATION.md
│   └── [other documentation files]
│
├── tests/                    # Test files
│   ├── test_authentication.py
│   ├── test_clean_api.py
│   ├── test_complete_integration.py
│   └── [other test files]
│
├── debug/                    # Debug files and screenshots
│   ├── backend.log
│   ├── debug_*.png
│   └── [other debug files]
│
├── .venv/                    # Python virtual environment
├── .venv311/                 # Alternative Python virtual environment
├── node_modules/             # Node.js dependencies
├── package.json              # Root package.json
├── .env                      # Environment variables
├── .gitignore               # Git ignore rules
└── PROJECT_STRUCTURE.md     # This file
```

## Quick Start

### Start Full Application
```bash
./scripts/start_app.sh
```

### Start Individual Services
```bash
# Backend only
./scripts/start_backend.sh

# Frontend only  
./scripts/start_frontend.sh

# Clean backend (no scraping)
./scripts/start_clean_backend.sh
```

## Development Workflow

1. **Frontend Development**: Work in `frontend/` directory
2. **Backend Development**: Work in `backend/` directory
3. **Documentation**: Update files in `docs/` directory
4. **Testing**: Add tests to `tests/` directory
5. **Scripts**: Utility scripts in `scripts/` directory

## Benefits of This Structure

- **Separation of Concerns**: Frontend and backend are clearly separated
- **Scalability**: Easy to add new modules and services
- **Maintainability**: Related files are grouped together
- **Development Efficiency**: Clear structure makes navigation easier
- **CI/CD Ready**: Structure supports automated deployment pipelines