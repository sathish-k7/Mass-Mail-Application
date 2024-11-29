import streamlit as st
import plotly.express as px
import pandas as pd
from database import get_all_stats

def display_dashboard():
    st.title("📊 Email Statistics Dashboard")
    
    # Fetch email statistics
    stats = get_all_stats()
    
    if stats:
        # Prepare data for visualizations
        stats_df = pd.DataFrame(list(stats.items()), columns=['Status', 'Count'])
        
        # Display total counts
        st.subheader("📈 Total Email Statistics")
        st.write(stats_df.set_index('Status'))
        
        # Pie Chart for Email Status Distribution
        st.subheader("📧 Email Status Distribution")
        fig_pie = px.pie(
            stats_df, 
            values='Count', 
            names='Status', 
            hole=0.3,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_pie.update_layout(title_text='Email Status Distribution', title_x=0.5)
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Bar Chart for Email Statistics
        st.subheader("📊 Email Stats Overview")
        fig_bar = px.bar(
            stats_df, 
            x='Status', 
            y='Count',
            color='Status',
            color_discrete_sequence=px.colors.qualitative.Pastel,
            text='Count'
        )
        fig_bar.update_layout(title_text='Email Counts by Status', title_x=0.5)
        fig_bar.update_traces(textposition='outside')
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning("No email statistics available.")

# For standalone testing
if __name__ == "__main__":
    display_dashboard()
