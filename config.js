/**
 * EstateHub API Configuration
 * 
 * Update API_BASE_URL with your computer's IP address
 * Windows: Run 'ipconfig' in terminal to find IPv4 Address
 * Mac/Linux: Run 'ifconfig' or 'ip addr'
 * 
 * For local development: http://localhost:5001
 * For physical devices: http://192.168.x.x:5001 (use your actual IP)
 */

// Replace 'your-ip' with your actual computer IP address
export const API_BASE_URL = 'http://192.168.1.193:5001';

export const API_ENDPOINTS = {
  // Health
  health: () => `${API_BASE_URL}/`,
  
  // Authentication
  register: () => `${API_BASE_URL}/api/auth/register`,
  login: () => `${API_BASE_URL}/api/auth/login`,
  
  // Properties
  properties: () => `${API_BASE_URL}/api/properties`,
  property: (id) => `${API_BASE_URL}/api/properties/${id}`,
  
  // Uploads
  uploadImage: (filename) => `${API_BASE_URL}/uploads/properties/${filename}`,
};

export const API_TIMEOUT = 30000; // 30 seconds
