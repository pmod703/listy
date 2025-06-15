import { useState, useCallback } from 'react';
import { useAuth } from './useAuth';

export const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { apiCall } = useAuth();

  const makeRequest = useCallback(async (url, options = {}) => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiCall(url, options);
      const data = await response.json();
      
      if (response.ok) {
        setLoading(false);
        return { success: true, data };
      } else {
        setError(data.error || 'Request failed');
        setLoading(false);
        return { success: false, error: data.error || 'Request failed' };
      }
    } catch (err) {
      const errorMessage = err.message || 'Network error occurred';
      setError(errorMessage);
      setLoading(false);
      return { success: false, error: errorMessage };
    }
  }, [apiCall]);

  return {
    loading,
    error,
    makeRequest,
    clearError: () => setError(null)
  };
};