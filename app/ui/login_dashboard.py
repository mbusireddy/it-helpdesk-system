import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# --- Streamlit Page Configuration ---
# Set page title, icon, and layout style (wide makes full use of screen width)
st.set_page_config(
    page_title="IT Helpdesk Dashboard - Login",
    page_icon="📊",
    layout="wide"
)

# Base URL for the backend API server
API_BASE = "http://localhost:8000"


# --- Session State Initialization ---
def init_session_state():
    """
    Initialize session state variables for user authentication and session management.
    These variables persist across Streamlit reruns during the user session.
    """
    if "access_token" not in st.session_state:
        st.session_state.access_token = None  # Store JWT or token after login
    if "user_info" not in st.session_state:
        st.session_state.user_info = None  # Store user details like username and role
    if "is_logged_in" not in st.session_state:
        st.session_state.is_logged_in = False  # Track if user is logged in


# --- Authentication Functions ---

def login(username: str, password: str):
    """
    Perform login by sending username and password to API.
    If successful, store access token and user info in session state.
    
    Returns:
        Tuple (success: bool, message: str)
    """
    try:
        # POST request to /login endpoint with JSON payload
        response = requests.post(
            f"{API_BASE}/login",
            json={
                "username": username,
                "password": password
            }
        )
        # If login successful (HTTP 200)
        if response.status_code == 200:
            data = response.json()
            # Save token and user info in session state for authenticated API calls
            st.session_state.access_token = data["access_token"]
            st.session_state.user_info = data["user"]
            st.session_state.is_logged_in = True
            return True, "Login successful!"
        else:
            # If login failed, return error message from API or generic message
            return False, response.json().get("detail", "Login failed")
    except Exception as e:
        # Catch network/connection errors
        return False, f"Connection error: {e}"


def logout():
    """
    Clear session state variables to log the user out.
    """
    st.session_state.access_token = None
    st.session_state.user_info = None
    st.session_state.is_logged_in = False


# --- Data Fetching Functions ---

