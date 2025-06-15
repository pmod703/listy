# 🔌 API Documentation

## Real Estate Open Home Optimizer API

This document provides comprehensive documentation for the Real Estate Open Home Optimizer API endpoints.

## Base URL

```
http://localhost:5001/api
```

## Authentication

Currently, the API operates in demo mode and does not require authentication. All endpoints are publicly accessible.

## Rate Limiting

- **Development**: No rate limiting applied
- **Production**: Recommended to implement rate limiting (e.g., 100 requests per minute per IP)

## Response Format

All API responses follow a consistent JSON format:

### Success Response
```json
{
  "data": [...],
  "status": "success",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Error Response
```json
{
  "error": "Error description",
  "code": "ERROR_CODE",
  "status": "error",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Endpoints

### 1. Health Check

Check if the API server is running and healthy.

**Endpoint:** `GET /api/health`

**Parameters:** None

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0",
  "uptime": "2 hours, 15 minutes"
}
```

**Example:**
```bash
curl http://localhost:5001/api/health
```

---

### 2. Get Inspections

Retrieve inspection times for a specific address and date by scraping Domain.com.au.

**Endpoint:** `GET /api/inspections`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `address` | string | Yes | Full property address including suburb and postcode |
| `date` | string | Yes | Date in YYYY-MM-DD format |

**Example Request:**
```bash
curl "http://localhost:5001/api/inspections?address=123%20Main%20St,%20Suburb%20NSW%202000&date=2024-01-15"
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
  },
  {
    "address": "789 Pine Road, Suburb NSW 2000",
    "date": "2024-01-15",
    "start_time": "2:00pm", 
    "end_time": "2:30pm"
  }
]
```

**Error Responses:**

*Missing Parameters (400):*
```json
{
  "error": "Missing address or date parameter",
  "code": "MISSING_PARAMETERS",
  "status": "error"
}
```

*Invalid Address Format (400):*
```json
{
  "error": "Invalid address format. Please include suburb and postcode",
  "code": "INVALID_ADDRESS",
  "status": "error"
}
```

*Scraping Error (500):*
```json
{
  "error": "Failed to scrape inspection data",
  "code": "SCRAPING_ERROR", 
  "status": "error"
}
```

---

### 3. Mock Data

Get mock inspection data for testing and development purposes.

**Endpoint:** `GET /api/mock-data`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `date` | string | Yes | Date in YYYY-MM-DD format |

**Example Request:**
```bash
curl "http://localhost:5001/api/mock-data?date=2024-01-15"
```

**Response:**
```json
[
  {
    "address": "123 Mock Street, Demo NSW 2000",
    "date": "2024-01-15",
    "start_time": "9:00am",
    "end_time": "9:30am"
  },
  {
    "address": "456 Test Avenue, Demo NSW 2000", 
    "date": "2024-01-15",
    "start_time": "10:15am",
    "end_time": "10:45am"
  }
]
```

---

### 4. Analytics (Future Enhancement)

Get analytics and recommendations for optimal inspection times.

**Endpoint:** `GET /api/analytics`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `address` | string | Yes | Property address |
| `date` | string | Yes | Target date |
| `radius` | number | No | Search radius in km (default: 2) |

**Example Request:**
```bash
curl "http://localhost:5001/api/analytics?address=123%20Main%20St,%20Suburb%20NSW%202000&date=2024-01-15&radius=3"
```

**Response:**
```json
{
  "total_inspections": 15,
  "peak_hours": ["10:00am", "2:00pm"],
  "recommended_times": ["9:00am", "4:00pm"],
  "competition_analysis": {
    "low": ["9:00am-10:00am", "4:00pm-5:00pm"],
    "medium": ["11:00am-12:00pm", "3:00pm-4:00pm"], 
    "high": ["10:00am-11:00am", "2:00pm-3:00pm"]
  },
  "success_probability": 0.75,
  "market_insights": {
    "average_duration": "30 minutes",
    "most_popular_day": "Saturday",
    "seasonal_trend": "increasing"
  }
}
```

## Data Models

### Inspection Object

```typescript
interface Inspection {
  address: string;        // Full property address
  date: string;          // Date in YYYY-MM-DD format
  start_time: string;    // Start time (e.g., "10:00am")
  end_time: string;      // End time (e.g., "10:30am")
}
```

### Analytics Object

```typescript
interface Analytics {
  total_inspections: number;
  peak_hours: string[];
  recommended_times: string[];
  competition_analysis: {
    low: string[];
    medium: string[];
    high: string[];
  };
  success_probability: number;
  market_insights: {
    average_duration: string;
    most_popular_day: string;
    seasonal_trend: string;
  };
}
```

## Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `MISSING_PARAMETERS` | Required parameters not provided | 400 |
| `INVALID_ADDRESS` | Address format is invalid | 400 |
| `INVALID_DATE` | Date format is invalid | 400 |
| `SCRAPING_ERROR` | Web scraping failed | 500 |
| `TIMEOUT_ERROR` | Request timed out | 504 |
| `RATE_LIMIT_EXCEEDED` | Too many requests | 429 |
| `INTERNAL_ERROR` | Server internal error | 500 |

## Implementation Details

### Web Scraping Process

1. **Address Parsing**: Extract suburb and postcode from full address
2. **URL Construction**: Build Domain.com.au URL with search parameters
3. **Page Loading**: Navigate to URL using Playwright/Firefox
4. **Data Extraction**: Parse inspection times from page elements
5. **Data Cleaning**: Format and validate extracted data
6. **Response**: Return structured JSON data

### CSS Selectors Used

- **Listing Cards**: `[data-testid='listing-card-wrapper-standard']`
- **Address**: `[data-testid='address-label']`
- **Inspection Time**: `[data-testid='inspection-time']`

### Fallback Mechanisms

1. **Mock Data**: If scraping fails, return generated mock data
2. **Retry Logic**: Automatic retry on temporary failures
3. **Error Handling**: Graceful degradation with informative errors

## Testing the API

### Using cURL

```bash
# Health check
curl http://localhost:5001/api/health

