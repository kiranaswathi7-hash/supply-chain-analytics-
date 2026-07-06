"""
Manufacturing Supply Chain Analytics - Main Streamlit Application
Multi-page dashboard for ERP-style data analysis
"""

import streamlit as st
import json
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Supply Chain Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load theme configurations from JSON file
def load_themes():
    """Load themes from themes.json file"""
    theme_file = Path(__file__).parent / "themes.json"
    try:
        with open(theme_file, 'r') as f:
            theme_data = json.load(f)
            return theme_data['themes']
    except FileNotFoundError:
        # Fallback to default themes if file not found
        return {
            "High-Tech Dark": {
                "app_bg": "#121212",
                "sidebar_bg": "#2d1b4e",
                "card_bg": "#1E1E1E",
                "text_color": "#E1E1E1",
                "title_color": "#8931EF",
                "accent_color": "#8931EF",
                "border_color": "#8931EF",
                "kpi_value": "#FFFFFF",
                "kpi_label": "#E0E0E0",
                "header_color": "#FFFFFF",
                "chart_bg": "#1E1E1E",
                "chart_text": "#E0E0E0",
                "chart_axis": "#E0E0E0",
                "button_bg": "#8931EF",
                "button_hover": "#7C2DD9",
                "color_scale": "Purples"
            }
        }

THEMES = load_themes()

# Initialize theme in session state
if "theme" not in st.session_state:
    st.session_state.theme = "Peacock Deep"

# Get current theme colors
theme = THEMES[st.session_state.theme]

