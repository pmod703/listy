/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      fontFamily: {
        'inter': ['Inter', 'sans-serif'],
        'poppins': ['Poppins', 'sans-serif'],
      },
      animation: {
        'fadeInUp': 'fadeInUp 0.6s ease-out',
        'fadeInDown': 'fadeInDown 0.6s ease-out',
        'slideInLeft': 'slideInLeft 0.6s ease-out',
        'slideInRight': 'slideInRight 0.6s ease-out',
        'float': 'float 3s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite',
        'shimmer': 'shimmer 2s linear infinite',
      },
      keyframes: {
        fadeInUp: {
          '0%': {
            opacity: '0',
            transform: 'translateY(30px)'
          },
          '100%': {
            opacity: '1',
            transform: 'translateY(0)'
          }
        },
        fadeInDown: {
          '0%': {
            opacity: '0',
            transform: 'translateY(-30px)'
          },
          '100%': {
            opacity: '1',
            transform: 'translateY(0)'
          }
        },
        slideInLeft: {
          '0%': {
            opacity: '0',
            transform: 'translateX(-50px)'
          },
          '100%': {
            opacity: '1',
            transform: 'translateX(0)'
          }
        },
        slideInRight: {
          '0%': {
            opacity: '0',
            transform: 'translateX(50px)'
          },
          '100%': {
            opacity: '1',
            transform: 'translateX(0)'
          }
        },
        float: {
          '0%, 100%': {
            transform: 'translateY(0px)'
          },
          '50%': {
            transform: 'translateY(-10px)'
          }
        },
        glow: {
          '0%, 100%': {
            boxShadow: '0 0 20px rgba(102, 126, 234, 0.3)'
          },
          '50%': {
            boxShadow: '0 0 30px rgba(102, 126, 234, 0.6)'
          }
        },
        shimmer: {
          '0%': {
            backgroundPosition: '-200px 0'
          },
          '100%': {
            backgroundPosition: 'calc(200px + 100%) 0'
          }
        }
      },
      backdropBlur: {
        xs: '2px',
      },
      colors: {
        primary: {
          50: '#f0f4ff',
          500: '#667eea',
          600: '#5a67d8',
          700: '#4c51bf',
        }
      }
    },
  },
  plugins: [],
}