# 🏠 Real Estate Open Home Optimizer

A comprehensive full-stack web application designed to help real estate agents optimize their open home schedules by analyzing inspection times and providing intelligent scheduling recommendations.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![React](https://img.shields.io/badge/React-16.14.0-blue.svg)](https://reactjs.org/)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://python.org/)
[![Flask](https://img.shields.io/badge/Flask-Latest-red.svg)](https://flask.palletsprojects.com/)

## 🎯 Overview

The Real Estate Open Home Optimizer is a sophisticated tool that helps real estate professionals find optimal times for property inspections. The application provides data-driven insights to maximize attendance and minimize scheduling conflicts.

### ✨ Key Features

- **🔍 Intelligent Property Search** - Search by address with automatic location detection
- **📅 Date-Based Analysis** - Analyze inspection times for specific dates
- **⏰ Time Conflict Detection** - Identify optimal time slots with minimal competition
- **📊 Visual Analytics** - Interactive charts and timeline visualizations
- **👤 User Authentication** - Secure login and registration system
- **📱 Responsive Design** - Mobile-first design that works on all devices
- **💾 Data Export** - Export results to CSV for further analysis
- **🎨 Modern UI** - Beautiful interface with Tailwind CSS styling

## 🏗️ Project Structure

```
real-estate-app/
├── 📁 frontend/              # React frontend application
│   ├── src/                  # React source code
│   │   ├── components/       # Reusable React components
│   │   ├── contexts/         # React context providers
│   │   ├── hooks/            # Custom React hooks
│   │   ├── services/         # API and service layers
│   │   ├── styles/           # CSS and styling files
│   │   └── utils/            # Utility functions
│   ├── public/               # Public assets
│   └── package.json          # Frontend dependencies
│
├── 📁 backend/               # Python backend services
│   ├── api/                  # API endpoints and servers
│   ├── auth/                 # Authentication modules
│   ├── database/             # Database configuration and schemas
│   └── requirements.txt      # Python dependencies
│
├── 📁 scripts/               # Startup and utility scripts
├── 📁 docs/                  # Project documentation
├── 📁 tests/                 # Test files
└── 📄 README.md              # This file
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** (v14 or higher)
- **Python** (3.8 or higher)
- **npm** or **yarn**
- **Git**

### 🎯 One-Command Startup

```bash
# Clone the repository
git clone https://github.com/pmod703/listy.git
cd listy

# Start the entire application (frontend + backend)
./scripts/start_app.sh
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000

### 🔧 Manual Setup

#### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start backend server
python api/integrated_api.py
```

#### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[API Documentation](docs/API_DOCUMENTATION.md)** - Complete API reference
- **[Authentication Guide](docs/AUTHENTICATION_DOCUMENTATION.md)** - User authentication system
- **[Database Documentation](docs/DATABASE_DOCUMENTATION.md)** - Database schema and setup
- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - Production deployment instructions
- **[Project Structure](PROJECT_STRUCTURE.md)** - Detailed project organization

## 🛠️ Development

### Available Scripts

#### Root Level Scripts
- `./scripts/start_app.sh` - Start full application
- `./scripts/start_backend.sh` - Start backend only
- `./scripts/start_frontend.sh` - Start frontend only
- `./scripts/start_clean_backend.sh` - Start backend without scraping

#### Frontend Scripts
```bash
cd frontend
npm start          # Start development server
npm test           # Run tests
npm run build      # Build for production
```

#### Backend Scripts
```bash
cd backend
python api/integrated_api.py              # Full-featured API
python api/clean_api.py                   # Clean API without scraping
python api/clean_api_with_database.py     # Clean API with database
```

### 🧪 Testing

```bash
# Run backend tests
cd tests
python test_authentication.py
python test_clean_api.py
python test_complete_integration.py

# Run frontend tests
cd frontend
npm test
```

## 🏗️ Architecture

The application follows a modern full-stack architecture:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │◄──►│  Flask Backend  │◄──►│    Database     │
│                 │    │                 │    │                 │
│ • Authentication│    │ • API Endpoints │    │ • User Data     │
│ • Property Search│    │ • Data Processing│    │ • Property Info │
│ • Visualizations│    │ • Authentication│    │ • Search History│
│ • Responsive UI │    │ • Data Export   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Technology Stack

#### Frontend
- **React 16.14.0** - UI framework
- **Tailwind CSS** - Styling and design system
- **Lucide React** - Icon library
- **React Context** - State management
- **Custom Hooks** - Reusable logic

#### Backend
- **Python 3.8+** - Programming language
- **Flask** - Web framework
- **SQLite/PostgreSQL** - Database
- **JWT** - Authentication tokens
- **BeautifulSoup** - Web scraping (optional)

## 🌟 Features in Detail

### Authentication System
- Secure user registration and login
- JWT token-based authentication
- Protected routes and middleware
- Password hashing and validation

### Property Search
- Address-based property lookup
- Automatic location detection
- Date-specific inspection analysis
- Real-time data processing

### Analytics Dashboard
- Interactive timeline visualizations
- Conflict detection algorithms
- Statistical analysis
- Export capabilities

### Responsive Design
- Mobile-first approach
- Touch-friendly interface
- Cross-browser compatibility
- Accessibility features

## 🚀 Deployment

### Development
```bash
./scripts/start_app.sh
```

### Production
See [Deployment Guide](docs/DEPLOYMENT_GUIDE.md) for detailed production deployment instructions including:
- Environment configuration
- Database setup
- Security considerations
- Performance optimization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow existing code style and conventions
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [documentation](docs/) for detailed guides
2. Review existing [issues](https://github.com/pmod703/listy/issues)
3. Create a new issue with detailed information
4. Contact the development team

## 🙏 Acknowledgments

- Built with modern web technologies
- Inspired by real estate industry needs
- Community-driven development
- Open source contributions welcome

---

**Built with ❤️ for real estate professionals**

*Last updated: December 2024*