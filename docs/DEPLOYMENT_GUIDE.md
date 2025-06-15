# 🏠 Real Estate Open Home Optimizer - Deployment Guide

## 🚀 Quick Start

### Option 1: One-Command Startup
```bash
./start_app.sh
```

### Option 2: Manual Startup

#### Backend (Terminal 1):
```bash
./start_backend.sh
```

#### Frontend (Terminal 2):
```bash
./start_frontend.sh
```

## 📍 Application URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5001
- **Health Check**: http://localhost:5001/api/health
- **Mock Data**: http://localhost:5001/api/mock-data

## 🔧 System Requirements

- **Python**: 3.8+ (Currently using 3.13.1)
- **Node.js**: 16+ (Currently using 24.1.0)
- **npm**: 8+ (Currently using 11.3.0)
- **Operating System**: macOS, Linux, or Windows

## 📦 Dependencies

### Python Dependencies
- Flask 3.0.0
- Flask-CORS 4.0.0
- Selenium 4.15.2
- Playwright 1.40.0
- Requests 2.31.0
- Python-dotenv 1.0.0

### Node.js Dependencies
- React 19.1.0
- Lucide React 0.513.0
- React Scripts 5.0.1
- Testing Libraries

## 🛠️ Manual Installation

### 1. Python Environment Setup
```bash
# Activate virtual environment
source .venv/bin/activate

# Install Python dependencies
pip install flask flask-cors selenium playwright requests python-dotenv

# Install Playwright browsers
playwright install firefox
```

### 2. Node.js Environment Setup
```bash
# Navigate to React app
cd my-real-estate-app

# Install Node.js dependencies
npm install
```

### 3. Start Services
```bash
# Terminal 1: Start Backend
python integrated_api.py

# Terminal 2: Start Frontend
cd my-real-estate-app && npm start
```

## 🔍 API Endpoints

### GET /api/health
Health check endpoint
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "version": "1.0.0"
}
```

### GET /api/inspections
Get real inspection data
```
Parameters:
- address: Property address (required)
- date: Date in YYYY-MM-DD format (required)
- start_time: Start time filter (optional, default: 09:00)
- end_time: End time filter (optional, default: 16:00)
```

### GET /api/mock-data
Get mock data for testing
```
Parameters:
- date: Date in YYYY-MM-DD format (optional)
- start_time: Start time filter (optional)
- end_time: End time filter (optional)
```

## 🧪 Testing

### Test Backend API
```bash
# Health check
curl http://localhost:5001/api/health

# Mock data
curl "http://localhost:5001/api/mock-data?date=2024-01-01"

# Real data (requires valid address)
curl "http://localhost:5001/api/inspections?address=123%20Main%20St,%20Sydney,%202000&date=2024-01-01"
```

### Test Frontend
1. Open http://localhost:3000
2. Use any email/password to login (demo mode)
3. Enter a property address
4. Click "Find Optimal Times"

## 🐛 Troubleshooting

### Common Issues

#### Backend won't start
```bash
# Check Python version
python3 --version

# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### Frontend won't start
```bash
# Check Node.js version
node --version

# Clear npm cache
npm cache clean --force

# Reinstall dependencies
cd my-real-estate-app
rm -rf node_modules package-lock.json
npm install
```

#### CORS Issues
- Ensure Flask-CORS is installed
- Check that API is running on port 5001
- Verify frontend is calling correct API URL

#### Scraping Issues
- Check internet connection
- Verify Playwright browsers are installed
- Check Domain.com.au website structure hasn't changed

### Port Conflicts
If ports 3000 or 5001 are in use:

```bash
# Find processes using ports
lsof -i :3000
lsof -i :5001

# Kill processes if needed
kill -9 <PID>
```

## 📊 Data Flow

1. **User Input**: Address and preferences entered in React frontend
2. **API Call**: Frontend sends GET request to `/api/inspections`
3. **Web Scraping**: Backend scrapes Domain.com.au for competing open homes
4. **Data Processing**: Backend analyzes competition levels
5. **Response**: Structured data returned to frontend
6. **Visualization**: Interactive timeline and recommendations displayed

## 🔒 Security Notes

- This is a development setup - not production ready
- API has no authentication (demo purposes)
- CORS is enabled for all origins
- Sensitive data should be moved to environment variables

## 🚀 Production Deployment

For production deployment, consider:

1. **Environment Variables**: Move all config to .env files
2. **Authentication**: Add proper user authentication
3. **Rate Limiting**: Implement API rate limiting
4. **Error Handling**: Enhanced error handling and logging
5. **Database**: Add persistent data storage
6. **Caching**: Implement caching for scraping results
7. **Monitoring**: Add application monitoring
8. **SSL/HTTPS**: Enable secure connections
9. **Docker**: Containerize the application
10. **Cloud Hosting**: Deploy to AWS, GCP, or Azure

## 📝 Development Notes

- Frontend uses mock data as fallback if API fails
- Backend saves CSV files to Desktop automatically
- Screenshots are saved for debugging scraping issues
- Application supports real-time data from Domain.com.au
- Responsive design works on mobile and desktop