def get_analytics():
    """
    Fetch dashboard analytics data from backend API.
    Requires Authorization header with Bearer token.
    
    Returns:
        JSON response dictionary if successful, else None.
    """
    try:
        headers = {}
        # Add Authorization header if access token exists
        if st.session_state.access_token:
            headers["Authorization"] = f"Bearer {st.session_state.access_token}"
        
        # GET request to /analytics/dashboard endpoint
        response = requests.get(
            f"{API_BASE}/analytics/dashboard",
            headers=headers
        )
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            # Unauthorized - token expired or invalid
            st.error("Session expired. Please login again.")
            logout()
            return None
        else:
            st.error(f"Error fetching analytics: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None


def get_all_tickets():
    """
    Fetch all tickets for support engineers.
    Requires Authorization header.
    
    Returns:
        List of tickets JSON or None on failure.
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
    except Exception:
        return None


def update_ticket_status(ticket_id: int, status: str):
    """
    Update the status of a given ticket by ticket ID.
    Requires Authorization header.
    
    Args:
        ticket_id (int): ID of the ticket to update.
        status (str): New status (e.g. "open", "in_progress", "resolved").
        
    Returns:
        JSON response on success, None on failure.
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
    except Exception:
        return None


# --- UI Pages ---

def login_page():
    """
    Render the login page with quick login buttons for demo users and
    a manual login form for username and password input.
    """
    st.title("📊 IT Helpdesk Dashboard - Login")
    
    # Create three columns to center the login form (left and right empty)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Please login to access the dashboard")
        
        # Quick login buttons for demo users
        st.markdown("#### Quick Login Options:")
        
        col_user, col_support = st.columns(2)
        
        with col_user:
            st.markdown("**👤 Regular User**")
            if st.button("Login as Regular User", key="quick_user", use_container_width=True):
                success, message = login("appuser", "password123")
                if success:
                    st.success(message)
                    st.rerun()  # Rerun app to load dashboard page
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
        
        # Manual login form with username and password fields
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


def dashboard_page():
    """
    Render the main dashboard page showing analytics, key metrics,
    charts, and for support engineers, ticket management tools.
    """
    # Header: Title, logged in user info, and logout button
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.title("📊 IT Helpdesk Dashboard")
        st.markdown("*Real-time analytics and ticket management*")
    
    with col2:
        # Show logged-in username and role
        st.markdown(f"**Logged in as:** {st.session_state.user_info['username']}")
        st.markdown(f"**Role:** {st.session_state.user_info['role']}")
    
    with col3:
        # Logout button triggers logout and rerun app
        if st.button("Logout", type="secondary"):
            logout()
            st.rerun()

    # Fetch analytics data for the dashboard
    analytics = get_analytics()
    
    # If failed to fetch, show error and return
    if not analytics:
        st.error("Unable to fetch analytics data. Please check your connection.")
        return

    # --- Display Key Metrics ---
    st.markdown("### 📈 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    # Total tickets count
    with col1:
        st.metric(
            label="Total Tickets",
            value=analytics["total_tickets"],
            delta=None
        )
    
    # Open tickets count
    with col2:
        st.metric(
            label="Open Tickets",
            value=analytics["open_tickets"],
            delta=None
        )
    
    # Resolved tickets count
    with col3:
        st.metric(
            label="Resolved Tickets",
            value=analytics["resolved_tickets"],
            delta=None
        )
    
    # Resolution rate as a percentage
    with col4:
        st.metric(
            label="Resolution Rate",
            value=f"{analytics['resolution_rate']:.1f}%",
            delta=None
        )

    # --- Display Analytics Charts ---
    st.markdown("### 📊 Analytics Charts")
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart for status distribution if tickets exist
        if analytics["total_tickets"] > 0:
            status_data = {
                "Status": ["Open", "Resolved"],
                "Count": [analytics["open_tickets"], analytics["resolved_tickets"]]
            }
            fig_status = px.pie(
                values=status_data["Count"],
                names=status_data["Status"],
                title="Ticket Status Distribution",
                color_discrete_map={
                    "Open": "#ff7f7f",        # Red shade for open tickets
                    "Resolved": "#7fbf7f"     # Green shade for resolved tickets
                }
            )
            st.plotly_chart(fig_status, use_container_width=True)
        else:
            st.info("No tickets to display")
    
    with col2:
        # Bar chart for tickets by category if data available
        if analytics["category_breakdown"]:
            categories = [item["category"] for item in analytics["category_breakdown"]]
            counts = [item["count"] for item in analytics["category_breakdown"]]
            
            fig_category = px.bar(
                x=categories,
                y=counts,
                title="Tickets by Category",
                labels={"x": "Category", "y": "Number of Tickets"},
                color=counts,
                color_continuous_scale="viridis"  # Color scale for bar intensity
            )
            st.plotly_chart(fig_category, use_container_width=True)
        else:
            st.info("No category data to display")

    # --- Support Engineer Section ---
    # Show ticket management tools if logged-in user is a support engineer
    if st.session_state.user_info['role'] == 'support-engineer':
        st.markdown("### 🔧 Support Engineer Tools")
        
        # Fetch all tickets to display
        tickets = get_all_tickets()
        
        if tickets:
            st.markdown(f"#### All Tickets ({len(tickets)})")
            
            # Display tickets in expandable sections for detail and status update
            for idx, ticket in enumerate(tickets):
                with st.expander(f"Ticket #{ticket['id']} - {ticket['category']} - {ticket['status']}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        # Show ticket details: title, truncated description, timestamps, and assigned user
                        st.write(f"**Title:** {ticket['title']}")
                        st.write(f"**Description:** {ticket['description'][:200]}...")  # Show first 200 chars
                        st.write(f"**Created:** {ticket['created_at']}")
                        st.write(f"**Updated:** {ticket['updated_at']}")
                        if ticket.get('assigned_to'):
                            st.write(f"**Assigned to:** {ticket['assigned_to']}")
                    
                    with col2:
                        # Dropdown to select new status (preselect current status)
                        new_status = st.selectbox(
                            "Update Status",
                            ["open", "in_progress", "resolved"],
                            index=["open", "in_progress", "resolved"].index(ticket['status']),
                            key=f"status_{ticket['id']}"
                        )
                        
                        # Button to submit status update
                        if st.button(f"Update", key=f"update_{ticket['id']}"):
                            if new_status != ticket['status']:
                                # Call API to update ticket status
                                result = update_ticket_status(ticket['id'], new_status)
                                if result:
                                    st.success(f"Ticket #{ticket['id']} updated to {new_status}")
                                    st.rerun()  # Refresh dashboard to show updated status
                                else:
                                    st.error("Failed to update ticket")
                            else:
                                st.info("Status unchanged")
            
            # Summary statistics for support engineers by ticket status
            st.markdown("#### Support Statistics")
            col1, col2, col3 = st.columns(3)
            
            status_counts = {}
            for ticket in tickets:
                status = ticket['status']
                status_counts[status] = status_counts.get(status, 0) + 1
            
            with col1:
                st.metric("Open", status_counts.get('open', 0))
            
            with col2:
                st.metric("In Progress", status_counts.get('in_progress', 0))
            
            with col3:
                st.metric("Resolved", status_counts.get('resolved', 0))
        
        else:
            st.info("No tickets available or insufficient permissions")
    
    else:
        # View for regular users with limited features and info
        st.markdown("### 👤 Your Account")
        st.info("""
        **Regular User Features:**
        - View system analytics
        - Access chat interface for support
        - Track your own tickets
        
        For ticket management and administrative features, please contact a support engineer.
        """)

    # --- Footer with Quick Links ---
    st.markdown("---")
    st.markdown("### 🔗 Quick Links")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💬 Go to Chat Interface"):
            st.markdown("[Open Chat Interface](http://localhost:8501)")
    
    with col2:
        if st.button("📚 API Documentation"):
            st.markdown("[Open API Docs](http://localhost:8000/docs)")
    
    with col3:
        if st.button("🔄 Refresh Data"):
            st.rerun()


# --- Main App Logic ---

def main():
    """
    Main entry point for the app.
    Initializes session and routes between login and dashboard pages.
    """
    init_session_state()
    
    # Show login page if not logged in, else show dashboard
    if not st.session_state.is_logged_in:
        login_page()
    else:
        dashboard_page()


# Run the app
if __name__ == "__main__":
    main()
