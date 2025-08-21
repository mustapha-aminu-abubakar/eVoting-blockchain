import React, { useState } from 'react';
// STEP 1: ADD YOUR IMAGE IMPORT HERE
import backgroundImage from '../assets/3D geometric crystalline background.png';

const SignIn = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    rememberMe: false
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Sign in data:', formData);
    // Handle sign in logic here
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col lg:flex-row">
      {/* Mobile Logo - Only visible on mobile */}
      <div className="lg:hidden bg-gradient-to-r from-gray-900 to-black py-6 px-4">
        <div className="flex items-center justify-center space-x-1">
          <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center">
            <svg className="w-5 h-5 text-black" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
          </div>
          <span className="text-2xl font-bold text-white">ote</span>
          <div className="w-6 h-6 border-2 border-white rounded-md flex items-center justify-center">
            <div className="w-3 h-3 bg-white rounded-sm"></div>
          </div>
          <span className="text-2xl font-bold text-white">ow</span>
        </div>
      </div>

      {/* Left Side - Background Image with Logo */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden">
        {/* Background Image Section */}
        <div 
          className="absolute inset-0 bg-cover bg-center bg-no-repeat"
          style={{
            // STEP 2: REPLACE THIS WITH YOUR IMPORTED IMAGE
             backgroundImage: 'url("3D geometric crystalline background.png")',
            
            // TEMPORARY: Using gradient until you add your image
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            backgroundColor: '#1f2937'
          }}
        >
          {/* Dark overlay for better text contrast */}
          <div className="absolute inset-0 bg-black bg-opacity-40"></div>
        </div>

        {/* Logo overlay on the image */}
        <div className="relative z-10 flex items-center justify-center w-full h-full">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-1 mb-4">
              <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center shadow-lg">
                <svg className="w-7 h-7 text-black" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              </div>
              <span className="text-4xl font-bold text-white drop-shadow-lg">ote</span>
              <div className="w-10 h-10 border-3 border-white rounded-md flex items-center justify-center shadow-lg">
                <div className="w-5 h-5 bg-white rounded-sm"></div>
              </div>
              <span className="text-4xl font-bold text-white drop-shadow-lg">ow</span>
            </div>
          </div>
        </div>
      </div>

      {/* Right Side - Sign In Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-4 lg:p-8">
        <div className="max-w-md w-full">
          <div className="text-center mb-6 lg:mb-8">
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-3 lg:mb-4">Welcome Back</h2>
            <p className="text-gray-600 text-sm lg:text-base">Enter your email and password to access your account</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="Enter your email"
                className="w-full px-4 py-3 lg:py-4 bg-gray-200 border-0 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white placeholder-gray-500 text-base"
                required
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Enter your email"
                className="w-full px-4 py-3 lg:py-4 bg-gray-200 border-0 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white placeholder-gray-500 text-base"
                required
              />
            </div>

            {/* Remember Me and Forgot Password */}
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="rememberMe"
                  name="rememberMe"
                  checked={formData.rememberMe}
                  onChange={handleChange}
                  className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2"
                />
                <label htmlFor="rememberMe" className="ml-2 text-sm text-gray-700">
                  Remember me
                </label>
              </div>
              <a href="/forgot-password" className="text-sm text-gray-700 hover:text-black hover:underline">
                Forgot Password
              </a>
            </div>

            <button
              type="submit"
              className="w-full bg-black text-white py-3 lg:py-4 rounded-lg font-medium text-base lg:text-lg hover:bg-gray-800 transition duration-200"
            >
              Sign In
            </button>

            <p className="text-center text-gray-600 text-sm lg:text-base">
              Don't have an account?{' '}
              <a href="/signup" className="text-black font-medium hover:underline">
                Sign Up
              </a>
            </p>
          </form>
        </div>
      </div>
    </div>
  );
};

export default SignIn;