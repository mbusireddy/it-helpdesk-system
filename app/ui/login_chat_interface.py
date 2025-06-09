# Importing Libraries
import streamlit as st
import requests
import json
from datetime import datetime
import uuid

# Configure the Streamlit app's title, icon, and layout style
st.set_page_config(
    page_title="IT Helpdesk Assistant - Login",
    page_icon="🔐",
    layout="wide"
)

# Base URL of the backend API the app communicates with
API_BASE = "http://localhost:8000"


def init_session_state():
    """
    Initialize the Streamlit session state variables.
    This runs once per user session to keep track of user data, messages, tokens, and login status.
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []  # Store chat messages (user and assistant)
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())  # Unique ID for this chat session
    if "user_id" not in st.session_state:
        st.session_state.user_id = None  # User's identifier (username)
    if "access_token" not in st.session_state:
        st.session_state.access_token = None  # JWT token for authenticated API requests
    if "user_info" not in st.session_state:
        st.session_state.user_info = None  # Dictionary with user details like role, name, email
    if "is_logged_in" not in st.session_state:
        st.session_state.is_logged_in = False  # Boolean flag for login status


def login(username: str, password: str):
    """
    Send login credentials to the backend API and process the response.
    On success, store access token and user info in session state.
    Returns a tuple: (success: bool, message: str)
    """
    try:
        response = requests.post(
            f"{API_BASE}/login",
            json={
                "username": username,
                "password": password
            }
        )
        # Successful login returns status 200 with token and user data
        if response.status_code == 200:
            data = response.json()
            st.session_state.access_token = data["access_token"]
            st.session_state.user_info = data["user"]
            st.session_state.user_id = data["user"]["username"]
            st.session_state.is_logged_in = True
            return True, "Login successful!"
        else:
            # API returns failure status and error message in JSON "detail"
            return False, response.json().get("detail", "Login failed")
    except Exception as e:
        # Network or unexpected errors
        return False, f"Connection error: {e}"


def logout():
    """
    Clear all user-related data from the session state to log out.
    Reset session_id to start fresh.
    """
    st.session_state.access_token = None
    st.session_state.user_info = None
    st.session_state.user_id = None
    st.session_state.is_logged_in = False
    st.session_state.messages = []
    st.session_state.session_id = str(uuid.uuid4())


def send_message(message: str, user_id: str, session_id: str):
    """
    Send a user message to the backend chat API endpoint.
    Attach JWT token for authentication if available.
    Handle various response statuses:
      - 200: success, return assistant's response JSON
      - 401: unauthorized (e.g., expired token), force logout
      - others: show error
    """
    try:
        headers = {}
        if st.session_state.access_token:
            headers["Authorization"] = f"Bearer {st.session_state.access_token}"
        
        response = requests.post(
            f"{API_BASE}/chat",
            json={
                "content": message,
                "user_id": user_id,
                "session_id": session_id
            },
            headers=headers
        )
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            st.error("Session expired. Please login again.")
            logout()
            return None
        else:
            st.error(f"Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None


def get_analytics():
    """
    Fetch dashboard analytics data from the API.
    This info includes ticket counts, resolution rates, etc.
    Returns analytics JSON or None if failure.
    """
    try:
        headers = {}
        if st.session_state.access_token:
            headers["Authorization"] = f"Bearer {st.session_state.access_token}"
        
        response = requests.get(
            f"{API_BASE}/analytics/dashboard",
            headers=headers
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None


def get_all_tickets():
    """
    For support engineers only.
    Fetch all tickets from the backend.
    Returns list of tickets or None if failure.
    """
    try:
        headers = {}
        if st.session_state.access_token:
            headers["Authorization"] = f"Bearer {st.session_state.access_token}"
        
        response = requests.get(
            f"{API_BASE}/tickets/all",
            headers=headers
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None


def update_ticket_status(ticket_id: int, status: str):
    """
    For support engineers only.
    Update the status of a ticket by calling backend API.
    Returns updated ticket data or None if failure.
    """
    try:
        headers = {}
        if st.session_state.access_token:
            headers["Authorization"] = f"Bearer {st.session_state.access_token}"
        
        response = requests.put(
            f"{API_BASE}/ticket/update",
            json={
                "ticket_id": ticket_id,
                "status": status
            },
            headers=headers
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None


def login_page():
    """
    Display the login interface with:
    - Quick login buttons for demo users
    - Manual username/password form
    - Info about test accounts
    """
    st.title("🔐 IT Helpdesk System - Login")
    
    # Layout columns to center the login form nicely
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Please login to continue")
        
        # Quick login for convenience/testing without typing credentials
        st.markdown("#### Quick Login Options:")
        
        col_user, col_support = st.columns(2)
        
        with col_user:
            st.markdown("**👤 Regular User**")
            if st.button("Login as Regular User", key="quick_user", use_container_width=True):
                success, message = login("appuser", "password123")
                if success:
                    st.success(message)
                    st.rerun()  # Reload app to reflect login state
                else:
                    st.error(message)
        
        with col_support:
            st.markdown("**🔧 Support Engineer**")
            if st.button("Login as Support Engineer", key="quick_support", use_container_width=True):
                success, message = login("support-engineer", "support123")
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        
        st.markdown("---")
        
        # Manual login form for custom credentials
        st.markdown("#### Manual Login:")
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if username and password:
                    success, message = login(username, password)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please enter both username and password")
        
        # Show info on test accounts so users can try them easily
        st.markdown("---")
        st.markdown("#### Test Accounts:")
        st.info("""
        **Regular User:**
        • Username: `appuser`
        • Password: `password123`
        • Permissions: Chat, Analytics, Own Tickets
        
        **Support Engineer:**
        • Username: `support-engineer`
        • Password: `support123`
        • Permissions: All tickets, Status updates, Admin features
        """)


def chat_page():
    """
    Main chat interface after user logs in.
    Shows header with user info, logout button,
    sidebar with user info, analytics, support engineer tools,
    and the chat message area with input.
    """
    # Header row with app title, user info, logout button
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.title("🛠️ IT Helpdesk Assistant")
        st.markdown("*Your AI-powered IT support companion*")
    
    with col2:
        # Show logged-in username and role
        st.markdown(f"**Logged in as:** {st.session_state.user_info['username']}")
        st.markdown(f"**Role:** {st.session_state.user_info['role']}")
    
    with col3:
        # Logout button logs out and reloads app
        if st.button("Logout", type="secondary"):
            logout()
            st.rerun()

    # Sidebar for user details, analytics, and support engineer tools
    with st.sidebar:
        st.header("👤 User Information")
        st.write(f"**Username:** {st.session_state.user_info['username']}")
        st.write(f"**Role:** {st.session_state.user_info['role']}")
        st.write(f"**Full Name:** {st.session_state.user_info['full_name']}")
        st.write(f"**Email:** {st.session_state.user_info.get('email', 'N/A')}")
        
        st.header("📊 Analytics")
        analytics = get_analytics()
        if analytics:
            # Show key ticket metrics as Streamlit metrics
            st.metric("Total Tickets", analytics["total_tickets"])
            st.metric("Open Tickets", analytics["open_tickets"])
            st.metric("Resolved Tickets", analytics["resolved_tickets"])
            st.metric("Resolution Rate", f"{analytics['resolution_rate']:.1f}%")
        
        # Support engineer exclusive features
        if st.session_state.user_info['role'] == 'support-engineer':
            st.header("🔧 Support Engineer Tools")
            
            # Button to fetch and display all tickets
            if st.button("View All Tickets"):
                tickets = get_all_tickets()
                if tickets:
                    st.success(f"Found {len(tickets)} tickets")
                    for ticket in tickets[:3]:  # Display first 3 tickets as sample
                        st.write(f"**#{ticket['id']}** - {ticket['status']} - {ticket['category']}")
                else:
                    st.error("Could not fetch tickets")
            
            # Section to update ticket status
            st.subheader("Update Ticket Status")
            ticket_id = st.number_input("Ticket ID", min_value=1, step=1, key="update_ticket_id")
            status = st.selectbox("New Status", ["open", "in_progress", "resolved"], key="update_status")
            
            if st.button("Update Status"):
                result = update_ticket_status(ticket_id, status)
                if result:
                    st.success(f"Ticket #{ticket_id} updated to {status}")
                else:
                    st.error("Failed to update ticket")
        
        st.header("Session Info")
        # Show shortened session ID
        st.text(f"Session: {st.session_state.session_id[:8]}...")
        
        # Button to clear the current chat session
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.session_state.session_id = str(uuid.uuid4())  # New session ID
            st.rerun()

    # Main chat message container
    chat_container = st.container()

    with chat_container:
        # Render all past chat messages
        for message in st.session_state.messages:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(message["content"])
                    # Show which AI agent handled the message if provided
                    if "agent" in message:
                        st.caption(f"*Handled by: {message['agent']} agent*")

    # Chat input box for new user queries
    if prompt := st.chat_input("How can I help you today?"):
        # Add user message to session state for display and history
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        # Immediately show user message in chat
        with st.chat_message("user"):
            st.write(prompt)

        # Send message to backend and get assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = send_message(
                    prompt,
                    st.session_state.user_id,
                    st.session_state.session_id
                )

                if response:
                    # Show assistant's response text
                    st.write(response["response"])
                    st.caption(f"*Handled by: {response['agent']} agent*")

                    # Save assistant message in session state history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response["response"],
                        "agent": response["agent"]
                    })

                    # Show ticket creation info if any
                    if response.get("ticket_id"):
                        st.info(f"🎫 Ticket #{response['ticket_id']} created")
                else:
                    st.error("Failed to get response")


def main():
    """
    Main entry point for the app.
    Initialize session state and route user to login or chat pages based on login status.
    """
    init_session_state()
    
    if not st.session_state.is_logged_in:
        login_page()
    else:
        chat_page()


if __name__ == "__main__":
    main()
