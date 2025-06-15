import { VALIDATION_RULES } from './constants';

// Validation utility functions

// Email validation
export const validateEmail = (email) => {
  if (!email || email.trim() === '') {
    return { isValid: false, message: 'Email is required' };
  }
  
  if (!VALIDATION_RULES.EMAIL.PATTERN.test(email)) {
    return { isValid: false, message: VALIDATION_RULES.EMAIL.MESSAGE };
  }
  
  return { isValid: true, message: '' };
};

// Password validation
export const validatePassword = (password) => {
  if (!password || password.length === 0) {
    return { isValid: false, message: 'Password is required' };
  }
  
  if (password.length < VALIDATION_RULES.PASSWORD.MIN_LENGTH) {
    return { isValid: false, message: VALIDATION_RULES.PASSWORD.MESSAGE };
  }
  
  return { isValid: true, message: '' };
};

// Phone number validation (Australian format)
export const validatePhone = (phone) => {
  if (!phone || phone.trim() === '') {
    return { isValid: false, message: 'Phone number is required' };
  }
  
  if (!VALIDATION_RULES.PHONE.PATTERN.test(phone)) {
    return { isValid: false, message: VALIDATION_RULES.PHONE.MESSAGE };
  }
  
  return { isValid: true, message: '' };
};

// Name validation
export const validateName = (name, fieldName = 'Name') => {
  if (!name || name.trim() === '') {
    return { isValid: false, message: `${fieldName} is required` };
  }
  
  if (name.trim().length < 2) {
    return { isValid: false, message: `${fieldName} must be at least 2 characters` };
  }
  
  return { isValid: true, message: '' };
};

// Required field validation
export const validateRequired = (value, fieldName) => {
  if (!value || (typeof value === 'string' && value.trim() === '')) {
    return { isValid: false, message: `${fieldName} is required` };
  }
  
  return { isValid: true, message: '' };
};

// Confirm password validation
export const validateConfirmPassword = (password, confirmPassword) => {
  if (!confirmPassword || confirmPassword.trim() === '') {
    return { isValid: false, message: 'Confirm password is required' };
  }
  
  if (password !== confirmPassword) {
    return { isValid: false, message: 'Passwords do not match' };
  }
  
  return { isValid: true, message: '' };
};

// Property price validation
export const validatePrice = (price, fieldName = 'Price') => {
  if (!price || price === '') {
    return { isValid: false, message: `${fieldName} is required` };
  }
  
  const numPrice = parseFloat(price);
  if (isNaN(numPrice) || numPrice <= 0) {
    return { isValid: false, message: `${fieldName} must be a valid positive number` };
  }
  
  return { isValid: true, message: '' };
};

// Bedrooms/Bathrooms validation
export const validateCount = (count, fieldName, min = 0, max = 20) => {
  if (count === '' || count === null || count === undefined) {
    return { isValid: false, message: `${fieldName} is required` };
  }
  
  const numCount = parseInt(count);
  if (isNaN(numCount) || numCount < min || numCount > max) {
    return { isValid: false, message: `${fieldName} must be between ${min} and ${max}` };
  }
  
  return { isValid: true, message: '' };
};

// Address validation
export const validateAddress = (address) => {
  if (!address || address.trim() === '') {
    return { isValid: false, message: 'Address is required' };
  }
  
  if (address.trim().length < 5) {
    return { isValid: false, message: 'Address must be at least 5 characters' };
  }
  
  return { isValid: true, message: '' };
};

// Validate form with multiple fields
export const validateForm = (formData, validationRules) => {
  const errors = {};
  let isValid = true;
  
  Object.keys(validationRules).forEach(field => {
    const rule = validationRules[field];
    const value = formData[field];
    
    let fieldValidation;
    
    switch (rule.type) {
      case 'email':
        fieldValidation = validateEmail(value);
        break;
      case 'password':
        fieldValidation = validatePassword(value);
        break;
      case 'phone':
        fieldValidation = validatePhone(value);
        break;
      case 'name':
        fieldValidation = validateName(value, rule.fieldName || field);
        break;
      case 'required':
        fieldValidation = validateRequired(value, rule.fieldName || field);
        break;
      case 'price':
        fieldValidation = validatePrice(value, rule.fieldName || field);
        break;
      case 'count':
        fieldValidation = validateCount(value, rule.fieldName || field, rule.min, rule.max);
        break;
      case 'address':
        fieldValidation = validateAddress(value);
        break;
      default:
        fieldValidation = { isValid: true, message: '' };
    }
    
    if (!fieldValidation.isValid) {
      errors[field] = fieldValidation.message;
      isValid = false;
    }
  });
  
  return { isValid, errors };
};

// Registration form validation
export const validateRegistrationForm = (formData) => {
  const validationRules = {
    firstName: { type: 'name', fieldName: 'First name' },
    lastName: { type: 'name', fieldName: 'Last name' },
    email: { type: 'email' },
    phone: { type: 'phone' },
    password: { type: 'password' }
  };
  
  const result = validateForm(formData, validationRules);
  
  // Additional validation for confirm password
  const confirmPasswordValidation = validateConfirmPassword(
    formData.password, 
    formData.confirmPassword
  );
  
  if (!confirmPasswordValidation.isValid) {
    result.errors.confirmPassword = confirmPasswordValidation.message;
    result.isValid = false;
  }
  
  return result;
};

// Login form validation
export const validateLoginForm = (formData) => {
  const validationRules = {
    email: { type: 'email' },
    password: { type: 'required', fieldName: 'Password' }
  };
  
  return validateForm(formData, validationRules);
};