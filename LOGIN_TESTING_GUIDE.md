# 🔐 Login Testing Guide - IT Helpdesk System

## 📍 Login URLs and Endpoints

### API Login Endpoint
**URL:** `http://localhost:8000/login`
**Method:** POST
**Content-Type:** application/json

### Web Interface URLs
- **Chat Interface:** http://localhost:8501 (login via API first)
- **Dashboard:** http://localhost:8502 (login via API first)
- **API Documentation:** http://localhost:8000/docs (interactive testing)

## 👥 Test User Accounts

### Regular User Account
```json
{
  "username": "appuser",
  "password": "password123",
  "role": "user",
  "permissions": [
    "chat with agents",
    "view own tickets", 
    "access analytics"
  ]
}
```

### Support Engineer Account
```json
{
  "username": "support-engineer", 
  "password": "support123",
  "role": "support-engineer",
  "permissions": [
    "chat with agents",
    "view ALL tickets",
    "update ticket status", 
    "assign tickets",
    "access admin features"
  ]
}
```

## 🧪 Manual Login Testing

### 1. Test Regular User Login

**Step 1: Login via cURL**
```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "appuser",
    "password": "password123"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "appuser",
    "role": "user",
    "full_name": "Application User",
    "email": "appuser@example.com",
    "is_active": true,
    "last_login": "2024-01-XX"
  }
}
```

**Step 2: Verify User Details**
```bash
# Replace YOUR_TOKEN with the access_token from login response
curl -X GET http://localhost:8000/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Step 3: Test User Permissions**
```bash
# Should work - chat access
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "content": "My computer wont start",
    "user_id": "appuser"
  }'

# Should work - analytics access
curl -X GET http://localhost:8000/analytics/dashboard \
  -H "Authorization: Bearer YOUR_TOKEN"

# Should FAIL - support-only endpoint
curl -X GET http://localhost:8000/tickets/all \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. Test Support Engineer Login

**Step 1: Login via cURL**
```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "support-engineer",
    "password": "support123"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer", 
  "user": {
    "id": 2,
    "username": "support-engineer",
    "role": "support-engineer",
    "full_name": "Support Engineer",
    "email": "support@example.com",
    "is_active": true,
    "last_login": "2024-01-XX"
  }
}
```

**Step 2: Test Support Engineer Permissions**
```bash
# Replace SUPPORT_TOKEN with the access_token from login response

# Should work - view all tickets
curl -X GET http://localhost:8000/tickets/all \
  -H "Authorization: Bearer SUPPORT_TOKEN"

# Should work - update ticket status
curl -X PUT http://localhost:8000/ticket/update \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SUPPORT_TOKEN" \
  -d '{
    "ticket_id": 1,
    "status": "in_progress"
  }'

# Should work - chat access
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SUPPORT_TOKEN" \
  -d '{
    "content": "How to reset user password",
    "user_id": "support-engineer"
  }'
```

## 🌐 Web Interface Testing

### Using the Interactive API Documentation

1. **Open API Docs:** http://localhost:8000/docs
2. **Find the `/login` endpoint**
3. **Click "Try it out"**
4. **Enter credentials:**
   ```json
   {
     "username": "appuser",
     "password": "password123"
   }
   ```
5. **Execute and copy the access_token**
6. **Click "Authorize" button at the top**
7. **Enter:** `Bearer YOUR_ACCESS_TOKEN`
8. **Test other endpoints with authentication**

### Using the Streamlit Interfaces

**Note:** The current Streamlit interfaces may not have built-in login forms. You'll need to use the API token approach:

1. **Get token via API login**
2. **Use token in backend for authenticated requests**

## 📊 User Status and Details

### Check Current User Details
```bash
# After login, use this to see full user profile
curl -X GET http://localhost:8000/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Regular User Response:**
```json
{
  "id": 1,
  "username": "appuser",
  "role": "user",
  "full_name": "Application User", 
  "email": "appuser@example.com",
  "is_active": true,
  "created_at": "2024-01-XX",
  "last_login": "2024-01-XX"
}
```

**Support Engineer Response:**
```json
{
  "id": 2,
  "username": "support-engineer",
  "role": "support-engineer", 
  "full_name": "Support Engineer",
  "email": "support@example.com",
  "is_active": true,
  "created_at": "2024-01-XX",
  "last_login": "2024-01-XX"
}
```

## 🔍 Permission Testing Matrix

| Endpoint | Regular User | Support Engineer |
|----------|--------------|------------------|
| `POST /login` | ✅ | ✅ |
| `GET /me` | ✅ | ✅ |
| `POST /chat` | ✅ | ✅ |
| `GET /analytics/dashboard` | ✅ | ✅ |
| `GET /tickets/all` | ❌ 403 | ✅ |
| `PUT /ticket/update` | ❌ 403 | ✅ |

## 🛠️ Quick Test Scripts

### Test Regular User
```bash
#!/bin/bash
echo "Testing Regular User Login..."
RESPONSE=$(curl -s -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "appuser", "password": "password123"}')

TOKEN=$(echo $RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "Token: ${TOKEN:0:20}..."

echo "User Details:"
curl -s -X GET http://localhost:8000/me \
  -H "Authorization: Bearer $TOKEN" | jq .
```

### Test Support Engineer
```bash
#!/bin/bash
echo "Testing Support Engineer Login..."
RESPONSE=$(curl -s -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "support-engineer", "password": "support123"}')

TOKEN=$(echo $RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "Token: ${TOKEN:0:20}..."

echo "User Details:"
curl -s -X GET http://localhost:8000/me \
  -H "Authorization: Bearer $TOKEN" | jq .

echo "All Tickets:"
curl -s -X GET http://localhost:8000/tickets/all \
  -H "Authorization: Bearer $TOKEN" | jq .
```

## 🚨 Common Issues

### Invalid Credentials
```json
{
  "detail": "Invalid username or password"
}
```

### Missing Authorization
```json
{
  "detail": "Not authenticated"
}
```

### Insufficient Permissions
```json
{
  "detail": "Support engineer access required"
}
```

### Token Expired
```json
{
  "detail": "Invalid authentication token"
}
```

## ✅ Successful Login Indicators

1. **Login Response contains:**
   - `access_token` (JWT string)
   - `token_type: "bearer"`
   - `user` object with role information

2. **User Details Response shows:**
   - Correct username and role
   - Updated `last_login` timestamp
   - Active status

3. **Permission Tests show:**
   - Regular user: Access denied to support endpoints
   - Support engineer: Access granted to all endpoints

Run the automated test with: `./test_auth.sh` for quick verification!