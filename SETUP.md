# EstateHub - Setup & Configuration Guide

## Step 1: Environment Setup

### 1.1 Install Python Dependencies
Open a terminal in the project root folder and run:

```bash
pip install -r requirements.txt
```

### 1.2 Configure Environment Variables
Copy `.env.example` to `.env` and update with your local configuration:

```bash
# Copy the template
cp .env.example .env
```

Edit `.env`:
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=estate
DB_PORT=3306

FLASK_ENV=development
FLASK_DEBUG=True

JWT_SECRET=your_super_secret_key_change_this
JWT_ALGORITHM=HS256
JWT_EXPIRY_MINUTES=1440

API_HOST=0.0.0.0
API_PORT=5001
```

### 1.3 Create MySQL Database

If MySQL is not running, start it first:
- **Windows**: Use MySQL Workbench or `mysql` CLI
- **Mac/Linux**: `brew services start mysql` or equivalent

Create the database and tables:

```bash
# Option A: Using MySQL CLI
mysql -u root -p < flask/db.sql

# Option B: From Python shell
python
>>> from db import init_db
>>> init_db()
>>> exit()
```

Verify the database was created:
```bash
mysql -u root -p
> SHOW DATABASES;
> USE estate;
> SHOW TABLES;
```

---

## Step 2: Start the API Server

From the project root folder:

```bash
python flask/app.py
```

You should see:
```
WARNING in app.runserver?
 * Running on http://0.0.0.0:5001
 * Debug mode: on
```

The API is now running at `http://localhost:5001`

---

## Step 3: Test the API

### 3.1 Check if API is running
Open your browser or Postman:
- `GET http://localhost:5001` → `{"message":"Real Estate API is running"}`

### 3.2 API Endpoints
```
GET    /api/properties           - List all properties
GET    /api/properties/<id>      - Get a specific property
POST   /api/properties           - Create property (requires auth + image upload)
PUT    /api/properties/<id>      - Update property (requires auth)
DELETE /api/properties/<id>      - Delete property (requires auth)

POST   /api/auth/register        - Register new user
POST   /api/auth/login           - Login user
```

### 3.3 Test Register & Login

**Register:**
```bash
curl -X POST http://localhost:5001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","email":"john@example.com","password":"password123"}'
```

Response:
```json
{
  "message": "User registered successfully",
  "email": "john@example.com"
}
```

**Login:**
```bash
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com","password":"password123"}'
```

Response:
```json
{
  "message": "Login successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "john@example.com",
    "name": "John Doe"
  }
}
```

### 3.4 Test Get Properties
```bash
curl http://localhost:5001/api/properties
```

Response: `[]` (empty list initially)

---

## Step 4: Connect React Native to Local API

### 4.1 Find Your Computer's IP Address

**Windows:**
```bash
ipconfig
```
Look for `IPv4 Address` (e.g., `192.168.1.10`)

**Mac/Linux:**
```bash
ifconfig
# or
ip addr
```
Look for `192.168.x.x`

### 4.2 Update React Native Config

Create or update `src/config.js`:

```javascript
export const API_BASE_URL = 'http://192.168.1.10:5001'; // Replace with YOUR IP
```

Update `App.js` to use the config:

```javascript
import { API_BASE_URL } from './src/config';

// Example API call
const testConnection = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/properties`);
    const data = await response.json();
    console.log('Properties:', data);
  } catch (error) {
    console.error('API Error:', error);
  }
};
```

### 4.3 Emulator / Device Access

| Target | URL |
|--------|-----|
| iOS Simulator | `http://localhost:5001` |
| Android Emulator | `http://10.0.2.2:5001` |
| Physical Device (same Wi-Fi) | `http://192.168.1.10:5001` |

**For simplicity, use your computer's IP (192.168.x.x) for all**

### 4.4 Test Connection from React Native

```javascript
const testAPI = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/properties`);
    const data = await response.json();
    console.log('Success:', data);
  } catch (error) {
    console.error('Failed:', error);
  }
};
```

### 4.5 Enable Cleartext Traffic (Android Only)

If you get network errors on Android (API uses HTTP, not HTTPS):

Edit `android/app/src/main/AndroidManifest.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.estatehub">
    
    <!-- Add android:usesCleartextTraffic="true" -->
    <application
        android:usesCleartextTraffic="true">
        <!-- ... rest of config ... -->
    </application>
</manifest>
```

> ⚠️ **For development only!** Never use this in production.

---

## Step 5: Authentication Flow (JWT)

### 5.1 Login Function

```javascript
const login = async (email, password) => {
  try {
    const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    
    const data = await res.json();
    
    if (res.ok) {
      await AsyncStorage.setItem('token', data.access_token);
      await AsyncStorage.setItem('user', JSON.stringify(data.user));
      return data.user;
    } else {
      throw new Error(data.error);
    }
  } catch (error) {
    console.error('Login failed:', error);
    throw error;
  }
};
```

### 5.2 Authenticated API Calls

```javascript
const authFetch = async (url, options = {}) => {
  const token = await AsyncStorage.getItem('token');
  
  return fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  });
};

