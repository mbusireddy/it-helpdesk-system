# 🔐 Where to Login - IT Helpdesk System

## 🌐 Login URLs - Web Interfaces

### **Primary Login Interfaces** (Login Required)
| Interface | URL | Purpose | Login Method |
|-----------|-----|---------|--------------|
| **Chat Interface** | http://localhost:8501 | AI chat with agents | Built-in login page |
| **Dashboard** | http://localhost:8502 | Analytics & ticket management | Built-in login page |

### **API Access** (Token-based)
| Interface | URL | Purpose | Login Method |
|-----------|-----|---------|--------------|
| **API Docs** | http://localhost:8000/docs | Interactive API testing | Token authentication |
| **Direct API** | http://localhost:8000/login | Raw API access | POST request |

## 👥 User Accounts

### **Regular User Account**
- **Username:** `appuser`
- **Password:** `password123`
- **Role:** `user`
- **Permissions:**
  - ✅ Chat with AI agents
  - ✅ View system analytics
  - ✅ Track own tickets
  - ❌ Cannot view all tickets
  - ❌ Cannot update ticket status

### **Support Engineer Account**
- **Username:** `support-engineer`
- **Password:** `support123`
- **Role:** `support-engineer`
- **Permissions:**
  - ✅ All regular user features
  - ✅ View ALL tickets in system
  - ✅ Update ticket status
  - ✅ Assign tickets to engineers
  - ✅ Access admin analytics

## 🚀 How to Login

### **Method 1: Web Interface Login (Easiest)**

#### **Chat Interface Login:**
1. Go to: http://localhost:8501
2. You'll see a login page with two options:
   - **Click "Login as Regular User"** (quick login)
   - **Click "Login as Support Engineer"** (quick login)
   - **Or enter credentials manually**
3. After login, you'll see the chat interface with your permissions

#### **Dashboard Login:**
1. Go to: http://localhost:8502
2. Same login options as chat interface
3. After login, you'll see analytics and role-specific features

### **Method 2: API Documentation Login**
1. Go to: http://localhost:8000/docs
2. Click on `/login` endpoint
3. Click "Try it out"
4. Enter credentials:
   ```json
   {
     "username": "appuser",
     "password": "password123"
   }
   ```
5. Execute and copy the `access_token`
6. Click "Authorize" button at top of page
7. Enter: `Bearer YOUR_ACCESS_TOKEN`
8. Now you can test all endpoints with authentication

### **Method 3: Direct API Login**
```bash
# Login as regular user
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "appuser", "password": "password123"}'

# Login as support engineer
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "support-engineer", "password": "support123"}'
```

### **Method 4: Test Scripts**
```bash
# Test regular user login
./test_user_login.sh

# Test support engineer login
./test_support_login.sh

# Complete system test
./test_everything.sh
```

## 🎯 What You See After Login

### **Regular User Experience**
After logging in as `appuser`:

**Chat Interface (8501):**
- Welcome message with your username
- Chat input to talk with AI agents
- Sidebar showing:
  - Your user information
  - Session analytics
  - Clear chat option

**Dashboard (8502):**
- System analytics (total tickets, resolution rate)
- Charts showing ticket distribution
- Your account information
- Quick links to other interfaces

### **Support Engineer Experience**
After logging in as `support-engineer`:

**Chat Interface (8501):**
- Everything regular users see, PLUS:
- Support engineer tools in sidebar:
  - "View All Tickets" button
  - Ticket status update form
  - Enhanced analytics

**Dashboard (8502):**
- Everything regular users see, PLUS:
- Complete ticket management section:
  - List of ALL tickets in system
  - Ability to update ticket status
  - Support statistics
  - Ticket assignment features

## 🔍 Login Verification

After successful login, you should see:
1. **Welcome message** with your username and role
2. **User information** in sidebar/header
3. **Role-appropriate features** (more options for support engineers)
4. **No "login required" messages**

## 🚨 Troubleshooting Login Issues

### **If login page doesn't load:**
```bash
# Check if services are running
./test_system.sh

# Restart services if needed
./start_with_login.sh
```

### **If login fails:**
- **Check credentials** (case-sensitive)
- **Try quick login buttons** instead of manual entry
- **Check logs:**
  ```bash
  tail -f app.log        # API logs
  tail -f chat_ui.log    # Chat interface logs
  tail -f dashboard.log  # Dashboard logs
  ```

### **If session expires:**
- You'll see "Session expired" message
- Simply login again
- JWT tokens expire after a set time

## 📱 Mobile/Browser Compatibility

The login interfaces work in any modern web browser:
- ✅ Chrome, Firefox, Safari, Edge
- ✅ Mobile browsers
- ✅ Desktop and tablet

## 🔐 Security Features

- **JWT Token Authentication** - Secure token-based system
- **Role-Based Access Control** - Different permissions per role
- **Session Management** - Automatic logout on token expiry
- **Password Protection** - Passwords are hashed in database

## 🎪 Quick Test Flow

1. **Start System:** `./start_with_login.sh`
2. **Open Chat:** http://localhost:8501
3. **Click "Login as Regular User"**
4. **Test chat:** Type "My computer won't start"
5. **Open Dashboard:** http://localhost:8502  
6. **Login again or use existing session**
7. **View analytics and features**
8. **Logout and try as Support Engineer**

## 📍 Summary - Where to Login

**🎯 Main Login Points:**
- **Chat Interface:** http://localhost:8501 (primary user interface)
- **Dashboard:** http://localhost:8502 (analytics and admin)
- **API Docs:** http://localhost:8000/docs (developer testing)

**👤 Quick Login:**
- Regular User: `appuser` / `password123`
- Support Engineer: `support-engineer` / `support123`

**🚀 Start with:** `./start_with_login.sh`

The system now has **full web-based login functionality** - no command line required for normal usage!