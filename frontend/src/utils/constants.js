// Application constants
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/api/auth/login',
    REGISTER: '/api/auth/register',
    LOGOUT: '/api/auth/logout',
    REFRESH: '/api/auth/refresh',
    VALIDATE_TOKEN: '/api/auth/validate-token',
    ME: '/api/auth/me',
    CHANGE_PASSWORD: '/api/auth/change-password',
    REQUEST_PASSWORD_RESET: '/api/auth/request-password-reset'
  },
  PROPERTIES: {
    BASE: '/api/properties',
    ANALYZE: '/api/properties/analyze',
    USER_PROPERTIES: (userId) => `/api/users/${userId}/properties`,
    ANALYSIS_HISTORY: (userId) => `/api/users/${userId}/analysis-history`
  }
};

export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER: 'user'
};

export const VALIDATION_RULES = {
  EMAIL: {
    PATTERN: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    MESSAGE: 'Please enter a valid email address'
  },
  PASSWORD: {
    MIN_LENGTH: 8,
    MESSAGE: 'Password must be at least 8 characters long'
  },
  PHONE: {
    PATTERN: /^(\+61|0)[2-9]\d{8}$/, // Australian phone number format
    MESSAGE: 'Please enter a valid Australian phone number'
  }
};

export const USER_ROLES = {
  ADMIN: 'admin',
  USER: 'user',
  AGENT: 'agent'
};

export const PROPERTY_TYPES = {
  HOUSE: 'house',
  APARTMENT: 'apartment',
  TOWNHOUSE: 'townhouse',
  UNIT: 'unit',
  VILLA: 'villa',
  STUDIO: 'studio'
};

export const AUSTRALIAN_STATES = [
  { code: 'NSW', name: 'New South Wales' },
  { code: 'VIC', name: 'Victoria' },
  { code: 'QLD', name: 'Queensland' },
  { code: 'WA', name: 'Western Australia' },
  { code: 'SA', name: 'South Australia' },
  { code: 'TAS', name: 'Tasmania' },
  { code: 'ACT', name: 'Australian Capital Territory' },
  { code: 'NT', name: 'Northern Territory' }
];

export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection and try again.',
  UNAUTHORIZED: 'You are not authorized to perform this action.',
  SESSION_EXPIRED: 'Your session has expired. Please log in again.',
  VALIDATION_ERROR: 'Please check your input and try again.',
  SERVER_ERROR: 'Server error. Please try again later.',
  NOT_FOUND: 'The requested resource was not found.'
};