// Usage
const getProperties = async () => {
  const response = await authFetch(`${API_BASE_URL}/api/properties`);
  return response.json();
};
```

### 5.3 Token Refresh (Optional)

```javascript
const logout = async () => {
  await AsyncStorage.removeItem('token');
  await AsyncStorage.removeItem('user');
};

const getStoredUser = async () => {
  const userJson = await AsyncStorage.getItem('user');
  return userJson ? JSON.parse(userJson) : null;
};
```

---

## Step 6: Image Upload & Display

### 6.1 Upload Property with Images

```javascript
const createProperty = async (formData) => {
  const token = await AsyncStorage.getItem('token');
  
  const res = await fetch(`${API_BASE_URL}/api/properties`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      // DO NOT set Content-Type – fetch will set it with boundary
    },
    body: formData,
  });
  
  return res.json();
};

// Build FormData with image from react-native-image-picker
const submitProperty = async (image) => {
  const formData = new FormData();
  formData.append('title', 'Beautiful House');
  formData.append('price', 250000);
  formData.append('city', 'New York');
  formData.append('description', 'Spacious 3BR house');
  formData.append('address', '123 Main St');
  formData.append('bedrooms', 3);
  formData.append('bathrooms', 2);
  formData.append('area', 2500);
  formData.append('property_type', 'house');
  formData.append('status', 'available');
  
  // Add image file
  formData.append('files', {
    uri: image.uri,
    type: image.type,   // e.g., 'image/jpeg'
    name: image.fileName,
  });
  
  try {
    const result = await createProperty(formData);
    console.log('Property created:', result);
  } catch (error) {
    console.error('Upload failed:', error);
  }
};
```

### 6.2 Display Images

Images are stored at `/uploads/properties/filename.jpg`

```javascript
const imageUrl = `${API_BASE_URL}/uploads/properties/filename.jpg`;

// In React Native:
<Image
  source={{ uri: imageUrl }}
  style={{ width: 200, height: 200 }}
/>
```

### 6.3 Serve Static Files

Update `flask/app.py` to serve images:

```python
from flask import Flask, send_from_directory

app = Flask(__name__)

# Serve static files
@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
    return send_from_directory('uploads', filename)
```

---

## Step 7: CORS Configuration

CORS is already enabled in `flask/app.py`:

```python
from flask_cors import CORS
CORS(app)  # Allow all origins
```

If you still get CORS errors, ensure:
1. ✅ Server runs with `--host 0.0.0.0` (it does by default)
2. ✅ CORS middleware is initialized before routes
3. ✅ Front-end makes requests to correct API URL

---

## Common Issues & Fixes

| Problem | Solution |
|---------|----------|
| `Network request failed` | Check IP address, firewall, Wi-Fi network, Android cleartext traffic |
| `CORS error` | Confirm server runs with `--host 0.0.0.0` and CORS is enabled |
| `401 Unauthorized` | Token missing or expired – login again |
| `Cannot POST /properties` | Make sure token is in `Authorization: Bearer <token>` header |
| `Image upload fails` | Use `FormData`, NOT JSON; ensure `files` field is present |
| `Images not showing` | Check `/uploads/properties/` folder exists and URL is correct |
| `Database connection error` | Check MySQL is running, credentials in `.env` are correct |
| `Module not found: db` | Ensure `db.py` is in project root (not in `flask/`) |

---

## Project Structure

```
EstateHub/
├── flask/
│   ├── app.py              # Flask main app
│   └── db.sql              # Database schema
├── routes/
│   ├── auth.py             # Authentication routes
│   └── properties.py       # Property CRUD routes
├── App.js                  # React Native entry point
├── index.js                # Expo entry point
├── package.json            # NPM dependencies
├── requirements.txt        # Python dependencies
├── db.py                   # Database connection module
├── .env.example            # Environment template
└── uploads/
    └── properties/         # Property images directory
```

---

## Next Steps

1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Create `.env` from `.env.example` and configure
3. ✅ Create database: `mysql -u root -p < flask/db.sql`
4. ✅ Start API: `python flask/app.py`
5. ✅ Update React Native config with your IP
6. ✅ Test endpoints with Postman or curl
7. ✅ Build authentication UI in React Native
8. ✅ Build property listing & upload screens

---

## Quick Reference - API URLs

```
Base URL: http://192.168.1.10:5001

Health Check:
GET /

Auth:
POST /api/auth/register
POST /api/auth/login

Properties:
GET    /api/properties
GET    /api/properties/{id}
POST   /api/properties (requires auth)
PUT    /api/properties/{id} (requires auth)
DELETE /api/properties/{id} (requires auth)

Static Files:
GET /uploads/properties/{filename}
```
