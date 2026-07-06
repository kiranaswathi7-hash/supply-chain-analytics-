"""
Manufacturing Supply Chain Analytics - Main Streamlit Application
Multi-page dashboard for ERP-style data analysis
"""

import streamlit as st
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Supply Chain Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for consistent styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .kpi-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .kpi-label {
        font-size: 1rem;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("📊 Supply Chain Analytics")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate to:",
    [
        "Executive Dashboard",
        "Inventory Risk Dashboard",
        "Supplier Analytics",
        "Production Risk Dashboard",
        "AI Copilot"
    ]
)

# Data loading info
st.sidebar.markdown("---")
st.sidebar.markdown("### Data Source")
st.sidebar.info("CSV files from 'csv files' directory")

# Page routing
if page == "Executive Dashboard":
    from pages import executive_dashboard
    executive_dashboard.show()
elif page == "Inventory Risk Dashboard":
    from pages import inventory_risk
    inventory_risk.show()
elif page == "Supplier Analytics":
    from pages import supplier_analytics
    supplier_analytics.show()
elif page == "Production Risk Dashboard":
    from pages import production_risk
    production_risk.show()
elif page == "AI Copilot":
    from pages import ai_copilot
    ai_copilot.show()
