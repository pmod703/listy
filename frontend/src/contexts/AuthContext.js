import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // API base URL
  const API_BASE_URL = 'http://localhost:5001';

  // Initialize authentication state from localStorage
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const storedToken = localStorage.getItem('access_token');
        const storedUser = localStorage.getItem('user');

        if (storedToken && storedUser) {
          // Validate token with server
          const isValid = await validateToken(storedToken);
          
          if (isValid) {
            setToken(storedToken);
            setUser(JSON.parse(storedUser));
            setIsAuthenticated(true);
          } else {
            // Token is invalid, try to refresh
            const refreshed = await refreshToken();
            if (!refreshed) {
              clearAuth();
            }
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        clearAuth();
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();
  }, []);

  // Validate token with server
  const validateToken = async (tokenToValidate) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/validate-token`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${tokenToValidate}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        return data.valid;
      }
      return false;
    } catch (error) {
      console.error('Token validation error:', error);
      return false;
    }
  };

  // Refresh access token
  const refreshToken = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        return false;
      }

      const response = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          refresh_token: refreshToken
        })
      });

      if (response.ok) {
        const data = await response.json();
        const newToken = data.access_token;
        
        localStorage.setItem('access_token', newToken);
        setToken(newToken);
        
        // Get updated user info
        await getCurrentUser(newToken);
        
        return true;
      } else {
        return false;
      }
    } catch (error) {
      console.error('Token refresh error:', error);
      return false;
    }
  };

  // Get current user info
  const getCurrentUser = async (tokenToUse = null) => {
    try {
      const authToken = tokenToUse || token;
      if (!authToken) return null;

      const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data.user);
        localStorage.setItem('user', JSON.stringify(data.user));
        return data.user;
      }
      return null;
    } catch (error) {
      console.error('Get current user error:', error);
      return null;
    }
  };

  // Login function
  const login = async (email, password) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
      });

      const data = await response.json();

      if (response.ok) {
        const { user: userData, access_token, refresh_token } = data;
        
        // Store tokens and user data
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);
        localStorage.setItem('user', JSON.stringify(userData));
        
        // Update state
        setToken(access_token);
        setUser(userData);
        setIsAuthenticated(true);
        
        return { success: true, user: userData };
      } else {
        return { success: false, error: data.error || 'Login failed' };
      }
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  };

  // Register function
  const register = async (userData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
      });

      const data = await response.json();

      if (response.ok) {
        const { user: newUser, access_token } = data;
        
        // Store token and user data
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('user', JSON.stringify(newUser));
        
        // Update state
        setToken(access_token);
        setUser(newUser);
        setIsAuthenticated(true);
        
        return { success: true, user: newUser };
      } else {
        return { 
          success: false, 
          error: data.error || 'Registration failed',
          details: data.details || {}
        };
      }
    } catch (error) {
      console.error('Registration error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  };

  // Logout function
  const logout = async () => {
    try {
      if (token) {
        // Notify server about logout
        await fetch(`${API_BASE_URL}/api/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      clearAuth();
    }
  };

  // Clear authentication state
  const clearAuth = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
  };

  // Update user profile
  const updateProfile = async (profileData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(profileData)
      });

      const data = await response.json();

      if (response.ok) {
        const updatedUser = data.user;
        setUser(updatedUser);
        localStorage.setItem('user', JSON.stringify(updatedUser));
        return { success: true, user: updatedUser };
      } else {
        return { success: false, error: data.error || 'Profile update failed' };
      }
    } catch (error) {
      console.error('Profile update error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  };

  // Change password
  const changePassword = async (currentPassword, newPassword) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/change-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword
        })
      });

      const data = await response.json();

      if (response.ok) {
        return { success: true, message: data.message };
      } else {
        return { success: false, error: data.error || 'Password change failed' };
      }
    } catch (error) {
      console.error('Password change error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  };

  // Request password reset
  const requestPasswordReset = async (email) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/request-password-reset`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email })
      });

      const data = await response.json();

      if (response.ok) {
        return { success: true, message: data.message };
      } else {
        return { success: false, error: data.error || 'Password reset request failed' };
      }
    } catch (error) {
      console.error('Password reset request error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  };

  // Make authenticated API calls
  const apiCall = async (url, options = {}) => {
    const authToken = token;
    
    if (!authToken) {
      throw new Error('No authentication token available');
    }

    const config = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
        'Authorization': `Bearer ${authToken}`
      }
    };

    try {
      const response = await fetch(`${API_BASE_URL}${url}`, config);

      // If token is expired, try to refresh
      if (response.status === 401) {
        const refreshed = await refreshToken();
        if (refreshed) {
          // Retry the original request with new token
          config.headers['Authorization'] = `Bearer ${token}`;
          return await fetch(`${API_BASE_URL}${url}`, config);
        } else {
          // Refresh failed, logout user
          clearAuth();
          throw new Error('Authentication expired');
        }
      }

      return response;
    } catch (error) {
      console.error('API call error:', error);
      throw error;
    }
  };

  // Get user's properties
  const getUserProperties = async () => {
    if (!user) return { success: false, error: 'User not authenticated' };

    try {
      const response = await apiCall(`/api/users/${user.id}/properties`);
      
      if (response.ok) {
        const data = await response.json();
        return { success: true, properties: data.properties };
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData.error || 'Failed to fetch properties' };
      }
    } catch (error) {
      console.error('Get properties error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  };

  // Get user's analysis history
  const getAnalysisHistory = async (limit = 10) => {
    if (!user) return { success: false, error: 'User not authenticated' };

    try {
      const response = await apiCall(`/api/users/${user.id}/analysis-history?limit=${limit}`);
      
      if (response.ok) {
        const data = await response.json();
        return { success: true, history: data.analysis_history };
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData.error || 'Failed to fetch analysis history' };
      }
    } catch (error) {
      console.error('Get analysis history error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  };

  const value = {
    // State
    user,
    token,
    loading,
    isAuthenticated,
    
    // Authentication methods
    login,
    register,
    logout,
    
    // User management
    updateProfile,
    changePassword,
    requestPasswordReset,
    getCurrentUser,
    
    // API utilities
    apiCall,
    
    // Data fetching
    getUserProperties,
    getAnalysisHistory,
    
    // Utilities
    validateToken,
    refreshToken
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};