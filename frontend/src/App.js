import React, { useState, useEffect } from 'react';
import { Calendar, Clock, MapPin, Home, Users, Car, Bath, Bed, Search, Filter, TrendingUp, AlertCircle, CheckCircle, Star, BarChart3, Zap, Target, ArrowRight, ChevronDown, Menu, X, User, LogOut } from 'lucide-react';
import './styles/components.css';

// Authentication components
import { AuthProvider, useAuth } from './contexts/AuthContext';
import SignUpPage from './components/auth/SignUpPage';
import LoginPage from './components/auth/LoginPage';
import ProtectedRoute from './components/auth/ProtectedRoute';
import AddressAutocomplete from './components/common/AddressAutocomplete';

// Authentication wrapper component
const AuthenticatedApp = () => {
  const { isAuthenticated, user, logout, loading } = useAuth();
  const [authView, setAuthView] = useState('login'); // 'login' or 'signup'

  // Show loading spinner while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="bg-gradient-to-br from-indigo-600 to-purple-600 w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg animate-pulse">
            <Home className="text-white w-10 h-10" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-4">Open Home Optimizer</h2>
          <div className="loading-dots">
            <div></div>
            <div></div>
            <div></div>
            <div></div>
          </div>
          <p className="text-gray-300 mt-4">Checking authentication...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    if (authView === 'signup') {
      return (
        <SignUpPage 
          onSignUpSuccess={(user, token) => {
            // Authentication context will handle the state update
            console.log('Sign up successful:', user);
          }}
          onSwitchToLogin={() => setAuthView('login')}
        />
      );
    } else {
      return (
        <LoginPage 
          onLoginSuccess={(user, token) => {
            // Authentication context will handle the state update
            console.log('Login successful:', user);
          }}
          onSwitchToSignUp={() => setAuthView('signup')}
          onForgotPassword={(email) => {
            // TODO: Implement forgot password
            alert(`Password reset link sent to ${email}`);
          }}
        />
      );
    }
  }

  // User is authenticated, show the main app
  return <MainApp user={user} onLogout={logout} />;
};

