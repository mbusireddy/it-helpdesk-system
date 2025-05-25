import streamlit as st
import requests
import json
from datetime import datetime
import uuid

# Configure Streamlit
st.set_page_config(
    page_title="IT Helpdesk Assistant - Login",
    page_icon="🔐",
    layout="wide"
)

# API base URL
API_BASE = "http://localhost:8000"


def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "access_token" not in st.session_state:
        st.session_state.access_token = None
    if "user_info" not in st.session_state:
        st.session_state.user_info = None
    if "is_logged_in" not in st.session_state:
        st.session_state.is_logged_in = False


def login(username: str, password: str):
    try:
        response = requests.post(
            f"{API_BASE}/login",
            json={
                "username": username,
                "password": password
            }
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.access_token = data["access_token"]
            st.session_state.user_info = data["user"]
            st.session_state.user_id = data["user"]["username"]
            st.session_state.is_logged_in = True
            return True, "Login successful!"
        else:
            return False, response.json().get("detail", "Login failed")
    except Exception as e:
        return False, f"Connection error: {e}"


def logout():
    st.session_state.access_token = None
    st.session_state.user_info = None
    st.session_state.user_id = None
    st.session_state.is_logged_in = False
    st.session_state.messages = []
    st.session_state.session_id = str(uuid.uuid4())


def send_message(message: str, user_id: str, session_id: str):
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
    """Support engineer only - get all tickets"""
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
    """Support engineer only - update ticket status"""
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
    st.title("🔐 IT Helpdesk System - Login")
    
    # Login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Please login to continue")
        
        # Quick login buttons
        st.markdown("#### Quick Login Options:")
        
        col_user, col_support = st.columns(2)
        
        with col_user:
            st.markdown("**👤 Regular User**")
            if st.button("Login as Regular User", key="quick_user", use_container_width=True):
                success, message = login("appuser", "password123")
                if success:
                    st.success(message)
                    st.rerun()
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
        
        # Manual login form
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
        
        # Account information
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
    # Header with user info and logout
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.title("🛠️ IT Helpdesk Assistant")
        st.markdown("*Your AI-powered IT support companion*")
    
    with col2:
        st.markdown(f"**Logged in as:** {st.session_state.user_info['username']}")
        st.markdown(f"**Role:** {st.session_state.user_info['role']}")
    
    with col3:
        if st.button("Logout", type="secondary"):
            logout()
            st.rerun()

    # Sidebar with user-specific features
    with st.sidebar:
        st.header("👤 User Information")
        st.write(f"**Username:** {st.session_state.user_info['username']}")
        st.write(f"**Role:** {st.session_state.user_info['role']}")
        st.write(f"**Full Name:** {st.session_state.user_info['full_name']}")
        st.write(f"**Email:** {st.session_state.user_info.get('email', 'N/A')}")
        
        st.header("📊 Analytics")
        analytics = get_analytics()
        if analytics:
            st.metric("Total Tickets", analytics["total_tickets"])
            st.metric("Open Tickets", analytics["open_tickets"])
            st.metric("Resolved Tickets", analytics["resolved_tickets"])
            st.metric("Resolution Rate", f"{analytics['resolution_rate']:.1f}%")
        
        # Support Engineer features
        if st.session_state.user_info['role'] == 'support-engineer':
            st.header("🔧 Support Engineer Tools")
            
            if st.button("View All Tickets"):
                tickets = get_all_tickets()
                if tickets:
                    st.success(f"Found {len(tickets)} tickets")
                    for ticket in tickets[:3]:  # Show first 3
                        st.write(f"**#{ticket['id']}** - {ticket['status']} - {ticket['category']}")
                else:
                    st.error("Could not fetch tickets")
            
            # Ticket status update
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
        st.text(f"Session: {st.session_state.session_id[:8]}...")
        
        # Clear chat
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.session_state.session_id = str(uuid.uuid4())
            st.rerun()

    # Main chat interface
    chat_container = st.container()

    with chat_container:
        # Display chat messages
        for message in st.session_state.messages:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(message["content"])
                    if "agent" in message:
                        st.caption(f"*Handled by: {message['agent']} agent*")

    # Chat input
    if prompt := st.chat_input("How can I help you today?"):
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        # Display user message immediately
        with st.chat_message("user"):
            st.write(prompt)

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = send_message(
                    prompt,
                    st.session_state.user_id,
                    st.session_state.session_id
                )

                if response:
                    st.write(response["response"])
                    st.caption(f"*Handled by: {response['agent']} agent*")

                    # Add assistant message
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response["response"],
                        "agent": response["agent"]
                    })

                    # Show ticket info if created
                    if response.get("ticket_id"):
                        st.info(f"🎫 Ticket #{response['ticket_id']} created")
                else:
                    st.error("Failed to get response")


def main():
    init_session_state()
    
    if not st.session_state.is_logged_in:
        login_page()
    else:
        chat_page()


if __name__ == "__main__":
    main()