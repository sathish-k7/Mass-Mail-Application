import streamlit as st
import pandas as pd
import csv
from database import DatabaseManager

# Initialize database manager
db_manager = DatabaseManager()

def display_contacts():
    """
    Display all contacts with options to add, update, delete, or import contacts.
    """
    st.title("📒 Contact Management")
    st.markdown("Manage your email contacts here.")

    # Ensure the contacts table exists
    db_manager.init_contacts_table()

    # Display existing contacts
    contacts = db_manager.fetch_all_contacts()
    if contacts:
        df = pd.DataFrame(contacts, columns=["ID", "Name", "Email"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No contacts available. Add some!")

    st.markdown("### Add New Contact")
    with st.form("Add Contact"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        add_button = st.form_submit_button("Add Contact")
        
        if add_button:
            if not name or not email:
                st.error("Both name and email are required.")
            elif not validate_email(email):
                st.error("Invalid email format.")
            else:
                db_manager.add_contact(name, email)
                st.success(f"Contact {name} added successfully.")
                st.rerun()  # Refresh the app after adding a contact

    st.markdown("### Import Contacts")
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    if uploaded_file:
        data = pd.read_csv(uploaded_file)
        if "Name" in data.columns and "Email" in data.columns:
            for _, row in data.iterrows():
                db_manager.add_contact(row["Name"], row["Email"])
            st.success("Contacts imported successfully!")
            st.rerun()  # Refresh the app after importing contacts
        else:
            st.error("CSV must contain 'Name' and 'Email' columns.")

    st.markdown("### Delete Contact")
    contact_id = st.number_input("Enter Contact ID to Delete", min_value=0, step=1)
    if st.button("Delete Contact"):
        db_manager.delete_contact(contact_id)
        st.success("Contact deleted successfully.")
        st.rerun()  # Refresh the app after deleting a contact

# Helper function to validate email format
def validate_email(email: str) -> bool:
    """
    Validate email format using a regex.
    """
    import re
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

# For standalone testing
if __name__ == "__main__":
    display_contacts()
