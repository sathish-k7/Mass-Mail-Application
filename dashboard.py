import streamlit as st
import plotly.express as px
import pandas as pd
from database import get_email_stats

def display_dashboard():
    st.title("📊 User Analytics Dashboard")
    
    # Fetch email statistics
    email_stats = get_email_stats()
    
    # Sidebar for filters
    st.sidebar.subheader("Filters")
    filter_options = ["All", "Sent", "Delivered", "Inbox", "Spam"]
    selected_filter = st.sidebar.radio("Filter Emails By Status", filter_options)
    
    # Prepare data for visualizations
    if email_stats:
        stats_df = pd.DataFrame.from_dict(
            email_stats, 
            orient='index', 
            columns=['Count']
        ).reset_index()
        stats_df.columns = ['Status', 'Count']
        
        # Apply filter
        if selected_filter != "All":
            stats_df = stats_df[stats_df['Status'] == selected_filter]

        # Pie Chart for Email Status Distribution
        st.subheader("📧 Email Status Distribution")
        fig_pie = px.pie(
            stats_df, 
            values='Count', 
            names='Status', 
            hole=0.3,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_pie.update_layout(title_x=0.5)
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Bar Chart for Email Statistics
        st.subheader("📊 Email Stats")
        fig_bar = px.bar(
            stats_df, 
            x='Status', 
            y='Count',
            color='Status',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_bar.update_layout(title_x=0.5)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning("No email statistics available.")

# For standalone testing
if __name__ == "__main__":
    display_dashboard()
