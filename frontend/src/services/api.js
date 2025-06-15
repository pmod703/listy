// Base API configuration and utilities
const API_BASE_URL = 'http://localhost:5001';

// Generic API call helper
export const apiCall = async (url, options = {}, token = null) => {
  const config = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
      ...(token && { 'Authorization': `Bearer ${token}` })
    }
  };

  try {
    const response = await fetch(`${API_BASE_URL}${url}`, config);
    return response;
  } catch (error) {
    console.error('API call error:', error);
    throw error;
  }
};

// Handle API responses
export const handleApiResponse = async (response) => {
  try {
    const data = await response.json();
    
    if (response.ok) {
      return { success: true, data };
    } else {
      return { 
        success: false, 
        error: data.error || 'Request failed',
        details: data.details || {}
      };
    }
  } catch (error) {
    return { 
      success: false, 
      error: 'Network error. Please try again.' 
    };
  }
};

export { API_BASE_URL };