# 🏠 Real Estate Open Home Optimizer

A comprehensive full-stack web application designed to help real estate agents optimize their open home schedules by analyzing inspection times from Domain.com.au and providing intelligent scheduling recommendations.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Frontend Components](#frontend-components)
- [Configuration](#configuration)
- [Development](#development)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

The Real Estate Open Home Optimizer is a sophisticated tool that automates the process of finding optimal times for property inspections. By scraping real-time data from Domain.com.au, the application analyzes inspection schedules in specific areas and provides intelligent recommendations to maximize attendance and minimize conflicts.

### Key Benefits

- **Time Optimization**: Find the best time slots with minimal competition
- **Data-Driven Decisions**: Make informed scheduling choices based on real market data
- **Automated Scraping**: Real-time data collection from Domain.com.au
- **Visual Analytics**: Interactive charts and timeline visualizations
- **Export Capabilities**: CSV export for further analysis
- **Mobile Responsive**: Works seamlessly on desktop and mobile devices

## ✨ Features

### Core Functionality

- **🔍 Intelligent Property Search**: Search by address with automatic suburb/postcode extraction
- **📅 Date-Based Analysis**: Analyze inspection times for specific dates
- **⏰ Time Conflict Detection**: Identify optimal time slots with minimal competition
- **📊 Visual Timeline**: Interactive timeline showing all inspections in the area
- **📈 Analytics Dashboard**: Comprehensive charts and statistics
- **📱 Responsive Design**: Mobile-first design with touch-friendly interface
- **💾 Data Export**: Export results to CSV for further analysis
- **🎨 Modern UI**: Beautiful, animated interface with dark/light themes

### Advanced Features

- **🤖 Mock Data Generation**: Fallback data when scraping is unavailable
- **📸 Debug Screenshots**: Automatic screenshot capture for troubleshooting
- **🔄 Real-time Updates**: Live data fetching and updates
- **⚡ Performance Optimization**: Efficient data loading and caching
- **🛡️ Error Handling**: Robust error handling and user feedback
- **🎯 Smart Recommendations**: AI-powered scheduling suggestions

## 🏗️ Architecture

The application follows a modern full-stack architecture:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │◄──►│  Flask Backend  │◄──►│  Domain.com.au  │
│                 │    │                 │    │                 │
│ • User Interface│    │ • API Endpoints │    │ • Data Source   │
│ • State Mgmt    │    │ • Web Scraping  │    │ • Inspection    │
│ • Visualizations│    │ • Data Process  │    │   Times         │
│ • Responsive UI │    │ • CSV Export    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Data Flow

1. **User Input**: User enters property address and date
2. **API Request**: Frontend sends request to Flask backend
3. **Data Scraping**: Backend scrapes Domain.com.au using Playwright
4. **Data Processing**: Raw data is cleaned and structured
5. **Response**: Processed data sent back to frontend
6. **Visualization**: Frontend displays interactive charts and timeline
7. **Export**: Optional CSV export to user's desktop

## 🛠️ Technology Stack

### Frontend
- **React 19.1.0**: Modern React with hooks and functional components
- **Lucide React**: Beautiful, customizable icons
- **Tailwind CSS**: Utility-first CSS framework
- **CSS Animations**: Custom animations and transitions
- **Responsive Design**: Mobile-first approach

### Backend
- **Flask 3.0.0**: Lightweight Python web framework
- **Flask-CORS**: Cross-origin resource sharing
- **Playwright**: Modern web scraping and browser automation
- **Selenium**: Alternative web scraping (fallback)
- **Python-dotenv**: Environment variable management

### Development Tools
- **Node.js**: JavaScript runtime for frontend
- **npm**: Package manager for frontend dependencies
- **pip**: Python package manager
- **Virtual Environment**: Isolated Python environment

### Browser Support
- **Firefox**: Primary browser for web scraping
- **Chrome/Safari/Edge**: Frontend compatibility

## 🚀 Installation

### Prerequisites

- **Python 3.8+**: Required for backend
- **Node.js 14+**: Required for frontend
- **Firefox Browser**: Required for web scraping
- **Git**: For cloning the repository

### Quick Start

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd real-estate-optimizer
   ```

2. **Set Up Python Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright Browsers**
   ```bash
   playwright install firefox
   ```

5. **Install Frontend Dependencies**
   ```bash
   cd my-real-estate-app
   npm install
   cd ..
   ```

6. **Start the Application**
   ```bash
   chmod +x start_app.sh
   ./start_app.sh
   ```

### Manual Installation

If you prefer to start services separately:

#### Backend Setup
```bash
# Terminal 1 - Backend
source .venv/bin/activate
pip install flask flask-cors selenium playwright requests python-dotenv
playwright install firefox
python integrated_api.py
```

#### Frontend Setup
```bash
# Terminal 2 - Frontend
cd my-real-estate-app
npm install
npm start
```

## 📖 Usage

### Getting Started

1. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5001

2. **Login (Demo Mode)**
   - Use any email and password to access the demo
   - No actual authentication required

3. **Search for Properties**
   - Enter a property address (e.g., "123 Main St, Suburb NSW 2000")
   - Select a date for analysis
   - Click "Find Optimal Times"

4. **Analyze Results**
   - View the interactive timeline
   - Check analytics and recommendations
   - Export data to CSV if needed

### User Interface Guide

#### Login Screen
- **Modern Design**: Animated background with floating particles
- **Demo Access**: Use any credentials to enter demo mode
- **Responsive**: Works on all device sizes

#### Dashboard
- **Property Search**: Enter address and date
- **Filters**: Adjust search radius and time preferences
- **Results Display**: Timeline and analytics views
- **Export Options**: Download CSV reports

#### Timeline View
- **Interactive Timeline**: Drag and zoom functionality
- **Color Coding**: Different colors for different time slots
- **Hover Details**: Additional information on hover
- **Mobile Optimized**: Touch-friendly controls

## 🔌 API Documentation

### Base URL
```
http://localhost:5001/api
```

### Endpoints

#### Health Check
```http
GET /api/health
```
**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0"
}
```

#### Get Inspections
```http
GET /api/inspections?address={address}&date={date}
```

**Parameters:**
- `address` (string, required): Full property address
- `date` (string, required): Date in YYYY-MM-DD format

**Example Request:**
```http
GET /api/inspections?address=123%20Main%20St,%20Suburb%20NSW%202000&date=2024-01-15
```

**Response:**
```json
[
  {
    "address": "123 Main Street, Suburb NSW 2000",
    "date": "2024-01-15",
    "start_time": "10:00am",
    "end_time": "10:30am"
  },
  {
    "address": "456 Oak Avenue, Suburb NSW 2000", 
    "date": "2024-01-15",
    "start_time": "11:00am",
    "end_time": "11:30am"
  }
]
```

#### Mock Data (Development)
```http
GET /api/mock-data?date={date}
```

**Parameters:**
- `date` (string, required): Date in YYYY-MM-DD format

**Response:** Same format as inspections endpoint

#### Analytics
```http
GET /api/analytics?address={address}&date={date}
```

**Response:**
```json
{
  "total_inspections": 15,
  "peak_hours": ["10:00am", "2:00pm"],
  "recommended_times": ["9:00am", "4:00pm"],
  "competition_level": "medium",
  "success_probability": 0.75
}
```

### Error Responses

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**Common Error Codes:**
- `400`: Bad Request - Missing or invalid parameters
- `404`: Not Found - Resource not found
- `500`: Internal Server Error - Server-side error
- `503`: Service Unavailable - Scraping service unavailable

## 🧩 Frontend Components

### Component Architecture

```
App.js (Main Component)
├── LoginView
│   ├── Animated Background
│   ├── Login Form
│   └── Demo Instructions
├── DashboardView
│   ├── Navigation Header
│   ├── Property Search Form
│   ├── Filters Panel
│   ├── Results Timeline
│   ├── Analytics Charts
│   └── Export Controls
└── Shared Components
    ├── Loading Spinners
    ├── Error Messages
    ├── Success Notifications
    └── Mobile Menu
```

### Key Components

#### LoginView
- **Purpose**: User authentication (demo mode)
- **Features**: Animated background, form validation, responsive design
- **Props**: `handleLogin` function

#### DashboardView
- **Purpose**: Main application interface
- **Features**: Property search, data visualization, export functionality
- **Props**: State management props for search and results

#### Timeline Component
- **Purpose**: Visual representation of inspection times
- **Features**: Interactive timeline, zoom/pan, color coding
- **Data**: Array of inspection objects

#### Analytics Component
- **Purpose**: Statistical analysis and recommendations
- **Features**: Charts, metrics, recommendations
- **Data**: Processed analytics data

### State Management

The application uses React hooks for state management:

```javascript
// Main application state
const [isLoggedIn, setIsLoggedIn] = useState(false);
const [addressValue, setAddressValue] = useState('');
const [propertyData, setPropertyData] = useState([]);
const [loading, setLoading] = useState(false);
const [searchRadius, setSearchRadius] = useState(2);
const [timeFilter, setTimeFilter] = useState('all');
```

### Styling

- **Tailwind CSS**: Utility-first CSS framework
- **Custom CSS**: Additional animations and effects
- **Responsive Design**: Mobile-first approach
- **Dark/Light Themes**: Automatic theme switching
- **Animations**: Smooth transitions and micro-interactions

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# API Configuration
API_PORT=5001
API_HOST=0.0.0.0
FLASK_ENV=development
FLASK_DEBUG=True

# Frontend Configuration
REACT_APP_API_URL=http://localhost:5001

# Scraping Configuration
SCRAPING_TIMEOUT=60000
HEADLESS_MODE=True
SCREENSHOT_DEBUG=True

# CSV Export Configuration
EXPORT_TO_DESKTOP=True
AUTO_OPEN_CSV=True
```

### Configuration Options

#### Backend Configuration
- **Port**: Default 5001, configurable via `API_PORT`
- **Debug Mode**: Enabled by default for development
- **CORS**: Enabled for frontend communication
- **Timeout**: 60 seconds for scraping operations

#### Frontend Configuration
- **API URL**: Points to backend server
- **Development Server**: Runs on port 3000
- **Build Output**: Optimized production build

#### Scraping Configuration
- **Browser**: Firefox (headless mode)
- **Timeout**: 60 seconds per page
- **Screenshots**: Enabled for debugging
- **User Agent**: Standard Firefox user agent

## 🔧 Development

### Development Workflow

1. **Start Development Servers**
   ```bash
   ./start_app.sh
   ```

2. **Make Changes**
   - Frontend: Edit files in `my-real-estate-app/src/`
   - Backend: Edit `integrated_api.py` or `scraper_api.py`

3. **Test Changes**
   - Frontend: Hot reload automatically updates
   - Backend: Restart server to see changes

4. **Debug Issues**
   - Check browser console for frontend errors
   - Check terminal output for backend errors
   - Review screenshot files for scraping issues

### Code Structure

#### Backend (`integrated_api.py`)
```python
# Main Flask application
app = Flask(__name__)
CORS(app)

# Core functions
def extract_suburb_postcode(address)  # Address parsing
def scrape_inspections(suburb, postcode, date)  # Web scraping
def generate_mock_data(date)  # Fallback data
def save_to_csv(data, suburb, date)  # Data export

# API endpoints
@app.route('/api/health')  # Health check
@app.route('/api/inspections')  # Main data endpoint
@app.route('/api/mock-data')  # Mock data endpoint
```

#### Frontend (`my-real-estate-app/src/App.js`)
```javascript
// Main component with state management
const RealEstateScheduler = () => {
  // State hooks
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  // ... other state variables
  
  // Event handlers
  const handleLogin = () => { /* ... */ };
  const handlePropertySubmit = () => { /* ... */ };
  
  // Render logic
  return isLoggedIn ? <DashboardView /> : <LoginView />;
};
```

### Testing

#### Manual Testing
1. **Frontend Testing**
   - Test responsive design on different screen sizes
   - Verify all interactive elements work
   - Check animations and transitions

2. **Backend Testing**
   - Test API endpoints with different parameters
   - Verify error handling
   - Check CSV export functionality

3. **Integration Testing**
   - Test complete user workflows
   - Verify data flow from frontend to backend
   - Test error scenarios

#### Automated Testing
```bash
# Frontend tests
cd my-real-estate-app
npm test

# Backend tests (if implemented)
python -m pytest tests/
```

### Common Development Tasks

#### Adding New Features
1. **Backend**: Add new endpoints in `integrated_api.py`
2. **Frontend**: Add new components in `src/` directory
3. **Styling**: Update CSS classes and animations
4. **Testing**: Test new functionality thoroughly

#### Debugging Scraping Issues
1. **Enable Screenshots**: Set `SCREENSHOT_DEBUG=True`
2. **Check Output**: Review generated screenshot files
3. **Adjust Selectors**: Update CSS selectors if needed
4. **Test Manually**: Use browser developer tools

#### Performance Optimization
1. **Frontend**: Optimize React rendering and state updates
2. **Backend**: Implement caching for repeated requests
3. **Scraping**: Optimize wait times and selectors
4. **Network**: Minimize API calls and data transfer

## 🚀 Deployment

### Production Deployment

#### Prerequisites
- **Server**: Linux/Windows server with Python and Node.js
- **Domain**: Optional custom domain
- **SSL**: HTTPS certificate for production
- **Database**: Optional database for persistent storage

#### Deployment Steps

1. **Prepare Production Environment**
   ```bash
   # Clone repository
   git clone <repository-url>
   cd real-estate-optimizer
   
   # Set up Python environment
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   playwright install firefox
   ```

2. **Build Frontend**
   ```bash
   cd my-real-estate-app
   npm install
   npm run build
   cd ..
   ```

3. **Configure Production Settings**
   ```env
   # .env.production
   FLASK_ENV=production
   FLASK_DEBUG=False
   API_HOST=0.0.0.0
   API_PORT=5001
   REACT_APP_API_URL=https://yourdomain.com
   ```

4. **Start Production Services**
   ```bash
   # Use process manager like PM2 or systemd
   pm2 start integrated_api.py --name real-estate-api
   pm2 start "serve -s my-real-estate-app/build" --name real-estate-frontend
   ```

#### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install firefox

COPY . .
EXPOSE 5001

CMD ["python", "integrated_api.py"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "5001:5001"
    environment:
      - FLASK_ENV=production
  
  frontend:
    image: node:16-alpine
    working_dir: /app
    volumes:
      - ./my-real-estate-app:/app
    ports:
      - "3000:3000"
    command: npm start
```

#### Cloud Deployment

**AWS Deployment:**
- **EC2**: Deploy on virtual machines
- **Elastic Beanstalk**: Managed deployment
- **Lambda**: Serverless functions
- **S3**: Static file hosting

**Heroku Deployment:**
```bash
# Install Heroku CLI
heroku create real-estate-optimizer
heroku buildpacks:add heroku/python
heroku buildpacks:add heroku/nodejs
git push heroku main
```

### Security Considerations

1. **Environment Variables**: Never commit sensitive data
2. **HTTPS**: Use SSL certificates in production
3. **Rate Limiting**: Implement API rate limiting
4. **Input Validation**: Validate all user inputs
5. **Error Handling**: Don't expose internal errors

## 🐛 Troubleshooting

### Common Issues

#### Installation Issues

**Problem**: Python virtual environment not activating
```bash
# Solution
python -m venv .venv311
source .venv311/bin/activate  # Linux/Mac
.venv311\Scripts\activate     # Windows
```

**Problem**: Playwright browser installation fails
```bash
# Solution
playwright install firefox --force
# Or install system-wide
sudo apt-get install firefox  # Linux
```

**Problem**: Node.js dependencies fail to install
```bash
# Solution
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

#### Runtime Issues

**Problem**: Backend server won't start
- **Check**: Port 5001 is not in use
- **Check**: Virtual environment is activated
- **Check**: All dependencies are installed
- **Solution**: `lsof -i :5001` and kill conflicting processes

**Problem**: Frontend can't connect to backend
- **Check**: Backend server is running on port 5001
- **Check**: CORS is enabled in Flask app
- **Check**: API URL is correct in frontend
- **Solution**: Verify `REACT_APP_API_URL` in `.env`

**Problem**: Scraping returns no data
- **Check**: Internet connection is working
- **Check**: Domain.com.au is accessible
- **Check**: CSS selectors are still valid
- **Solution**: Enable screenshots and debug visually

#### Performance Issues

**Problem**: Slow scraping performance
- **Solution**: Reduce timeout values
- **Solution**: Optimize CSS selectors
- **Solution**: Use headless mode

**Problem**: Frontend is slow to load
- **Solution**: Optimize React components
- **Solution**: Implement lazy loading
- **Solution**: Minimize bundle size

### Debug Tools

#### Backend Debugging
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Add debug prints
print(f"Debug: {variable_name}")

# Use Python debugger
import pdb; pdb.set_trace()
```

#### Frontend Debugging
```javascript
// Browser console
console.log('Debug:', variable);
console.error('Error:', error);

// React Developer Tools
// Install browser extension for component inspection
```

#### Network Debugging
```bash
# Check API endpoints
curl http://localhost:5001/api/health

# Monitor network traffic
# Use browser developer tools Network tab
```

### Log Files

- **Backend Logs**: Terminal output or log files
- **Frontend Logs**: Browser console
- **Scraping Logs**: Screenshot files and terminal output
- **System Logs**: Check system logs for resource issues

## 🤝 Contributing

### Development Guidelines

1. **Code Style**
   - **Python**: Follow PEP 8 style guide
   - **JavaScript**: Use ES6+ features and consistent formatting
   - **CSS**: Use Tailwind utility classes when possible

2. **Commit Messages**
   - Use descriptive commit messages
   - Follow conventional commit format
   - Include issue numbers when applicable

3. **Pull Requests**
   - Create feature branches for new development
   - Include tests for new functionality
   - Update documentation as needed

### Getting Started with Contributing

1. **Fork the Repository**
   ```bash
   git fork <repository-url>
   git clone <your-fork-url>
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-feature-name
   ```

3. **Make Changes**
   - Follow coding standards
   - Add tests if applicable
   - Update documentation

4. **Submit Pull Request**
   - Push changes to your fork
   - Create pull request with description
   - Wait for review and feedback

### Areas for Contribution

- **New Features**: Additional analytics, export formats, integrations
- **Bug Fixes**: Resolve issues and improve stability
- **Documentation**: Improve guides and API documentation
- **Testing**: Add automated tests and improve coverage
- **Performance**: Optimize scraping and frontend performance
- **UI/UX**: Enhance user interface and experience

## 📄 License

This project is licensed under the ISC License. See the LICENSE file for details.

## 📞 Support

For support and questions:

- **Issues**: Create GitHub issues for bugs and feature requests
- **Documentation**: Check this README and inline code comments
- **Community**: Join discussions in GitHub Discussions

## 🙏 Acknowledgments

- **Domain.com.au**: Data source for property inspections
- **React Team**: Amazing frontend framework
- **Flask Team**: Lightweight and powerful backend framework
- **Playwright Team**: Modern web scraping capabilities
- **Tailwind CSS**: Beautiful utility-first CSS framework
- **Lucide Icons**: Beautiful icon library

---

**Built with ❤️ for real estate professionals**