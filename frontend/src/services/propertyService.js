import { apiCall, handleApiResponse } from './api';

// Property service functions
export const propertyService = {
  // Get user's properties
  getUserProperties: async (userId, token) => {
    try {
      const response = await apiCall(`/api/users/${userId}/properties`, {
        method: 'GET'
      }, token);

      return handleApiResponse(response);
    } catch (error) {
      console.error('Get properties error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  },

  // Get user's analysis history
  getAnalysisHistory: async (userId, limit = 10, token) => {
    try {
      const response = await apiCall(`/api/users/${userId}/analysis-history?limit=${limit}`, {
        method: 'GET'
      }, token);

      return handleApiResponse(response);
    } catch (error) {
      console.error('Get analysis history error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  },

  // Add a new property
  addProperty: async (propertyData, token) => {
    try {
      const response = await apiCall('/api/properties', {
        method: 'POST',
        body: JSON.stringify(propertyData)
      }, token);

      return handleApiResponse(response);
    } catch (error) {
      console.error('Add property error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  },

  // Update property
  updateProperty: async (propertyId, propertyData, token) => {
    try {
      const response = await apiCall(`/api/properties/${propertyId}`, {
        method: 'PUT',
        body: JSON.stringify(propertyData)
      }, token);

      return handleApiResponse(response);
    } catch (error) {
      console.error('Update property error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  },

  // Delete property
  deleteProperty: async (propertyId, token) => {
    try {
      const response = await apiCall(`/api/properties/${propertyId}`, {
        method: 'DELETE'
      }, token);

      return handleApiResponse(response);
    } catch (error) {
      console.error('Delete property error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  },

  // Get property details
  getPropertyDetails: async (propertyId, token) => {
    try {
      const response = await apiCall(`/api/properties/${propertyId}`, {
        method: 'GET'
      }, token);

      return handleApiResponse(response);
    } catch (error) {
      console.error('Get property details error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  },

  // Analyze property
  analyzeProperty: async (propertyData, token) => {
    try {
      const response = await apiCall('/api/properties/analyze', {
        method: 'POST',
        body: JSON.stringify(propertyData)
      }, token);

      return handleApiResponse(response);
    } catch (error) {
      console.error('Property analysis error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  }
};