# Dynamic CSS based on selected theme
st.markdown(f"""
<style>
    /* Hide Streamlit default header/menu */
    .stApp [data-testid="stHeader"] {{
        display: none;
    }}
    .stApp [data-testid="stTopLevelHeader"] {{
        display: none;
    }}
    
    /* Hide sidebar menu elements */
    [data-testid="stSidebar"] [data-testid="stSidebarHeader"] {{
        display: none;
    }}
    [data-testid="stSidebar"] [data-testid="collapsedControl"] {{
        display: none;
    }}
    [data-testid="stSidebar"] [data-testid="sidebarNavigation"] {{
        display: none;
    }}
    
    /* Main app background */
    .stApp {{
        background-color: {theme['app_bg']};
        color: {theme['text_color']};
    }}
    
    /* Main title with enhanced styling */
    .main-title {{
        font-size: 2.5rem;
        font-weight: bold;
        color: {theme['title_color']};
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
        letter-spacing: -0.5px;
    }}
    
    /* KPI cards with 3D effect */
    .kpi-card {{
        background: linear-gradient(145deg, {theme['card_bg']}, {theme['card_bg']}dd);
        padding: 1.5rem;
        border-radius: 1rem;
        border-left: 4px solid {theme['border_color']};
        box-shadow: 
            0 4px 16px rgba(0, 0, 0, 0.1),
            0 2px 8px rgba(0, 0, 0, 0.05),
            inset 0 1px 2px rgba(255, 255, 255, 0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .kpi-card:hover {{
        transform: translateY(-2px);
        box-shadow: 
            0 8px 24px rgba(0, 0, 0, 0.15),
            0 4px 12px rgba(0, 0, 0, 0.08),
            inset 0 1px 2px rgba(255, 255, 255, 0.15);
    }}
    .kpi-value {{
        font-size: 2.5rem;
        font-weight: bold;
        color: {theme['kpi_value']};
    }}
    .kpi-label {{
        font-size: 1rem;
        color: {theme['kpi_label']};
        font-weight: 500;
    }}
    
    /* Metrics with enhanced styling */
    .stMetric {{
        background: linear-gradient(145deg, {theme['card_bg']}, {theme['card_bg']}dd);
        padding: 1.2rem;
        border-radius: 0.75rem;
        color: {theme['text_color']};
        box-shadow: 
            0 2px 12px rgba(0, 0, 0, 0.08),
            inset 0 1px 2px rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(128, 128, 128, 0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .stMetric:hover {{
        transform: translateY(-1px);
        box-shadow: 
            0 4px 16px rgba(0, 0, 0, 0.12),
            inset 0 1px 2px rgba(255, 255, 255, 0.15);
    }}
    .stMetric label {{
        color: {theme['kpi_label']};
        font-weight: 600;
        font-size: 0.9rem;
    }}
    .stMetric .stMetricValue {{
        color: {theme['kpi_value']};
        font-weight: 700;
        font-size: 1.8rem;
    }}
    
    /* Headers - all levels with enhanced styling */
    h1, h2, h3, h4, h5, h6 {{
        color: {theme['header_color']} !important;
        font-weight: 600;
        letter-spacing: -0.3px;
    }}
    
    /* Subheaders */
    .css-1d391kg {{
        color: {theme['text_color']} !important;
    }}
    
    /* Dataframes and tables with enhanced styling */
    .stDataFrame {{
        background-color: {theme['card_bg']};
        color: {theme['text_color']};
        border-radius: 0.5rem;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }}
    .stDataFrame th {{
        background: {theme['accent_color']}22;
        color: {theme['header_color']};
        font-weight: 600;
    }}
    .stDataFrame td {{
        border-bottom: 1px solid rgba(128, 128, 128, 0.1);
    }}
    
    /* General text */
    p, span, div {{
        color: {theme['text_color']};
    }}
    
    /* Buttons with gradient and 3D effect */
    .stButton > button {{
        background: linear-gradient(135deg, {theme['button_bg']}, {theme['button_hover']});
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        box-shadow: 
            0 4px 12px rgba(0, 0, 0, 0.2),
            inset 0 1px 2px rgba(255, 255, 255, 0.2);
        transition: all 0.2s ease;
    }}
    .stButton > button:hover {{
        background: linear-gradient(135deg, {theme['button_hover']}, {theme['button_bg']});
        transform: translateY(-1px);
        box-shadow: 
            0 6px 16px rgba(0, 0, 0, 0.25),
            inset 0 1px 2px rgba(255, 255, 255, 0.3);
    }}
    
    /* Selectboxes and inputs */
    .stSelectbox, .stMultiSelect {{
        color: {theme['text_color']};
    }}
    
    /* Sidebar styling with enhanced 3D effects */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {theme['sidebar_bg']}, {theme['sidebar_bg']}dd);
        color: #ffffff;
        box-shadow: 4px 0 16px rgba(0, 0, 0, 0.2);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }}
    [data-testid="stSidebar"] * {{
        color: #ffffff !important;
    }}
    [data-testid="stSidebar"] .css-1d391kg {{
        color: #ffffff !important;
        font-weight: 600;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
    }}
    [data-testid="stSidebar"] label {{
        color: #ffffff !important;
        font-weight: 500;
    }}
    [data-testid="stSidebar"] .stRadio > label {{
        color: #ffffff !important;
        font-weight: 600;
        padding: 10px 14px;
        border-radius: 8px;
        transition: all 0.3s ease;
        margin: 2px 0;
    }}
    [data-testid="stSidebar"] .stRadio > div {{
        color: #ffffff !important;
    }}
    [data-testid="stSidebar"] .stRadio > label:hover {{
        background: rgba(255, 255, 255, 0.15);
        transform: translateX(4px);
    }}
    [data-testid="stSidebar"] .stRadio [role="radiogroup"] > div {{
        background: rgba(255, 255, 255, 0.05);
        padding: 6px;
        border-radius: 10px;
        margin: 6px 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }}
    [data-testid="stSidebar"] .stRadio [role="radiogroup"] > div:hover {{
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(255, 255, 255, 0.2);
    }}
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

# Theme selector at bottom of sidebar with beautiful styling
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎨 Theme")
selected_theme = st.sidebar.selectbox(
    "Select Theme",
    list(THEMES.keys()),
    index=list(THEMES.keys()).index(st.session_state.theme),
    key="theme_selector"
)

if selected_theme != st.session_state.theme:
    st.session_state.theme = selected_theme
    st.rerun()

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

if __name__ == "__main__":
    pass
