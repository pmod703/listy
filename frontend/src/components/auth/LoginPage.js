import React, { useState } from 'react';
import { 
  Mail, 
  Lock, 
  Eye, 
  EyeOff, 
  AlertCircle,
  ArrowRight,
  Shield,
  LogIn,
  Home,
  RefreshCw
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

const LoginPage = ({ onLoginSuccess, onSwitchToSignUp, onForgotPassword }) => {
  const { login } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });

  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);

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
      // Use the login function from AuthContext
      const result = await login(formData.email, formData.password);

      if (result.success) {
        // Store remember me preference
        if (rememberMe) {
          localStorage.setItem('remember_me', 'true');
        } else {
          localStorage.removeItem('remember_me');
        }
        
        // Call success callback if provided
        if (onLoginSuccess) {
          onLoginSuccess(result.user, localStorage.getItem('access_token'));
        }
        
        // The AuthContext will handle the state update and redirect
      } else {
        // Handle login errors
        if (result.error) {
          if (result.error.includes('locked')) {
            setErrors({ general: 'Account is temporarily locked due to multiple failed login attempts. Please try again later.' });
          } else if (result.error.includes('Invalid email or password')) {
            setErrors({ general: 'Invalid email or password. Please check your credentials and try again.' });
          } else {
            setErrors({ general: result.error });
          }
        } else {
          setErrors({ general: 'Login failed. Please try again.' });
        }
      }
    } catch (error) {
      console.error('Login error:', error);
      setErrors({ general: 'Network error. Please check your connection and try again.' });
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPassword = () => {
    if (onForgotPassword) {
      onForgotPassword(formData.email);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative overflow-hidden">
      {/* Particle Background */}
      <div className="particles">
        {[...Array(9)].map((_, i) => (
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
        <div className="card-enhanced shadow-enhanced p-8 w-full max-w-md animate-fadeInUp">
          <div className="text-center mb-8">
            <div className="bg-gradient-to-br from-indigo-600 to-purple-600 w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg animate-glow">
              <Home className="text-white w-10 h-10 animate-float" />
            </div>
            <h1 className="title-enhanced text-3xl gradient-text mb-2 animate-fadeInDown">
              Welcome Back
            </h1>
            <p className="subtitle-enhanced text-gray-600 text-lg animate-fadeInUp">
              Sign in to your Open Home Optimizer account
            </p>
          </div>

          {/* General Error Message */}
          {errors.general && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl flex items-center space-x-3 animate-slideInDown">
              <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
              <span className="text-red-700 text-sm">{errors.general}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2 animate-slideInLeft">
              <label className="block text-sm font-semibold text-gray-700">
                Email Address
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
                  autoComplete="email"
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
                Password
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
                  autoComplete="current-password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors duration-200"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
              {errors.password && (
                <p className="text-red-500 text-sm flex items-center">
                  <AlertCircle className="w-4 h-4 mr-1" />
                  {errors.password}
                </p>
              )}
            </div>

            {/* Remember Me and Forgot Password */}
            <div className="flex items-center justify-between animate-fadeInUp">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="w-4 h-4 text-indigo-600 bg-gray-100 border-gray-300 rounded focus:ring-indigo-500 focus:ring-2"
                />
                <span className="text-sm text-gray-600">Remember me</span>
              </label>
              
              <button
                type="button"
                onClick={handleForgotPassword}
                className="text-sm text-indigo-600 hover:text-indigo-700 font-semibold transition-colors duration-200"
              >
                Forgot password?
              </button>
            </div>
            
            <button 
              type="submit"
              disabled={loading}
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
                  <span>Signing In...</span>
                </>
              ) : (
                <>
                  <LogIn className="w-5 h-5 animate-float" />
                  <span>Sign In</span>
                  <ArrowRight className="w-5 h-5 animate-float delay-200" />
                </>
              )}
            </button>
          </form>

          {/* Sign Up Link */}
          <div className="mt-8 text-center animate-fadeInUp">
            <div className="glass p-4 border border-blue-200/50 shadow-enhanced">
              <p className="text-sm text-gray-600">
                Don't have an account?{' '}
                <button 
                  onClick={onSwitchToSignUp}
                  className="text-indigo-600 hover:text-indigo-700 font-semibold transition-colors duration-200"
                >
                  Create one here
                </button>
              </p>
            </div>
          </div>

          {/* Demo Mode Notice */}
          <div className="mt-6 text-center animate-fadeInUp">
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-4">
              <div className="flex items-center justify-center space-x-2 mb-2">
                <Shield className="w-5 h-5 text-blue-600" />
                <span className="text-sm text-blue-700 font-medium">
                  Secure Authentication
                </span>
              </div>
              <p className="text-xs text-blue-600">
                Your login is protected with enterprise-grade security including JWT tokens and account lockout protection.
              </p>
            </div>
          </div>

          {/* Quick Demo Access */}
          <div className="mt-4 text-center animate-fadeInUp">
            <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl p-4">
              <div className="flex items-center justify-center space-x-2 mb-2">
                <RefreshCw className="w-4 h-4 text-green-600" />
                <span className="text-sm text-green-700 font-medium">
                  Demo Access
                </span>
              </div>
              <p className="text-xs text-green-600 mb-2">
                For testing: Use any valid email format and password with 8+ characters, uppercase, lowercase, number, and special character.
              </p>
              <button
                type="button"
                onClick={() => {
                  setFormData({
                    email: 'demo@realestate.com',
                    password: 'DemoPass123!'
                  });
                }}
                className="text-xs text-green-700 hover:text-green-800 font-semibold underline"
              >
                Fill Demo Credentials
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;