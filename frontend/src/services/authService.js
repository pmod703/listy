import { apiCall, handleApiResponse } from './api';

// Authentication service functions
export const authService = {
  // Validate token with server
  validateToken: async (token) => {
    try {
      const response = await apiCall('/api/auth/validate-token', {
        method: 'GET'
      }, token);

      if (response.ok) {
        const data = await response.json();
        return data.valid;
      }
      return false;
    } catch (error) {
      console.error('Token validation error:', error);
      return false;
    }
  },

  // Refresh access token
  refreshToken: async (refreshToken) => {
    try {
      const response = await apiCall('/api/auth/refresh', {
        method: 'POST',
        body: JSON.stringify({ refresh_token: refreshToken })
      });

      return handleApiResponse(response);
    } catch (error) {
      console.error('Token refresh error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  },

  // Get current user info
  getCurrentUser: async (token) => {
    try {
      const response = await apiCall('/api/auth/me', {
        method: 'GET'
      }, token);

      return handleApiResponse(response);
    } catch (error) {
      console.error('Get current user error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  },

  // Login function
  login: async (email, password) => {
    try {
      const response = await apiCall('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password })
      });

      return handleApiResponse(response);
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  },

  // Register function
  register: async (userData) => {
    try {
      const response = await apiCall('/api/auth/register', {
        method: 'POST',
        body: JSON.stringify(userData)
      });

      return handleApiResponse(response);
    } catch (error) {
      console.error('Registration error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  },

  // Logout function
  logout: async (token) => {
    try {
      await apiCall('/api/auth/logout', {
        method: 'POST'
      }, token);
      return { success: true };
    } catch (error) {
      console.error('Logout error:', error);
      return { success: false, error: 'Network error during logout.' };
    }
  },

  // Update user profile
  updateProfile: async (profileData, token) => {
    try {
      const response = await apiCall('/api/auth/me', {
        method: 'PUT',
        body: JSON.stringify(profileData)
      }, token);

      return handleApiResponse(response);
    } catch (error) {
      console.error('Profile update error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  },

  // Change password
  changePassword: async (currentPassword, newPassword, token) => {
    try {
      const response = await apiCall('/api/auth/change-password', {
        method: 'POST',
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword
        })
      }, token);

      return handleApiResponse(response);
    } catch (error) {
      console.error('Password change error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  },

  // Request password reset
  requestPasswordReset: async (email) => {
    try {
      const response = await apiCall('/api/auth/request-password-reset', {
        method: 'POST',
        body: JSON.stringify({ email })
      });

      return handleApiResponse(response);
    } catch (error) {
      console.error('Password reset request error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  }
};