import streamlit as st
from database import DatabaseManager

# Initialize database manager
db_manager = DatabaseManager()

def display_templates():
    """
    Manage email templates with options to create, read, update, and delete templates.
    """
    st.title("📄 Email Template Management")
    st.markdown("Manage your email templates here.")

    # Ensure the templates table exists
    db_manager.init_templates_table()

    # Display existing templates
    templates = db_manager.fetch_all_templates()
    if templates:
        st.markdown("### Existing Templates")
        for template_id, name, content in templates:
            with st.expander(f"📜 {name}"):
                st.write(content)
                col1, col2, col3 = st.columns([1, 1, 2])

                with col1:
                    if st.button(f"🖊 Edit Template {template_id}", key=f"edit_{template_id}"):
                        edit_template(template_id, name, content)

                with col2:
                    if st.button(f"❌ Delete Template {template_id}", key=f"delete_{template_id}"):
                        db_manager.delete_template(template_id)
                        st.success(f"Template {template_id} deleted successfully.")
                        st.rerun()
    else:
        st.info("No templates available. Create one!")

    # Add new template
    st.markdown("### Create New Template")
    with st.form("Create Template"):
        template_name = st.text_input("Template Name", placeholder="Enter a descriptive name")
        template_content = st.text_area("Template Content", placeholder="Write your email content here...")
        create_button = st.form_submit_button("Create Template")

        if create_button:
            if not template_name or not template_content:
                st.error("Template name and content are required.")
            else:
                db_manager.add_template(template_name, template_content)
                st.success("Template created successfully!")
                st.rerun()


def edit_template(template_id, current_name, current_content):
    """
    Edit an existing template.
    """
    st.markdown(f"### Edit Template {template_id}")
    with st.form(f"Edit Template {template_id}"):
        updated_name = st.text_input("Template Name", value=current_name)
        updated_content = st.text_area("Template Content", value=current_content)
        update_button = st.form_submit_button("Update Template")

        if update_button:
            if not updated_name or not updated_content:
                st.error("Template name and content are required.")
            else:
                db_manager.update_template(template_id, updated_name, updated_content)
                st.success("Template updated successfully!")
                st.rerun()


# For standalone testing
if __name__ == "__main__":
    display_templates()
