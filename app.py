import streamlit as st
import re
import logging
from typing import Optional, Dict
import os
from dotenv import load_dotenv
load_dotenv()

# Import statements for the new modules
from database import add_user, get_user, check_password, get_all_stats
from email_service import send_email, send_bulk_emails, schedule_email, generate_email_report
from dashboard import display_dashboard
from contact_manager import display_contacts
from template_manager import display_templates
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def local_css() -> None:
    st.markdown("""
    <style>
    .stApp { background-color: #867365; font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .css-1aumxhk { background-color: #000000; border-right: 1px solid #e1e4e8; }
    .stButton > button { background-color: #4a90e2; color: white; border-radius: 6px; font-weight: 600; }
    .stButton > button:hover { background-color: #414141; }
    .stTextInput > div > div > input:focus { border-color: #4a90e2; }
    .success-message { background-color: #e8f5e9; color: #2e7d32; }
    .error-message { background-color: #ffebee; color: #d32f2f; }
    </style>
    """, unsafe_allow_html=True)

def is_valid_email(email: str) -> bool:
    
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def validate_password(password: str) -> bool:
    return (
        len(password) >= 8 and 
        any(char.isupper() for char in password) and 
        any(char.islower() for char in password) and 
        any(char.isdigit() for char in password)
    )

def logout() -> None:

    try:
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    except Exception as e:
        logger.error(f"Logout error: {e}")
        st.error("An error occurred during logout.")

def main() -> None:
    # Configure page settings
    st.set_page_config(
        page_title="Mass Mail", 
        layout="wide",
        initial_sidebar_state="auto"
    )

    # Apply custom styling
    local_css()

    # Initialize session state
    if 'user_logged_in' not in st.session_state:
        st.session_state.user_logged_in = False

    # Main application layout
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.title("Mass Mailing Application")
        st.markdown("---")

        # Navigation
        page = st.radio(
            "Navigate", 
            ["Login", "Send Email", "Dashboard", "Contacts", "Templates", "Analytics"], 
            horizontal=True
        )

        # Login Page
        if page == "Login":
            choice = st.radio("Select Action", ["Login", "Register"], horizontal=True)
            
            if choice == "Login":
                with st.form("Login Form"):
                    username = st.text_input('Username', placeholder="Enter your username")
                    password = st.text_input('Password', type='password', placeholder="Enter your password")
                    login_button = st.form_submit_button("Login")

                    if login_button:
                        if not username or not password:
                            st.error("Please enter both username and password.")
                        else:
                            try:
                                user = get_user(username)
                                if user and check_password(user['password'], password):
                                    st.session_state.user_logged_in = True
                                    st.session_state.username = username
                                    st.success("Login Successful!")
                                    st.rerun()
                                else:
                                    st.error("Invalid username or password.")
                            except Exception as e:
                                logger.error(f"Login error: {e}")
                                st.error("An unexpected error occurred.")
            
            elif choice == "Register":
                with st.form("Registration Form"):
                    username = st.text_input('Username', placeholder="Choose a unique username")
                    password = st.text_input('Password', type='password', placeholder="Create a strong password")
                    confirm_password = st.text_input('Confirm Password', type='password', placeholder="Repeat your password")
                    register_button = st.form_submit_button("Register")

                    if register_button:
                        if not username or not password or not confirm_password:
                            st.error("Please fill in all fields.")
                        elif not validate_password(password):
                            st.error("Password must be at least 8 characters long and include uppercase, lowercase, and numbers.")
                        elif password != confirm_password:
                            st.error("Passwords do not match.")
                        else:
                            try:
                                if add_user(username, password):
                                    st.success("Registration Successful! You can now login.")
                                else:
                                    st.error("Registration failed. Username might already exist.")
                            except Exception as e:
                                logger.error(f"Registration error: {e}")
                                st.error("An unexpected error occurred during registration.")

        # Email Sending Page
        elif page == "Send Email":
            if st.session_state.get('user_logged_in', False):
                st.subheader(f"📧 Email Sender - Welcome {st.session_state.get('username', 'User')}")
                
                with st.form("Email Form"):
                    sender = st.text_input('Your Email', placeholder="Your Gmail address")
                    to = st.text_area('Recipients (comma-separated)', placeholder="Enter recipient emails")
                    subject = st.text_input('Email Subject', placeholder="Subject of your email")
                    body = st.text_area('Email Body', placeholder="Write your message here...")
                    send_button = st.form_submit_button("Send Email")

                    if send_button:
                        recipients = [email.strip() for email in to.split(",")]
                        if not sender or not recipients or not subject or not body:
                            st.error("Please fill all fields.")
                        elif not is_valid_email(sender):
                            st.error("Invalid sender email format.")
                        elif not all(is_valid_email(recipient) for recipient in recipients):
                            st.error("One or more recipient emails are invalid.")
                        else:
                            results = send_bulk_emails(sender, recipients, subject, body)
                            st.success("Emails sent successfully!")
                            st.write(results)
            else:
                st.warning("Please login to send emails.")

                # Email Scheduling
                with st.expander("📅 Schedule an Email"):
                    send_time = st.text_input("Send Time (YYYY-MM-DD HH:MM:SS)", placeholder="Enter the time to send")
                    schedule_button = st.button("Schedule Email")
                    if schedule_button and send_time:
                        schedule_email(sender, recipients, subject, body, send_time)
                        st.success("Email scheduled successfully!")

                if st.sidebar.button('🚪 Logout'):
                    logout()

        # Dashboard Page
        if page == "Dashboard":
            if st.session_state.get('user_logged_in', False):
                display_dashboard()
            else:
                st.warning("Please login to view the dashboard.")

        # Contacts Management Page
        elif page == "Contacts":
            if st.session_state.get('user_logged_in', False):
                display_contacts()
            else:
                st.warning("Please login to manage contacts.")

        # Templates Management Page
        elif page == "Templates":
            if st.session_state.get('user_logged_in', False):
                display_templates()
            else:
                st.warning("Please login to manage templates.")

        # Analytics Page
        elif page == "Analytics":
            if st.session_state.get('user_logged_in', False):
                st.subheader("📊 Email Analytics")
                report = generate_email_report()
                st.json(report)
            else:
                st.warning("Please login to view analytics.")

if __name__ == "__main__":
    main()

