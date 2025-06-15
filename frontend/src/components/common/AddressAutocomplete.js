import React, { useEffect, useRef, useState } from 'react';
import { MapPin } from 'lucide-react';

const AddressAutocomplete = ({ value, onChange, placeholder, className }) => {
  const inputRef = useRef(null);
  const autocompleteRef = useRef(null);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    const loadGoogleMapsAPI = () => {
      // Check if already loaded
      if (window.google && window.google.maps && window.google.maps.places) {
        setIsLoaded(true);
        initializeAutocomplete();
        return;
      }

      // Check if script is already loading
      if (document.querySelector('script[src*="maps.googleapis.com"]')) {
        const handleGoogleLoad = () => {
          setIsLoaded(true);
          initializeAutocomplete();
        };
        window.addEventListener('google-places-loaded', handleGoogleLoad);
        return () => window.removeEventListener('google-places-loaded', handleGoogleLoad);
      }

      // Load Google Maps API
      const script = document.createElement('script');
      script.src = `https://maps.googleapis.com/maps/api/js?key=${process.env.REACT_APP_GOOGLE_PLACES_API_KEY}&libraries=places&callback=initGooglePlaces`;
      script.async = true;
      script.defer = true;
      
      script.onload = () => {
        console.log('Google Maps API loaded successfully');
      };
      
      script.onerror = () => {
        console.error('Failed to load Google Maps API');
        setIsLoaded(false);
      };

      // Global error handler for Google Maps
      window.gm_authFailure = () => {
        console.error('Google Maps API Key Error: Please check your API key and billing');
        setIsLoaded(false);
      };

      const handleGoogleLoad = () => {
        setIsLoaded(true);
        initializeAutocomplete();
      };
      
      window.addEventListener('google-places-loaded', handleGoogleLoad);
      document.head.appendChild(script);
      
      return () => {
        window.removeEventListener('google-places-loaded', handleGoogleLoad);
      };
    };

    loadGoogleMapsAPI();
  }, []);

  const initializeAutocomplete = () => {
    if (!inputRef.current || !window.google) return;

    // Create autocomplete instance
    autocompleteRef.current = new window.google.maps.places.Autocomplete(
      inputRef.current,
      {
        types: ['address'],
        componentRestrictions: { country: 'au' }, // Restrict to Australia
        fields: ['formatted_address', 'geometry', 'address_components']
      }
    );

    // Add place changed listener
    autocompleteRef.current.addListener('place_changed', () => {
      const place = autocompleteRef.current.getPlace();
      
      if (place && place.formatted_address) {
        onChange({
          target: {
            value: place.formatted_address
          }
        });
      }
    });
  };

  const handleInputChange = (e) => {
    onChange(e);
  };

  const handleKeyDown = (e) => {
    // Prevent form submission when selecting from dropdown
    if (e.key === 'Enter' && document.querySelector('.pac-container:not([style*="display: none"])')) {
      e.preventDefault();
    }
  };

  return (
    <div className="relative">
      <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
        <MapPin className="h-5 w-5 text-gray-400" />
      </div>
      <input
        ref={inputRef}
        type="text"
        value={value}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        className={`pl-12 ${className}`}
        placeholder={placeholder}
        autoComplete="off"
      />
      {!isLoaded && (
        <div className="absolute inset-y-0 right-0 pr-4 flex items-center">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-indigo-600"></div>
        </div>
      )}
    </div>
  );
};

export default AddressAutocomplete;