// Main application component (only shown when authenticated)
const MainApp = ({ user, onLogout }) => {
  // Component state
  const [currentView, setCurrentView] = useState('dashboard');
  const [propertyData, setPropertyData] = useState({
    address: '',
    bedrooms: 3,
    bathrooms: 2,
    carSpots: 1,
    propertyType: 'house'
  });
  
  const [similarPropertyCriteria, setSimilarPropertyCriteria] = useState({
    bedrooms: '3-4',
    bathrooms: '2+',
    carSpots: '1-2'
  });
  
  const [addressValue, setAddressValue] = useState('');
  const [searchRadius, setSearchRadius] = useState(5);
  const [timeFilter, setTimeFilter] = useState({ start: '10:00', end: '15:00' });
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [animationStep, setAnimationStep] = useState(0);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedTimeSlot, setSelectedTimeSlot] = useState(null);

  // Get authentication context
  const { apiCall } = useAuth();

  // Mock data for demonstration
  const mockOpenHomes = [
    { time: '09:00', count: 2, competition: 'low' },
    { time: '09:30', count: 1, competition: 'low' },
    { time: '10:00', count: 8, competition: 'high' },
    { time: '10:30', count: 12, competition: 'very-high' },
    { time: '11:00', count: 15, competition: 'very-high' },
    { time: '11:30', count: 10, competition: 'high' },
    { time: '12:00', count: 18, competition: 'very-high' },
    { time: '12:30', count: 14, competition: 'very-high' },
    { time: '13:00', count: 16, competition: 'very-high' },
    { time: '13:30', count: 9, competition: 'high' },
    { time: '14:00', count: 7, competition: 'medium' },
    { time: '14:30', count: 4, competition: 'low' },
    { time: '15:00', count: 3, competition: 'low' },
    { time: '15:30', count: 2, competition: 'low' }
  ];

  useEffect(() => {
    if (loading) {
      const timer = setInterval(() => {
        setAnimationStep(prev => (prev + 1) % 4);
      }, 500);
      return () => clearInterval(timer);
    }
  }, [loading]);

  const handleAddressChange = (e) => {
    const value = e.target.value;
    setAddressValue(value);
    setPropertyData(prev => ({ ...prev, address: value }));
  };

  const handlePropertySubmit = async (e) => {
    e?.preventDefault();
    if (!addressValue.trim()) return;
    
    setLoading(true);
    setAnimationStep(0);
    
    try {
      // Use current date if no date specified
      const currentDate = new Date().toISOString().split('T')[0];
      
      // Call the backend API (with authentication if available)
      const apiUrl = `/api/inspections?address=${encodeURIComponent(addressValue)}&date=${currentDate}&start_time=${timeFilter.start}&end_time=${timeFilter.end}&similar_bedrooms=${encodeURIComponent(similarPropertyCriteria.bedrooms)}&similar_bathrooms=${encodeURIComponent(similarPropertyCriteria.bathrooms)}&similar_car_spots=${encodeURIComponent(similarPropertyCriteria.carSpots)}`;
      
      let response;
      try {
        // Try authenticated API call first
        response = await apiCall(apiUrl);
      } catch (error) {
        // Fallback to public API call
        response = await fetch(`http://localhost:5001${apiUrl}`);
      }
      
      if (!response.ok) {
        throw new Error('Failed to fetch inspection data');
      }
      
      const data = await response.json();
      
      // Transform API response to match frontend format
      const transformedData = data.competition_analysis.map(slot => ({
        time: slot.time,
        count: slot.count,
        competition: slot.competition
      }));
      
      setRecommendations(transformedData);
      setLoading(false);
      setCurrentView('results');
      setCurrentIndex(0);
      setSelectedTimeSlot(transformedData[0]);
      
    } catch (error) {
      console.error('Error fetching data:', error);
      
      // Fallback to mock data if API fails
      const filtered = mockOpenHomes.filter(slot => {
        const slotTime = parseInt(slot.time.split(':')[0]);
        const startTime = parseInt(timeFilter.start.split(':')[0]);
        const endTime = parseInt(timeFilter.end.split(':')[0]);
        return slotTime >= startTime && slotTime <= endTime;
      });
      
      const sorted = filtered.sort((a, b) => a.count - b.count);
      setRecommendations(sorted);
      setLoading(false);
      setCurrentView('results');
      setCurrentIndex(0);
      setSelectedTimeSlot(sorted[0]);
    }
  };

  const getCompetitionColor = (level) => {
    switch(level) {
      case 'low': return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'medium': return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'high': return 'bg-orange-50 text-orange-700 border-orange-200';
      case 'very-high': return 'bg-red-50 text-red-700 border-red-200';
      default: return 'bg-gray-50 text-gray-700 border-gray-200';
    }
  };

  const getCompetitionGradient = (level) => {
    switch(level) {
      case 'low': return 'from-emerald-400 to-emerald-600';
      case 'medium': return 'from-amber-400 to-amber-600';
      case 'high': return 'from-orange-400 to-orange-600';
      case 'very-high': return 'from-red-400 to-red-600';
      default: return 'from-gray-400 to-gray-600';
    }
  };

  return currentView === 'dashboard' ? (
    <DashboardView 
      addressValue={addressValue}
      handleAddressChange={handleAddressChange}
      propertyData={propertyData}
      setPropertyData={setPropertyData}
      similarPropertyCriteria={similarPropertyCriteria}
      setSimilarPropertyCriteria={setSimilarPropertyCriteria}
      searchRadius={searchRadius}
      setSearchRadius={setSearchRadius}
      timeFilter={timeFilter}
      setTimeFilter={setTimeFilter}
      handlePropertySubmit={handlePropertySubmit}
      loading={loading}
      animationStep={animationStep}
      user={user}
      onLogout={onLogout}
      mobileMenuOpen={mobileMenuOpen}
      setMobileMenuOpen={setMobileMenuOpen}
    />
  ) : (
    <ResultsView 
      addressValue={addressValue}
      searchRadius={searchRadius}
      recommendations={recommendations}
      currentIndex={currentIndex}
      setCurrentIndex={setCurrentIndex}
      setSelectedTimeSlot={setSelectedTimeSlot}
      setCurrentView={setCurrentView}
      user={user}
      onLogout={onLogout}
      mockOpenHomes={mockOpenHomes}
      getCompetitionColor={getCompetitionColor}
      getCompetitionGradient={getCompetitionGradient}
    />
  );
};

