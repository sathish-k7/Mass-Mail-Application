import streamlit as st
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
from database import get_email_stats

def display_dashboard():
    # Set dashboard title and layout
    st.title("📊 User Analytics Dashboard")
    
    # Create columns for different visualization sections
    col1, col2 = st.columns([2, 1])
    
    # Fetch email statistics
    email_stats = get_email_stats()
    
    # Prepare data for visualizations
    if email_stats:
        # Convert email stats to DataFrame
        stats_df = pd.DataFrame.from_dict(
            email_stats, 
            orient='index', 
            columns=['Count']
        ).reset_index()
        stats_df.columns = ['Status', 'Count']
        
        # Pie Chart for Email Status Distribution
        with col1:
            st.subheader("📧 Email Status Distribution")
            fig_pie = px.pie(
                stats_df, 
                values='Count', 
                names='Status', 
                hole=0.3,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_pie.update_layout(
                title_x=0.5,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # Bar Chart in second column
        with col2:
            st.subheader("📊 Email Stats")
            fig_bar = px.bar(
                stats_df, 
                x='Status', 
                y='Count',
                color='Status',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_bar.update_layout(
                title_x=0.5,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    
    # Simulate user activity data
    def generate_user_activity_data():
        """Generate sample user activity data"""
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        login_data = [
            {'Month': month, 'New Users': max(0, 100 + int(50 * (1 + 0.1 * (i-2)**2))) } 
            for i, month in enumerate(months)
        ]
        return pd.DataFrame(login_data)
    
    # User Activity Line Chart
    st.subheader("📈 Monthly User Growth")
    user_activity_df = generate_user_activity_data()
    
    # Create line chart with area fill
    fig_line = px.area(
        user_activity_df, 
        x='Month', 
        y='New Users',
        line_shape='spline',
        color_discrete_sequence=['#636EFA']
    )
    fig_line.update_layout(
        title_x=0.5,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title='Month',
        yaxis_title='New Users'
    )
    st.plotly_chart(fig_line, use_container_width=True)
    
    # Additional Metrics Section
    st.subheader("🔍 Quick Metrics")
    
    # Create three columns for metrics
    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
    
    with metrics_col1:
        st.metric(
            label="Total Emails Sent", 
            value=sum(email_stats.values()) if email_stats else 0,
            delta="↑ 12.5%"
        )
    
    with metrics_col2:
        st.metric(
            label="Active Users", 
            value="1,245",
            delta="↑ 8.3%"
        )
    
    with metrics_col3:
        # Fixing the ZeroDivisionError by checking if total is 0
        total_sent = sum(email_stats.values()) if email_stats else 0
        if total_sent == 0:
            success_rate = "0%"  # Handle the case when total is zero
        else:
            success_rate = f"{(email_stats.get('success', 0)) / total_sent * 100:.2f}%"
        
        st.metric(
            label="Email Success Rate", 
            value=success_rate,
            delta="↑ 5.2%"
        )
    
    # Custom CSS for dashboard
    st.markdown("""
    <style>
    /* Dashboard Styling */
    .stMetric {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .stMetric > div {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    
    .stMetric div[data-testid="stMetricDelta"] {
        color: green;
    }
    </style>
    """, unsafe_allow_html=True)

# For standalone testing
if __name__ == "__main__":
    display_dashboard()
