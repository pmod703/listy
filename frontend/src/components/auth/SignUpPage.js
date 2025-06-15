import React, { useState } from 'react';
import { 
  User, 
  Mail, 
  Lock, 
  Phone, 
  Building, 
  CreditCard, 
  Eye, 
  EyeOff, 
  CheckCircle, 
  AlertCircle,
  ArrowRight,
  Shield,
  UserPlus
} from 'lucide-react';

const SignUpPage = ({ onSignUpSuccess, onSwitchToLogin }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: '',
    phone: '',
    agencyName: '',
    licenseNumber: ''
  });

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState({
    score: 0,
    feedback: []
  });

  // Password strength checker
  const checkPasswordStrength = (password) => {
    const checks = [
      { test: /.{8,}/, message: 'At least 8 characters' },
      { test: /[A-Z]/, message: 'One uppercase letter' },
      { test: /[a-z]/, message: 'One lowercase letter' },
      { test: /\d/, message: 'One number' },
      { test: /[!@#$%^&*(),.?":{}|<>]/, message: 'One special character' }
    ];

    const passed = checks.filter(check => check.test.test(password));
    const failed = checks.filter(check => !check.test.test(password));

    return {
      score: passed.length,
      feedback: failed.map(check => check.message)
    };
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Clear specific error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }

    // Check password strength
    if (name === 'password') {
      setPasswordStrength(checkPasswordStrength(value));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!emailRegex.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (passwordStrength.score < 5) {
      newErrors.password = 'Password does not meet security requirements';
    }

    // Confirm password validation
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    // Name validation
    if (!formData.firstName.trim()) {
      newErrors.firstName = 'First name is required';
    }

    if (!formData.lastName.trim()) {
      newErrors.lastName = 'Last name is required';
    }

    // Phone validation (optional but if provided, should be valid)
    if (formData.phone && !/^\+?[\d\s\-\(\)]+$/.test(formData.phone)) {
      newErrors.phone = 'Please enter a valid phone number';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setErrors({});

    try {
      const response = await fetch('http://localhost:5001/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
          first_name: formData.firstName,
          last_name: formData.lastName,
          phone: formData.phone || null,
          agency_name: formData.agencyName || null,
          license_number: formData.licenseNumber || null
        }),
      });

      const data = await response.json();

      if (response.ok) {
        // Store tokens in localStorage
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        // Call success callback
        if (onSignUpSuccess) {
          onSignUpSuccess(data.user, data.access_token);
        }
      } else {
        // Handle server errors
        if (data.details) {
          // Validation errors from server
          setErrors(data.details);
        } else {
          setErrors({ general: data.error || 'Registration failed' });
        }
      }
    } catch (error) {
      console.error('Registration error:', error);
      setErrors({ general: 'Network error. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  const getPasswordStrengthColor = () => {
    if (passwordStrength.score <= 2) return 'bg-red-500';
    if (passwordStrength.score <= 3) return 'bg-yellow-500';
    if (passwordStrength.score <= 4) return 'bg-blue-500';
    return 'bg-green-500';
  };

  const getPasswordStrengthText = () => {
    if (passwordStrength.score <= 2) return 'Weak';
    if (passwordStrength.score <= 3) return 'Fair';
    if (passwordStrength.score <= 4) return 'Good';
    return 'Strong';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative overflow-hidden">
      {/* Particle Background */}
      <div className="particles">
        {[...Array(12)].map((_, i) => (
          <div key={i} className="particle" style={{top: `${Math.random() * 100}%`, animationDelay: `${i * 0.5}s`}}></div>
        ))}
      </div>
      
      {/* Animated background elements */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-3/4 left-1/2 w-48 h-48 bg-pink-500/10 rounded-full blur-3xl animate-pulse delay-500"></div>
      </div>
      
      <div className="relative z-10 flex items-center justify-center min-h-screen p-4">
        <div className="card-enhanced shadow-enhanced p-8 w-full max-w-2xl animate-fadeInUp">
          <div className="text-center mb-8">
            <div className="bg-gradient-to-br from-indigo-600 to-purple-600 w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg animate-glow">
              <UserPlus className="text-white w-10 h-10 animate-float" />
            </div>
            <h1 className="title-enhanced text-3xl gradient-text mb-2 animate-fadeInDown">
              Join Open Home Optimizer
            </h1>
            <p className="subtitle-enhanced text-gray-600 text-lg animate-fadeInUp">
              Create your account to start optimizing your open home schedules
            </p>
          </div>

          {/* General Error Message */}
          {errors.general && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl flex items-center space-x-3 animate-slideInDown">
              <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
              <span className="text-red-700">{errors.general}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Personal Information */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <User className="w-5 h-5 mr-2 text-indigo-600" />
                Personal Information
              </h3>
              
              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2 animate-slideInLeft">
                  <label className="block text-sm font-semibold text-gray-700">
                    First Name *
                  </label>
                  <input 
                    type="text"
                    name="firstName"
                    value={formData.firstName}
                    onChange={handleInputChange}
                    className={`input-enhanced text-lg ${errors.firstName ? 'border-red-500 focus:border-red-500' : ''}`}
                    placeholder="John"
                    required
                  />
                  {errors.firstName && (
                    <p className="text-red-500 text-sm flex items-center">
                      <AlertCircle className="w-4 h-4 mr-1" />
                      {errors.firstName}
                    </p>
                  )}
                </div>

                <div className="space-y-2 animate-slideInRight">
                  <label className="block text-sm font-semibold text-gray-700">
                    Last Name *
                  </label>
                  <input 
                    type="text"
                    name="lastName"
                    value={formData.lastName}
                    onChange={handleInputChange}
                    className={`input-enhanced text-lg ${errors.lastName ? 'border-red-500 focus:border-red-500' : ''}`}
                    placeholder="Smith"
                    required
                  />
                  {errors.lastName && (
                    <p className="text-red-500 text-sm flex items-center">
                      <AlertCircle className="w-4 h-4 mr-1" />
                      {errors.lastName}
                    </p>
                  )}
                </div>
              </div>

              <div className="space-y-2 animate-slideInLeft">
                <label className="block text-sm font-semibold text-gray-700">
                  Email Address *
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <input 
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    className={`input-enhanced text-lg pl-12 ${errors.email ? 'border-red-500 focus:border-red-500' : ''}`}
                    placeholder="agent@realestate.com"
                    required
                  />
                </div>
                {errors.email && (
                  <p className="text-red-500 text-sm flex items-center">
                    <AlertCircle className="w-4 h-4 mr-1" />
                    {errors.email}
                  </p>
                )}
              </div>

              <div className="space-y-2 animate-slideInRight">
                <label className="block text-sm font-semibold text-gray-700">
                  Phone Number
                </label>
                <div className="relative">
                  <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <input 
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleInputChange}
                    className={`input-enhanced text-lg pl-12 ${errors.phone ? 'border-red-500 focus:border-red-500' : ''}`}
                    placeholder="+1 (555) 123-4567"
                  />
                </div>
                {errors.phone && (
                  <p className="text-red-500 text-sm flex items-center">
                    <AlertCircle className="w-4 h-4 mr-1" />
                    {errors.phone}
                  </p>
                )}
              </div>
            </div>

            {/* Professional Information */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <Building className="w-5 h-5 mr-2 text-indigo-600" />
                Professional Information
              </h3>
              
              <div className="space-y-2 animate-slideInLeft">
                <label className="block text-sm font-semibold text-gray-700">
                  Agency Name
                </label>
                <div className="relative">
                  <Building className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <input 
                    type="text"
                    name="agencyName"
                    value={formData.agencyName}
                    onChange={handleInputChange}
                    className="input-enhanced text-lg pl-12"
                    placeholder="Premium Real Estate"
                  />
                </div>
              </div>

              <div className="space-y-2 animate-slideInRight">
                <label className="block text-sm font-semibold text-gray-700">
                  License Number
                </label>
                <div className="relative">
                  <CreditCard className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <input 
                    type="text"
                    name="licenseNumber"
                    value={formData.licenseNumber}
                    onChange={handleInputChange}
                    className="input-enhanced text-lg pl-12"
                    placeholder="RE123456"
                  />
                </div>
              </div>
            </div>

            {/* Security Information */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <Shield className="w-5 h-5 mr-2 text-indigo-600" />
                Security Information
              </h3>
              
              <div className="space-y-2 animate-slideInLeft">
                <label className="block text-sm font-semibold text-gray-700">
                  Password *
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <input 
                    type={showPassword ? "text" : "password"}
                    name="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    className={`input-enhanced text-lg pl-12 pr-12 ${errors.password ? 'border-red-500 focus:border-red-500' : ''}`}
                    placeholder="••••••••"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
                
                {/* Password Strength Indicator */}
                {formData.password && (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Password Strength:</span>
                      <span className={`text-sm font-medium ${
                        passwordStrength.score <= 2 ? 'text-red-600' :
                        passwordStrength.score <= 3 ? 'text-yellow-600' :
                        passwordStrength.score <= 4 ? 'text-blue-600' :
                        'text-green-600'
                      }`}>
                        {getPasswordStrengthText()}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full transition-all duration-300 ${getPasswordStrengthColor()}`}
                        style={{ width: `${(passwordStrength.score / 5) * 100}%` }}
                      ></div>
                    </div>
                    {passwordStrength.feedback.length > 0 && (
                      <div className="text-sm text-gray-600">
                        <p className="font-medium">Password must include:</p>
                        <ul className="list-disc list-inside space-y-1">
                          {passwordStrength.feedback.map((feedback, index) => (
                            <li key={index}>{feedback}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
                
                {errors.password && (
                  <p className="text-red-500 text-sm flex items-center">
                    <AlertCircle className="w-4 h-4 mr-1" />
                    {errors.password}
                  </p>
                )}
              </div>

              <div className="space-y-2 animate-slideInRight">
                <label className="block text-sm font-semibold text-gray-700">
                  Confirm Password *
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <input 
                    type={showConfirmPassword ? "text" : "password"}
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleInputChange}
                    className={`input-enhanced text-lg pl-12 pr-12 ${errors.confirmPassword ? 'border-red-500 focus:border-red-500' : ''}`}
                    placeholder="••••••••"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
                {formData.confirmPassword && formData.password === formData.confirmPassword && (
                  <p className="text-green-500 text-sm flex items-center">
                    <CheckCircle className="w-4 h-4 mr-1" />
                    Passwords match
                  </p>
                )}
                {errors.confirmPassword && (
                  <p className="text-red-500 text-sm flex items-center">
                    <AlertCircle className="w-4 h-4 mr-1" />
                    {errors.confirmPassword}
                  </p>
                )}
              </div>
            </div>

            {/* Submit Button */}
            <div className="pt-6">
              <button 
                type="submit"
                disabled={loading || passwordStrength.score < 5}
                className="btn-primary w-full py-4 text-lg shadow-enhanced-hover disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center space-x-3 animate-fadeInUp"
              >
                {loading ? (
                  <>
                    <div className="loading-dots">
                      <div></div>
                      <div></div>
                      <div></div>
                      <div></div>
                    </div>
                    <span>Creating Account...</span>
                  </>
                ) : (
                  <>
                    <UserPlus className="w-5 h-5 animate-float" />
                    <span>Create Account</span>
                    <ArrowRight className="w-5 h-5 animate-float delay-200" />
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Login Link */}
          <div className="mt-8 text-center animate-fadeInUp">
            <div className="glass p-4 border border-blue-200/50 shadow-enhanced">
              <p className="text-sm text-gray-600">
                Already have an account?{' '}
                <button 
                  onClick={onSwitchToLogin}
                  className="text-indigo-600 hover:text-indigo-700 font-semibold transition-colors duration-200"
                >
                  Sign in here
                </button>
              </p>
            </div>
          </div>

          {/* Security Notice */}
          <div className="mt-6 text-center animate-fadeInUp">
            <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl p-4">
              <div className="flex items-center justify-center space-x-2">
                <Shield className="w-5 h-5 text-green-600" />
                <span className="text-sm text-green-700 font-medium">
                  Your data is protected with enterprise-grade security
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SignUpPage;