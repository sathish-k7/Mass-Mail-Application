import streamlit as st
import re
import logging
from typing import Optional, Dict

# Import statements (assuming these are in separate modules)
from database import add_user, get_user, check_password, get_email_stats
from email_service import send_email
from dashboard import display_dashboard

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def local_css() -> None:
    """
    Apply custom CSS to enhance Streamlit UI with improved styling and readability.
    
    Uses a more comprehensive and modern CSS approach for better user experience.
    """
    st.markdown("""
    <style>
    /* Enhanced Global Styling */
    .stApp {
        background-color: #867365;
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Improved Sidebar */
    .css-1aumxhk {
        background-color: #000000;
        border-right: 1px solid #e1e4e8;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    /* Refined Navigation */
    .stRadio > div {
        display: flex;
        justify-content: center;
        gap: 15px;
    }

    .stRadio > div > label {
        background-color: #282828;
        color: #00000;
        padding: 10px 20px;
        border-radius: 8px;
        transition: all 0.3s ease;
        border: 1px solid transparent;
    }

    .stRadio > div > label:hover {
        background-color: #575757;
        border-color: #4a90e2;
    }

    /* Enhanced Input Fields */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea {
        border: 2px solid #ced4da;
        border-radius: 6px;
        padding: 12px;
        transition: all 0.3s ease;
    }

    .stTextInput > div > div > input:focus, 
    .stTextArea > div > div > textarea:focus {
        border-color: #4a90e2;
        box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.2);
    }

    /* Refined Buttons */
    .stButton > button {
        background-color: #4a90e2;
        color: white;
        border: none;
        padding: 10px 25px;
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background-color: #414141;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* Improved Messaging */
    .success-message {
        background-color: #e8f5e9;
        color: #2e7d32;
        border: 1px solid #a5d6a7;
    }

    .error-message {
        background-color: #ffebee;
        color: #d32f2f;
        border: 1px solid #ef9a9a;
    }
    </style>
    """, unsafe_allow_html=True)

def is_valid_email(email: str) -> bool:
    """
    Validate email format with a more robust regex pattern.
    
    Args:
        email (str): Email address to validate
    
    Returns:
        bool: True if email is valid, False otherwise
    """
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def validate_password(password: str) -> bool:
    """
    Validate password strength.
    
    Args:
        password (str): Password to validate
    
    Returns:
        bool: True if password meets criteria, False otherwise
    """
    return (
        len(password) >= 8 and 
        any(char.isupper() for char in password) and 
        any(char.islower() for char in password) and 
        any(char.isdigit() for char in password)
    )

def logout() -> None:
    """
    Securely logout the current user by clearing session state.
    """
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
    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        st.title("Mass Mailing Application")
        st.markdown("---")

        # Navigation
        page = st.radio(
            "Navigate", 
            ["Login", "Send Email", "Dashboard"], 
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
                            st.error("Please enter both username and password.", icon="🚨")
                        else:
                            try:
                                user = get_user(username)
                                if user and check_password(user['password'], password):
                                    st.session_state.user_logged_in = True
                                    st.session_state.username = username
                                    st.success("Login Successful!", icon="✅")
                                    st.rerun()
                                else:
                                    st.error("Invalid username or password.", icon="🚨")
                            except Exception as e:
                                logger.error(f"Login error: {e}")
                                st.error("An unexpected error occurred.", icon="🚨")
            
            elif choice == "Register":
                with st.form("Registration Form"):
                    username = st.text_input('Username', placeholder="Choose a unique username")
                    password = st.text_input('Password', type='password', placeholder="Create a strong password")
                    confirm_password = st.text_input('Confirm Password', type='password', placeholder="Repeat your password")
                    register_button = st.form_submit_button("Register")

                    if register_button:
                        if not username or not password or not confirm_password:
                            st.error("Please fill in all fields.", icon="⚠️")
                        elif not validate_password(password):
                            st.error("Password must be at least 8 characters long and include uppercase, lowercase, and numbers.", icon="⚠️")
                        elif password != confirm_password:
                            st.error("Passwords do not match.", icon="⚠️")
                        else:
                            try:
                                if add_user(username, password):
                                    st.success("Registration Successful! You can now login.", icon="✅")
                                else:
                                    st.error("Registration failed. Username might already exist.", icon="🚨")
                            except Exception as e:
                                logger.error(f"Registration error: {e}")
                                st.error("An unexpected error occurred during registration.", icon="🚨")

        # Email Sending Page
        elif page == "Send Email":
            if st.session_state.get('user_logged_in', False):
                st.subheader(f"📧 Email Sender - Welcome {st.session_state.get('username', 'User')}")
                
                with st.form("Email Form"):
                    sender = st.text_input('Your Email', placeholder="Your Gmail address")
                    to = st.text_input('Recipient Email', placeholder="Recipient's email address")
                    subject = st.text_input('Email Subject', placeholder="Subject of your email")
                    body = st.text_area('Email Body', placeholder="Write your message here...")
                    
                    send_button = st.form_submit_button("Send Email")

                    if send_button:
                        # Comprehensive email validation
                        if not is_valid_email(sender):
                            st.error("Invalid sender email format.", icon="🚨")
                        elif not is_valid_email(to):
                            st.error("Invalid recipient email format.", icon="🚨")
                        elif not all([sender, to, subject, body]):
                            st.error("Please fill all fields.", icon="⚠️")
                        else:
                            try:
                                send_email(sender, to, subject, body)
                                st.success("Email sent successfully!", icon="✅")
                            except Exception as e:
                                logger.error(f"Email sending error: {e}")
                                st.error(f"Failed to send email: {str(e)}", icon="🚨")

                # Logout button
                if st.sidebar.button('🚪 Logout', use_container_width=True):
                    logout()

        # Dashboard Page
        elif page == "Dashboard":
            if st.session_state.get('user_logged_in', False):
                display_dashboard()
            else:
                st.warning("Please login to view the dashboard.", icon="⚠️")

if __name__ == "__main__":
    main()