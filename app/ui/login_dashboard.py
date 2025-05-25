import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# Configure Streamlit
st.set_page_config(
    page_title="IT Helpdesk Dashboard - Login",
    page_icon="📊",
    layout="wide"
)

# API base URL
API_BASE = "http://localhost:8000"


def init_session_state():
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
            st.session_state.is_logged_in = True
            return True, "Login successful!"
        else:
            return False, response.json().get("detail", "Login failed")
    except Exception as e:
        return False, f"Connection error: {e}"


def logout():
    st.session_state.access_token = None
    st.session_state.user_info = None
    st.session_state.is_logged_in = False


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
        elif response.status_code == 401:
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
    st.title("📊 IT Helpdesk Dashboard - Login")
    
    # Login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Please login to access the dashboard")
        
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


def dashboard_page():
    # Header with user info and logout
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.title("📊 IT Helpdesk Dashboard")
        st.markdown("*Real-time analytics and ticket management*")
    
    with col2:
        st.markdown(f"**Logged in as:** {st.session_state.user_info['username']}")
        st.markdown(f"**Role:** {st.session_state.user_info['role']}")
    
    with col3:
        if st.button("Logout", type="secondary"):
            logout()
            st.rerun()

    # Fetch analytics data
    analytics = get_analytics()
    
    if not analytics:
        st.error("Unable to fetch analytics data. Please check your connection.")
        return

    # Key Metrics Row
    st.markdown("### 📈 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Tickets",
            value=analytics["total_tickets"],
            delta=None
        )
    
    with col2:
        st.metric(
            label="Open Tickets",
            value=analytics["open_tickets"],
            delta=None
        )
    
    with col3:
        st.metric(
            label="Resolved Tickets",
            value=analytics["resolved_tickets"],
            delta=None
        )
    
    with col4:
        st.metric(
            label="Resolution Rate",
            value=f"{analytics['resolution_rate']:.1f}%",
            delta=None
        )

    # Charts Row
    st.markdown("### 📊 Analytics Charts")
    col1, col2 = st.columns(2)
    
    with col1:
        # Status Distribution Pie Chart
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
                    "Open": "#ff7f7f",
                    "Resolved": "#7fbf7f"
                }
            )
            st.plotly_chart(fig_status, use_container_width=True)
        else:
            st.info("No tickets to display")
    
    with col2:
        # Category Breakdown Bar Chart
        if analytics["category_breakdown"]:
            categories = [item["category"] for item in analytics["category_breakdown"]]
            counts = [item["count"] for item in analytics["category_breakdown"]]
            
            fig_category = px.bar(
                x=categories,
                y=counts,
                title="Tickets by Category",
                labels={"x": "Category", "y": "Number of Tickets"},
                color=counts,
                color_continuous_scale="viridis"
            )
            st.plotly_chart(fig_category, use_container_width=True)
        else:
            st.info("No category data to display")

    # Support Engineer Section
    if st.session_state.user_info['role'] == 'support-engineer':
        st.markdown("### 🔧 Support Engineer Tools")
        
        # Fetch all tickets
        tickets = get_all_tickets()
        
        if tickets:
            st.markdown(f"#### All Tickets ({len(tickets)})")
            
            # Convert to DataFrame for better display
            df_tickets = pd.DataFrame(tickets)
            
            # Display tickets table
            for idx, ticket in enumerate(tickets):
                with st.expander(f"Ticket #{ticket['id']} - {ticket['category']} - {ticket['status']}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Title:** {ticket['title']}")
                        st.write(f"**Description:** {ticket['description'][:200]}...")
                        st.write(f"**Created:** {ticket['created_at']}")
                        st.write(f"**Updated:** {ticket['updated_at']}")
                        if ticket.get('assigned_to'):
                            st.write(f"**Assigned to:** {ticket['assigned_to']}")
                    
                    with col2:
                        # Status update form
                        new_status = st.selectbox(
                            "Update Status",
                            ["open", "in_progress", "resolved"],
                            index=["open", "in_progress", "resolved"].index(ticket['status']),
                            key=f"status_{ticket['id']}"
                        )
                        
                        if st.button(f"Update", key=f"update_{ticket['id']}"):
                            if new_status != ticket['status']:
                                result = update_ticket_status(ticket['id'], new_status)
                                if result:
                                    st.success(f"Ticket #{ticket['id']} updated to {new_status}")
                                    st.rerun()
                                else:
                                    st.error("Failed to update ticket")
                            else:
                                st.info("Status unchanged")
            
            # Ticket statistics for support engineers
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
        # Regular user view
        st.markdown("### 👤 Your Account")
        st.info("""
        **Regular User Features:**
        - View system analytics
        - Access chat interface for support
        - Track your own tickets
        
        For ticket management and administrative features, please contact a support engineer.
        """)

    # Footer with useful links
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


def main():
    init_session_state()
    
    if not st.session_state.is_logged_in:
        login_page()
    else:
        dashboard_page()


if __name__ == "__main__":
    main()