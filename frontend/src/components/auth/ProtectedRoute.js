import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Shield, Lock } from 'lucide-react';

const ProtectedRoute = ({ children, requireVerified = false }) => {
  const { isAuthenticated, user, loading } = useAuth();

  // Show loading spinner while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="bg-gradient-to-br from-indigo-600 to-purple-600 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg animate-pulse">
            <Shield className="text-white w-8 h-8" />
          </div>
          <div className="loading-dots mb-4">
            <div></div>
            <div></div>
            <div></div>
            <div></div>
          </div>
          <p className="text-gray-600">Verifying authentication...</p>
        </div>
      </div>
    );
  }

  // If not authenticated, show access denied
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 flex items-center justify-center p-4">
        <div className="card-enhanced shadow-enhanced p-8 w-full max-w-md text-center">
          <div className="bg-gradient-to-br from-red-500 to-red-600 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
            <Lock className="text-white w-8 h-8" />
          </div>
          
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Authentication Required
          </h2>
          
          <p className="text-gray-600 mb-6">
            You need to be signed in to access this page. Please log in to continue.
          </p>
          
          <div className="space-y-3">
            <button 
              onClick={() => window.location.reload()}
              className="btn-primary w-full py-3"
            >
              Sign In
            </button>
            
            <p className="text-sm text-gray-500">
              Don't have an account? Create one to get started.
            </p>
          </div>
        </div>
      </div>
    );
  }

  // If verification is required but user is not verified
  if (requireVerified && user && !user.email_verified) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 flex items-center justify-center p-4">
        <div className="card-enhanced shadow-enhanced p-8 w-full max-w-md text-center">
          <div className="bg-gradient-to-br from-yellow-500 to-orange-600 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
            <Shield className="text-white w-8 h-8" />
          </div>
          
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Email Verification Required
          </h2>
          
          <p className="text-gray-600 mb-6">
            Please verify your email address to access this feature. Check your inbox for a verification link.
          </p>
          
          <div className="space-y-3">
            <button 
              onClick={() => {
                // TODO: Implement resend verification email
                alert('Verification email resent! Please check your inbox.');
              }}
              className="btn-primary w-full py-3"
            >
              Resend Verification Email
            </button>
            
            <button 
              onClick={() => window.location.reload()}
              className="text-indigo-600 hover:text-indigo-700 font-semibold text-sm"
            >
              I've verified my email
            </button>
          </div>
        </div>
      </div>
    );
  }

  // User is authenticated (and verified if required), render children
  return children;
};

export default ProtectedRoute;