const DashboardView = ({ 
  addressValue, 
  handleAddressChange, 
  propertyData, 
  setPropertyData, 
  similarPropertyCriteria,
  setSimilarPropertyCriteria,
  searchRadius, 
  setSearchRadius, 
  timeFilter, 
  setTimeFilter, 
  handlePropertySubmit, 
  loading, 
  animationStep, 
  user,
  onLogout, 
  mobileMenuOpen, 
  setMobileMenuOpen 
}) => (
  <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 relative">
    {/* Particle Background */}
    <div className="particles">
      {[...Array(12)].map((_, i) => (
        <div key={i} className="particle" style={{top: `${Math.random() * 100}%`, animationDelay: `${i * 0.5}s`}}></div>
      ))}
    </div>
    <nav className="glass border-b border-white/20 sticky top-0 z-50 shadow-enhanced">
      <div className="container mx-auto px-6 py-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-3 animate-slideInLeft">
            <div className="bg-gradient-to-br from-indigo-600 to-purple-600 w-10 h-10 rounded-xl flex items-center justify-center animate-glow">
              <Home className="text-white w-6 h-6 animate-float" />
            </div>
            <div>
              <h1 className="title-enhanced text-xl text-gray-900">Open Home Optimizer</h1>
              <p className="subtitle-enhanced text-sm text-gray-500 hidden sm:block">AI-Powered Scheduling</p>
            </div>
          </div>
          
          <div className="hidden md:flex items-center space-x-4 animate-slideInRight">
            <div className="flex items-center space-x-2 text-sm text-gray-600 glass px-3 py-2 rounded-full">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span>Live Market Data</span>
            </div>
            
            {/* User Info */}
            <div className="flex items-center space-x-2 text-sm text-gray-600 glass px-3 py-2 rounded-full">
              <User className="w-4 h-4" />
              <span>Welcome, {user?.first_name || 'Agent'}</span>
            </div>
            
            <button 
              onClick={onLogout}
              className="text-gray-600 hover:text-gray-900 transition-all duration-300 px-4 py-2 rounded-lg hover:bg-white/20 glass flex items-center space-x-2"
            >
              <LogOut className="w-4 h-4" />
              <span>Sign Out</span>
            </button>
          </div>
          
          <button 
            className="md:hidden"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>
    </nav>

    <div className="container mx-auto px-6 py-8">
      {/* Hero Section */}
      <div className="text-center mb-12 animate-fadeInUp">
        <h2 className="title-enhanced text-4xl md:text-5xl text-gray-900 mb-4 animate-fadeInDown">
          Find Your <span className="gradient-text">Perfect</span> Open Home Time
        </h2>
        <p className="subtitle-enhanced text-xl text-gray-600 max-w-2xl mx-auto animate-fadeInUp">
          Leverage AI-powered market analysis to schedule open homes when competition is lowest and visibility is highest.
        </p>
        
        {/* Decorative elements */}
        <div className="flex justify-center mt-6 space-x-2">
          <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce"></div>
          <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce delay-100"></div>
          <div className="w-2 h-2 bg-pink-400 rounded-full animate-bounce delay-200"></div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid md:grid-cols-3 gap-6 mb-12">
        <div className="card-enhanced shadow-enhanced-hover p-6 animate-slideInLeft">
          <div className="flex items-center space-x-3 mb-4">
            <div className="bg-gradient-to-br from-green-500 to-emerald-600 w-12 h-12 rounded-xl flex items-center justify-center animate-pulse">
              <Target className="text-white w-6 h-6" />
            </div>
            <div>
              <h3 className="title-enhanced text-2xl gradient-text">85%</h3>
              <p className="subtitle-enhanced text-gray-600">Success Rate</p>
            </div>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 mt-4">
            <div className="bg-gradient-to-r from-green-500 to-emerald-600 h-2 rounded-full w-4/5 animate-pulse"></div>
          </div>
        </div>
        
        <div className="card-enhanced shadow-enhanced-hover p-6 animate-fadeInUp">
          <div className="flex items-center space-x-3 mb-4">
            <div className="bg-gradient-to-br from-blue-500 to-indigo-600 w-12 h-12 rounded-xl flex items-center justify-center animate-pulse delay-200">
              <BarChart3 className="text-white w-6 h-6" />
            </div>
            <div>
              <h3 className="title-enhanced text-2xl gradient-text">3.2x</h3>
              <p className="subtitle-enhanced text-gray-600">More Visitors</p>
            </div>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 mt-4">
            <div className="bg-gradient-to-r from-blue-500 to-indigo-600 h-2 rounded-full w-full animate-pulse delay-200"></div>
          </div>
        </div>
        
        <div className="card-enhanced shadow-enhanced-hover p-6 animate-slideInRight">
          <div className="flex items-center space-x-3 mb-4">
            <div className="bg-gradient-to-br from-purple-500 to-pink-600 w-12 h-12 rounded-xl flex items-center justify-center animate-pulse delay-400">
              <Zap className="text-white w-6 h-6" />
            </div>
            <div>
              <h3 className="title-enhanced text-2xl gradient-text">2min</h3>
              <p className="subtitle-enhanced text-gray-600">Analysis Time</p>
            </div>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 mt-4">
            <div className="bg-gradient-to-r from-purple-500 to-pink-600 h-2 rounded-full w-1/5 animate-pulse delay-400"></div>
          </div>
        </div>
      </div>

      {/* Main Form */}
      <div className="card-enhanced shadow-enhanced overflow-hidden animate-fadeInUp">
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-8 text-white relative overflow-hidden">
          {/* Decorative elements */}
          <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full blur-3xl"></div>
          <div className="absolute bottom-0 left-0 w-24 h-24 bg-white/5 rounded-full blur-2xl"></div>
          
          <h3 className="title-enhanced text-2xl mb-2 relative z-10">Schedule Your Open Home</h3>
          <p className="subtitle-enhanced text-indigo-100 relative z-10">Tell us about your property and we'll find the optimal times</p>
        </div>
        
        <div className="p-8">
          <div className="space-y-8">
            <div className="grid lg:grid-cols-1 xl:grid-cols-3 gap-8">
              {/* Property Details */}
              <div className="space-y-6">
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <MapPin className="w-5 h-5 mr-2 text-indigo-600" />
                    Property Details
                  </h4>
                </div>
                
                <div className="animate-slideInLeft">
                  <label className="block text-sm font-semibold text-gray-700 mb-3">Property Address</label>
                  <AddressAutocomplete
                    value={addressValue}
                    onChange={handleAddressChange}
                    className="input-enhanced text-lg shadow-enhanced"
                    placeholder="Start typing an address..."
                  />
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-3">
                      <Bed className="inline w-4 h-4 mr-1" />
                      Bedrooms
                    </label>
                    <select 
                      value={propertyData.bedrooms}
                      onChange={(e) => setPropertyData({...propertyData, bedrooms: parseInt(e.target.value)})}
                      className="w-full px-3 py-3 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all duration-300"
                    >
                      {[1,2,3,4,5,6].map(num => (
                        <option key={num} value={num}>{num}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-3">
                      <Bath className="inline w-4 h-4 mr-1" />
                      Bathrooms
                    </label>
                    <select 
                      value={propertyData.bathrooms}
                      onChange={(e) => setPropertyData({...propertyData, bathrooms: parseInt(e.target.value)})}
                      className="w-full px-3 py-3 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all duration-300"
                    >
                      {[1,2,3,4,5].map(num => (
                        <option key={num} value={num}>{num}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-3">
                      <Car className="inline w-4 h-4 mr-1" />
                      Car Spaces
                    </label>
                    <select 
                      value={propertyData.carSpots}
                      onChange={(e) => setPropertyData({...propertyData, carSpots: parseInt(e.target.value)})}
                      className="w-full px-3 py-3 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all duration-300"
                    >
                      {[0,1,2,3,4].map(num => (
                        <option key={num} value={num}>{num}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* Similar Property Criteria */}
              <div className="space-y-6">
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <Search className="w-5 h-5 mr-2 text-purple-600" />
                    Similar Property Criteria
                  </h4>
                </div>
                
                <div className="bg-gradient-to-r from-purple-50 to-indigo-50 border border-purple-200 rounded-xl p-3">
                  <p className="text-sm text-gray-600 mb-1">
                    Define your perception of similar properties to analyze competition more accurately
                  </p>
                  <div className="text-xs text-purple-700 font-medium">
                    💡 This helps identify properties that buyers might consider as alternatives
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-3">
                      <Bed className="inline w-4 h-4 mr-1" />
                      Similar Bedrooms
                    </label>
                    <select 
                      value={similarPropertyCriteria.bedrooms}
                      onChange={(e) => setSimilarPropertyCriteria({...similarPropertyCriteria, bedrooms: e.target.value})}
                      className="w-full px-3 py-3 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all duration-300"
                    >
                      <option value="1">Exactly 1</option>
                      <option value="2">Exactly 2</option>
                      <option value="3">Exactly 3</option>
                      <option value="4">Exactly 4</option>
                      <option value="5">Exactly 5</option>
                      <option value="6">Exactly 6</option>
                      <option value="1-2">1-2 bedrooms</option>
                      <option value="2-3">2-3 bedrooms</option>
                      <option value="3-4">3-4 bedrooms</option>
                      <option value="4-5">4-5 bedrooms</option>
                      <option value="5-6">5-6 bedrooms</option>
                      <option value="2+">2+ bedrooms</option>
                      <option value="3+">3+ bedrooms</option>
                      <option value="4+">4+ bedrooms</option>
                      <option value="5+">5+ bedrooms</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-3">
                      <Bath className="inline w-4 h-4 mr-1" />
                      Similar Bathrooms
                    </label>
                    <select 
                      value={similarPropertyCriteria.bathrooms}
                      onChange={(e) => setSimilarPropertyCriteria({...similarPropertyCriteria, bathrooms: e.target.value})}
                      className="w-full px-3 py-3 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all duration-300"
                    >
                      <option value="1">Exactly 1</option>
                      <option value="2">Exactly 2</option>
                      <option value="3">Exactly 3</option>
                      <option value="4">Exactly 4</option>
                      <option value="5">Exactly 5</option>
                      <option value="1-2">1-2 bathrooms</option>
                      <option value="2-3">2-3 bathrooms</option>
                      <option value="3-4">3-4 bathrooms</option>
                      <option value="4-5">4-5 bathrooms</option>
                      <option value="1+">1+ bathrooms</option>
                      <option value="2+">2+ bathrooms</option>
                      <option value="3+">3+ bathrooms</option>
                      <option value="4+">4+ bathrooms</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-3">
                      <Car className="inline w-4 h-4 mr-1" />
                      Similar Car Spaces
                    </label>
                    <select 
                      value={similarPropertyCriteria.carSpots}
                      onChange={(e) => setSimilarPropertyCriteria({...similarPropertyCriteria, carSpots: e.target.value})}
                      className="w-full px-3 py-3 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all duration-300"
                    >
                      <option value="0">Exactly 0</option>
                      <option value="1">Exactly 1</option>
                      <option value="2">Exactly 2</option>
                      <option value="3">Exactly 3</option>
                      <option value="4">Exactly 4</option>
                      <option value="0-1">0-1 spaces</option>
                      <option value="1-2">1-2 spaces</option>
                      <option value="2-3">2-3 spaces</option>
                      <option value="3-4">3-4 spaces</option>
                      <option value="1+">1+ spaces</option>
                      <option value="2+">2+ spaces</option>
                      <option value="3+">3+ spaces</option>
                    </select>
                  </div>
                </div>

                <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl p-4">
                  <div className="flex items-start space-x-3">
                    <div className="bg-green-500 w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                      <Target className="w-3 h-3 text-white" />
                    </div>
                    <div>
                      <h5 className="font-semibold text-green-900 text-sm">Smart Matching</h5>
                      <p className="text-green-700 text-sm mt-1">
                        These criteria help identify competing properties that buyers might consider as alternatives to yours. 
                        For example, if selling a 4-bedroom home, buyers might also look at "3-5" bedroom properties.
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Search Preferences */}
              <div className="space-y-6">
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <Filter className="w-5 h-5 mr-2 text-indigo-600" />
                    Search Preferences
                  </h4>
                </div>
                
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-3">Search Radius</label>
                  <select 
                    value={searchRadius}
                    onChange={(e) => setSearchRadius(parseInt(e.target.value))}
                    className="w-full px-4 py-4 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all duration-300 text-lg"
                  >
                    <option value={2}>2km radius - Immediate vicinity</option>
                    <option value={5}>5km radius - Local area</option>
                    <option value={10}>10km radius - Extended area</option>
                    <option value={15}>15km radius - Broad market</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-3">Preferred Time Window</label>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs text-gray-500 mb-2">Start Time</label>
                      <input 
                        type="time"
                        value={timeFilter.start}
                        onChange={(e) => setTimeFilter({...timeFilter, start: e.target.value})}
                        className="w-full px-3 py-3 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all duration-300"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-500 mb-2">End Time</label>
                      <input 
                        type="time"
                        value={timeFilter.end}
                        onChange={(e) => setTimeFilter({...timeFilter, end: e.target.value})}
                        className="w-full px-3 py-3 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all duration-300"
                      />
                    </div>
                  </div>
                </div>

                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-4">
                  <div className="flex items-start space-x-3">
                    <div className="bg-blue-500 w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                      <Clock className="w-3 h-3 text-white" />
                    </div>
                    <div>
                      <h5 className="font-semibold text-blue-900 text-sm">Smart Tip</h5>
                      <p className="text-blue-700 text-sm mt-1">
                        Weekend mornings (9-11 AM) typically have the highest foot traffic, while early afternoons (2-4 PM) often have less competition.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex justify-center pt-6">
              <button 
                onClick={handlePropertySubmit}
                disabled={loading || !addressValue.trim()}
                className="btn-primary px-12 py-4 text-lg shadow-enhanced-hover disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center space-x-3 animate-fadeInUp"
              >
                {loading ? (
                  <>
                    <div className="loading-dots">
                      <div></div>
                      <div></div>
                      <div></div>
                      <div></div>
                    </div>
                    <span>Analyzing Market Data...</span>
                  </>
                ) : (
                  <>
                    <TrendingUp className="w-5 h-5 animate-float" />
                    <span>Find Optimal Times</span>
                    <ArrowRight className="w-5 h-5 animate-float delay-200" />
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
);

const ResultsView = ({ 
  addressValue, 
  searchRadius, 
  recommendations, 
  currentIndex, 
  setCurrentIndex, 
  setSelectedTimeSlot, 
  setCurrentView, 
  user,
  onLogout, 
  mockOpenHomes, 
  getCompetitionColor, 
  getCompetitionGradient 
}) => (
  <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
    <nav className="bg-white/90 backdrop-blur-xl shadow-sm border-b border-gray-200/50 sticky top-0 z-50">
      <div className="container mx-auto px-6 py-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <div className="bg-gradient-to-br from-indigo-600 to-purple-600 w-10 h-10 rounded-xl flex items-center justify-center">
              <Home className="text-white w-6 h-6" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Open Home Optimizer</h1>
              <p className="text-sm text-gray-500 hidden sm:block">Analysis Complete</p>
            </div>
          </div>
          
          <div className="flex space-x-4">
            <button 
              onClick={() => setCurrentView('dashboard')}
              className="bg-indigo-600 text-white px-6 py-2 rounded-xl hover:bg-indigo-700 transition-colors duration-200 flex items-center space-x-2"
            >
              <Search className="w-4 h-4" />
              <span>New Search</span>
            </button>
            <button 
              onClick={onLogout}
              className="text-gray-600 hover:text-gray-900 transition-colors duration-200 px-4 py-2 rounded-lg hover:bg-gray-100 flex items-center space-x-2"
            >
              <LogOut className="w-4 h-4" />
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      </div>
    </nav>

    <div className="container mx-auto px-6 py-8">
      {/* Header */}
      <div className="text-center mb-12">
        <div className="inline-flex items-center space-x-2 bg-green-100 text-green-800 px-4 py-2 rounded-full text-sm font-semibold mb-4">
          <CheckCircle className="w-4 h-4" />
          <span>Analysis Complete</span>
        </div>
        <h2 className="text-4xl font-bold text-gray-900 mb-4">
          Optimal Time <span className="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">Recommendations</span>
        </h2>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Analysis for <span className="font-semibold text-indigo-600">{addressValue}</span> within {searchRadius}km radius
        </p>
        <div className="mt-4 inline-flex items-center space-x-2 bg-blue-100 text-blue-800 px-4 py-2 rounded-full text-sm font-medium">
          <Search className="w-4 h-4" />
          <span>Analyzing similar properties with your criteria</span>
        </div>
      </div>

      {/* Interactive Timeline */}
      {recommendations.length > 0 && (
        <div className="bg-white rounded-2xl p-6 mb-8 shadow-lg border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
            <Clock className="w-5 h-5 mr-2 text-indigo-600" />
            Interactive Timeline
          </h3>
          
          <div className="relative">
            {/* Timeline Line */}
            <div className="absolute top-6 left-0 right-0 h-1 bg-gradient-to-r from-indigo-200 via-purple-200 to-indigo-200 rounded-full"></div>
            
            {/* Timeline Points */}
            <div className="flex justify-between items-center relative">
              {recommendations.map((slot, index) => {
                const isSelected = currentIndex === index;
                const isRecommended = index < 3; // Top 3 recommendations
                
                return (
                  <div
                    key={index}
                    className="flex flex-col items-center cursor-pointer transform transition-all duration-300 hover:scale-110"
                    onClick={() => {
                      setCurrentIndex(index);
                      setSelectedTimeSlot(recommendations[index]);
                    }}
                  >
                    {/* Timeline Point */}
                    <div className={`w-4 h-4 rounded-full border-4 transition-all duration-300 ${
                      isSelected 
                        ? 'bg-indigo-600 border-indigo-200 shadow-lg scale-150' 
                        : isRecommended 
                          ? 'bg-green-500 border-green-200 hover:bg-green-600' 
                          : 'bg-gray-400 border-gray-200 hover:bg-gray-500'
                    }`}></div>
                    
                    {/* Time Label */}
                    <div className={`mt-3 text-sm font-medium transition-colors duration-300 ${
                      isSelected 
                        ? 'text-indigo-600' 
                        : isRecommended 
                          ? 'text-green-600' 
                          : 'text-gray-600'
                    }`}>
                      {slot.time}
                    </div>
                    
                    {/* Competition Badge */}
                    <div className={`mt-1 px-2 py-1 rounded-full text-xs font-bold transition-all duration-300 ${
                      isSelected 
                        ? 'bg-indigo-100 text-indigo-700 border border-indigo-300' 
                        : slot.competition === 'low' 
                          ? 'bg-green-100 text-green-700' 
                          : slot.competition === 'medium' 
                            ? 'bg-yellow-100 text-yellow-700' 
                            : 'bg-red-100 text-red-700'
                    }`}>
                      {slot.count}
                    </div>
                    
                    {/* Recommended Badge */}
                    {isRecommended && (
                      <div className="mt-1 text-xs text-green-600 font-bold">
                        {index === 0 ? '🥇 BEST' : index === 1 ? '🥈 GOOD' : '🥉 OK'}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
            
            {/* Selected Slot Details */}
            {currentIndex !== null && recommendations[currentIndex] && (
              <div className="mt-8 p-6 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl border border-indigo-200">
                <div className="grid md:grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-indigo-600">
                      {recommendations[currentIndex].time}
                    </div>
                    <div className="text-sm text-gray-600">Selected Time</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">
                      {recommendations[currentIndex].count}
                    </div>
                    <div className="text-sm text-gray-600">Competing Opens</div>
                  </div>
                  <div className="text-center">
                    <div className={`text-lg font-bold ${
                      recommendations[currentIndex].competition === 'low' ? 'text-green-600' :
                      recommendations[currentIndex].competition === 'medium' ? 'text-yellow-600' :
                      'text-red-600'
                    }`}>
                      {recommendations[currentIndex].competition.replace('-', ' ').toUpperCase()}
                    </div>
                    <div className="text-sm text-gray-600">Competition Level</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      <div className="grid xl:grid-cols-3 gap-8">
        {/* Timeline Visualization */}
        <div className="xl:col-span-2 bg-white rounded-3xl shadow-xl border border-gray-100 overflow-hidden">
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-6 text-white">
            <h3 className="text-xl font-bold flex items-center">
              <Clock className="w-6 h-6 mr-3" />
              Competition Timeline
            </h3>
            <p className="text-indigo-100 mt-1">30-minute intervals showing market competition</p>
          </div>
          
          <div className="p-6 space-y-3">
            {mockOpenHomes.map((slot, index) => (
              <div key={index} className="group hover:bg-gray-50 transition-all duration-200 p-4 rounded-xl border border-gray-100">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="text-lg font-bold text-gray-900 w-20">{slot.time}</div>
                    <div className="flex-1 bg-gray-200 rounded-full h-3 w-48 relative overflow-hidden">
                      <div 
                        className={`h-3 rounded-full bg-gradient-to-r ${getCompetitionGradient(slot.competition)} transition-all duration-1000 delay-${index * 100}`}
                        style={{width: `${Math.min((slot.count / 20) * 100, 100)}%`}}
                      ></div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="text-right">
                      <div className="text-sm font-semibold text-gray-900">{slot.count} open homes</div>
                      <div className="text-xs text-gray-500">in your area</div>
                    </div>
                    <span className={`px-3 py-1.5 rounded-full text-xs font-bold border ${getCompetitionColor(slot.competition)}`}>
                      {slot.competition.replace('-', ' ').toUpperCase()}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recommendations Sidebar */}
        <div className="space-y-6">
          {/* Top Recommendations */}
          <div className="bg-white rounded-3xl shadow-xl border border-gray-100 overflow-hidden">
            <div className="bg-gradient-to-r from-green-600 to-emerald-600 p-6 text-white">
              <h3 className="text-xl font-bold flex items-center">
                <Star className="w-6 h-6 mr-3" />
                Best Times
              </h3>
              <p className="text-green-100 mt-1">Ranked by opportunity</p>
            </div>
            
            <div className="p-6 space-y-4">
              {recommendations.slice(0, 3).map((slot, index) => (
                <div key={index} className={`relative p-5 rounded-2xl border-2 transition-all duration-300 hover:shadow-lg ${
                  index === 0 
                    ? 'border-green-300 bg-gradient-to-r from-green-50 to-emerald-50' 
                    : 'border-gray-200 hover:border-indigo-300'
                }`}>
                  {index === 0 && (
                    <div className="absolute -top-2 -right-2 bg-gradient-to-r from-green-500 to-emerald-600 text-white text-xs font-bold px-3 py-1 rounded-full">
                      BEST
                    </div>
                  )}
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      {index === 0 && <CheckCircle className="w-5 h-5 text-green-600" />}
                      <span className="text-xl font-bold text-gray-900">{slot.time}</span>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-bold border ${getCompetitionColor(slot.competition)}`}>
                      {slot.competition.replace('-', ' ')}
                    </span>
                  </div>
                  <div className="text-sm text-gray-600 mb-2">
                    Only <span className="font-semibold text-gray-900">{slot.count}</span> competing open homes
                  </div>
                  <div className="text-xs text-gray-500">
                    {index === 0 ? '🎯 Minimal competition - highest visibility potential' :
                     index === 1 ? '✨ Low competition - great visitor turnout expected' :
                     '👍 Good option with moderate competition'}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Market Insights */}
          <div className="bg-white rounded-3xl shadow-xl border border-gray-100 overflow-hidden">
            <div className="bg-gradient-to-r from-purple-600 to-pink-600 p-6 text-white">
              <h3 className="text-xl font-bold flex items-center">
                <BarChart3 className="w-6 h-6 mr-3" />
                Market Insights
              </h3>
            </div>
            
            <div className="p-6 space-y-6">
              <div className="text-center">
                <div className="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">85%</div>
                <div className="text-sm text-gray-600 mt-1">Peak hours avoided</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">3.2x</div>
                <div className="text-sm text-gray-600 mt-1">Higher visibility potential</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">12</div>
                <div className="text-sm text-gray-600 mt-1">Similar properties nearby</div>
              </div>
            </div>
          </div>

          {/* Pro Tips */}
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-3xl p-6">
            <div className="flex items-start space-x-3">
              <div className="bg-gradient-to-br from-blue-500 to-indigo-600 w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0">
                <Zap className="w-4 h-4 text-white" />
              </div>
              <div>
                <h4 className="font-bold text-blue-900 mb-2">Pro Strategy</h4>
                <p className="text-blue-700 text-sm leading-relaxed">
                  Consider booking multiple 30-minute slots during low-competition times to maximize exposure. This strategy can increase your visitor count by up to 40%.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Additional Insights Section */}
      <div className="mt-12 grid md:grid-cols-2 gap-8">
        {/* Detailed Analysis */}
        <div className="bg-white rounded-3xl shadow-xl border border-gray-100 p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
            <Target className="w-6 h-6 mr-3 text-indigo-600" />
            Detailed Analysis
          </h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-4 bg-gray-50 rounded-xl">
              <span className="text-gray-700">Best performing time slot</span>
              <span className="font-bold text-green-600">{recommendations[0]?.time}</span>
            </div>
            <div className="flex justify-between items-center p-4 bg-gray-50 rounded-xl">
              <span className="text-gray-700">Average competition level</span>
              <span className="font-bold text-orange-600">High</span>
            </div>
            <div className="flex justify-between items-center p-4 bg-gray-50 rounded-xl">
              <span className="text-gray-700">Recommended booking window</span>
              <span className="font-bold text-indigo-600">60 minutes</span>
            </div>
            <div className="flex justify-between items-center p-4 bg-gray-50 rounded-xl">
              <span className="text-gray-700">Expected visitor increase</span>
              <span className="font-bold text-purple-600">+220%</span>
            </div>
          </div>
        </div>

        {/* Market Trends */}
        <div className="bg-white rounded-3xl shadow-xl border border-gray-100 p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
            <TrendingUp className="w-6 h-6 mr-3 text-green-600" />
            Market Trends
          </h3>
          <div className="space-y-4">
            <div className="p-4 bg-green-50 border border-green-200 rounded-xl">
              <div className="flex items-center space-x-2 mb-2">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="font-semibold text-green-800">Low Competition Window</span>
              </div>
              <p className="text-green-700 text-sm">9:00 AM - 9:30 AM shows consistently low competition</p>
            </div>
            
            <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl">
              <div className="flex items-center space-x-2 mb-2">
                <div className="w-3 h-3 bg-amber-500 rounded-full"></div>
                <span className="font-semibold text-amber-800">Peak Hours</span>
              </div>
              <p className="text-amber-700 text-sm">11:00 AM - 1:00 PM has highest competition levels</p>
            </div>
            
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-xl">
              <div className="flex items-center space-x-2 mb-2">
                <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                <span className="font-semibold text-blue-800">Sweet Spot</span>
              </div>
              <p className="text-blue-700 text-sm">2:30 PM - 3:30 PM offers good balance of traffic vs. competition</p>
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="mt-12 text-center">
        <div className="bg-white rounded-3xl shadow-xl border border-gray-100 p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">Ready to Schedule?</h3>
          <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
            Based on our analysis, we recommend booking your open home during the highlighted time slots for maximum visibility and minimal competition.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-gradient-to-r from-green-600 to-emerald-600 text-white px-8 py-4 rounded-2xl font-semibold text-lg hover:from-green-700 hover:to-emerald-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5">
              Book Recommended Time
            </button>
            <button 
              onClick={() => setCurrentView('dashboard')}
              className="border-2 border-indigo-600 text-indigo-600 px-8 py-4 rounded-2xl font-semibold text-lg hover:bg-indigo-600 hover:text-white transition-all duration-300"
            >
              Try Different Property
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
);

// Main App component with authentication
const App = () => {
  return (
    <AuthProvider>
      <AuthenticatedApp />
    </AuthProvider>
  );
};

export default App;