# Get inspections
curl "http://localhost:5001/api/inspections?address=123%20Main%20St,%20Suburb%20NSW%202000&date=2024-01-15"

# Get mock data
curl "http://localhost:5001/api/mock-data?date=2024-01-15"
```

### Using JavaScript/Fetch

```javascript
// Health check
const healthCheck = async () => {
  const response = await fetch('http://localhost:5001/api/health');
  const data = await response.json();
  console.log(data);
};

// Get inspections
const getInspections = async (address, date) => {
  const url = `http://localhost:5001/api/inspections?address=${encodeURIComponent(address)}&date=${date}`;
  const response = await fetch(url);
  const data = await response.json();
  return data;
};
```

### Using Python/Requests

```python
import requests

# Health check
response = requests.get('http://localhost:5001/api/health')
print(response.json())

# Get inspections
params = {
    'address': '123 Main St, Suburb NSW 2000',
    'date': '2024-01-15'
}
response = requests.get('http://localhost:5001/api/inspections', params=params)
print(response.json())
```

## Performance Considerations

### Response Times

- **Health Check**: < 100ms
- **Mock Data**: < 200ms  
- **Real Scraping**: 5-15 seconds (depends on page load time)

### Optimization Tips

1. **Caching**: Implement Redis caching for repeated requests
2. **Async Processing**: Use background tasks for long-running scrapes
3. **Rate Limiting**: Prevent abuse and ensure fair usage
4. **CDN**: Use CDN for static assets and API responses

## Security Considerations

### Input Validation

- **Address**: Validate format and sanitize input
- **Date**: Ensure valid date format and reasonable range
- **Parameters**: Escape special characters

### Rate Limiting

```python
# Example rate limiting implementation
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@app.route('/api/inspections')
@limiter.limit("10 per minute")
def get_inspections():
    # Implementation
```

### CORS Configuration

```python
from flask_cors import CORS

# Configure CORS for production
CORS(app, origins=['https://yourdomain.com'])
```

## Future Enhancements

### Planned Features

1. **Authentication**: JWT-based user authentication
2. **User Accounts**: Personal dashboards and saved searches
3. **Real-time Updates**: WebSocket connections for live data
4. **Advanced Analytics**: Machine learning predictions
5. **Multiple Sources**: Scrape from additional real estate sites
6. **Caching Layer**: Redis caching for improved performance
7. **Background Jobs**: Celery for async processing

### API Versioning

Future versions will use URL versioning:

```
/api/v1/inspections  # Current version
/api/v2/inspections  # Future version with enhanced features
```

## Support

For API-related questions and issues:

- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check this guide and inline code comments
- **Examples**: See the frontend implementation for usage examples

---

*Last updated: January 2024*