import streamlit as st
import requests
import json
from datetime import datetime
import uuid

# Configure Streamlit
st.set_page_config(
    page_title="IT Helpdesk Assistant",
    page_icon="🛠️",
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
        st.session_state.user_id = f"user_{uuid.uuid4().hex[:8]}"


def send_message(message: str, user_id: str, session_id: str):
    try:
        response = requests.post(
            f"{API_BASE}/chat",
            json={
                "content": message,
                "user_id": user_id,
                "session_id": session_id
            }
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None


def get_ticket_status(ticket_id: int):
    try:
        response = requests.post(
            f"{API_BASE}/ticket/status",
            json={"ticket_id": ticket_id}
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"Error fetching ticket: {e}")
        return None


def main():
    init_session_state()

    st.title("🛠️ IT Helpdesk Assistant")
    st.markdown("*Your AI-powered IT support companion*")

    # Sidebar
    with st.sidebar:
        st.header("Session Info")
        st.text(f"User ID: {st.session_state.user_id[:8]}...")
        st.text(f"Session: {st.session_state.session_id[:8]}...")

        st.header("Quick Actions")

        # Ticket status checker
        st.subheader("Check Ticket Status")
        ticket_id_input = st.number_input("Enter Ticket ID", min_value=1, step=1)
        if st.button("Check Status"):
            if ticket_id_input:
                ticket_info = get_ticket_status(int(ticket_id_input))
                if ticket_info:
                    st.success(f"Ticket #{ticket_info['id']}")
                    st.write(f"**Status:** {ticket_info['status']}")
                    st.write(f"**Category:** {ticket_info['category']}")
                    st.write(f"**Title:** {ticket_info['title']}")
                    st.write(f"**Created:** {ticket_info['created_at']}")
                else:
                    st.error("Ticket not found")

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


if __name__ == "__main__":
    main()
