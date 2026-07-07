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
            "Ocean Deep": {
      "app_bg": "linear-gradient(135deg, #0c2340, #1a5276, #2e86c1)",
      "sidebar_bg": "#0a1f33",
      "card_bg": "rgba(255, 255, 255, 0.08)",
      "text_color": "#E8F4FD",
      "title_color": "#85c1e9",
      "accent_color": "#85c1e9",
      "border_color": "#85c1e9",
      "kpi_value": "#FFFFFF",
      "kpi_label": "#AED6F1",
      "header_color": "#FFFFFF",
      "chart_bg": "rgba(255, 255, 255, 0.05)",
      "chart_text": "#E8F4FD",
      "chart_axis": "#E8F4FD",
      "button_bg": "#2e86c1",
      "button_hover": "#1a5276",
      "color_scale": "Blues"
    },
        }

THEMES = load_themes()

# Initialize theme in session state
if "theme" not in st.session_state:
    st.session_state.theme = "Cyberpunk"

# Get current theme colors
theme = THEMES[st.session_state.theme]

# Dynamic CSS with gradient background support
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');
    
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
    
    /* Main app background with gradient support */
    .stApp {{
        background: {theme['app_bg']};
        color: {theme['text_color']};
        min-height: 100vh;
        font-family: 'Poppins', sans-serif;
    }}
    
    /* Ensure content area has transparent background to show gradient */
    .stApp > div:first-child {{
        background: transparent !important;
    }}
    
    /* Apply Poppins font to all headings */
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Poppins', sans-serif !important;
    }}
    
    /* Main title with enhanced styling */
    .main-title {{
        font-family: 'Poppins', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: {theme['title_color']};
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
        letter-spacing: -0.5px;
    }}
    
    /* KPI cards with glassmorphism effect */
    .kpi-card {{
        background: {theme['card_bg']};
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .kpi-card:hover {{
        transform: translateY(-2px);
        box-shadow: 
            0 12px 48px rgba(0, 0, 0, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.15);
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
    
    /* AI Copilot specific styling - ensuring dark text */
    .ai-copilot-container {{
        background: rgba(255, 255, 255, 0.9) !important;
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 1.5rem;
        color: #1a1a1a !important;
        border: 1px solid rgba(0, 0, 0, 0.1);
    }}
    .ai-copilot-container * {{
        color: #1a1a1a !important;
    }}
    
    /* Custom card for AI content */
    .ai-card {{
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(0, 0, 0, 0.05);
    }}
    
    /* Metrics with glassmorphism */
    .stMetric {{
        background: {theme['card_bg']};
        backdrop-filter: blur(10px);
        padding: 1.2rem;
        border-radius: 0.75rem;
        color: {theme['text_color']};
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        transition: transform 0.2s ease;
    }}
    .stMetric:hover {{
        transform: translateY(-1px);
    }}
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {{
        color: {theme['header_color']} !important;
        font-weight: 600;
        letter-spacing: -0.3px;
    }}
    
    /* Dataframes and tables */
    .stDataFrame {{
        background: {theme['card_bg']};
        backdrop-filter: blur(10px);
        color: {theme['text_color']};
        border-radius: 0.5rem;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }}
    .stDataFrame th {{
        background: rgba(255, 255, 255, 0.1);
        color: {theme['header_color']};
        font-weight: 600;
    }}
    
    /* General text */
    p, span, div {{
        color: {theme['text_color']};
    }}
    
    /* Buttons with gradient */
    .stButton > button {{
        background: linear-gradient(135deg, {theme['button_bg']}, {theme['button_hover']});
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        transition: all 0.2s ease;
    }}
    .stButton > button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.25);
    }}
    
    /* ===== SIDEBAR - Consistent Dark Theme ===== */
    [data-testid="stSidebar"] {{
        background: {theme['sidebar_bg']} !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        padding: 1rem 0.5rem !important;
        min-height: 100vh !important;
    }}
    
    /* Sidebar - ALL TEXT should be light colored */
    [data-testid="stSidebar"] * {{
        color: #f0f0f0 !important;
    }}
    
    /* Sidebar Title - Bright accent color */
    [data-testid="stSidebar"] .stSidebarTitle {{
        color: {theme['sidebar_text']} !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.4) !important;
        letter-spacing: 0.5px !important;
    }}
    
    /* Sidebar Headings */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] h5,
    [data-testid="stSidebar"] h6 {{
        color: {theme['sidebar_text']} !important;
        font-weight: 600 !important;
        text-shadow: 0 1px 4px rgba(0, 0, 0, 0.3) !important;
    }}
    
    /* Sidebar Labels - Bright and readable */
    [data-testid="stSidebar"] label {{
        color: {theme['sidebar_text']} !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        opacity: 0.95;
    }}
    
    /* Sidebar radio buttons */
    [data-testid="stSidebar"] .stRadio > label {{
        color: {theme['sidebar_text']} !important;
        font-weight: 600 !important;
        padding: 10px 14px !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
        margin: 2px 0 !important;
        font-size: 1rem !important;
        border-left: 3px solid transparent;
    }}
    
    /* Sidebar radio button hover state */
    [data-testid="stSidebar"] .stRadio > label:hover {{
        background: rgba(255, 255, 255, 0.1) !important;
        transform: translateX(4px) !important;
        border-left-color: {theme['sidebar_hover']} !important;
        color: {theme['sidebar_hover']} !important;
    }}
    
    /* Selected radio button */
    [data-testid="stSidebar"] .stRadio [role="radiogroup"] > div {{
        background: rgba(255, 255, 255, 0.05) !important;
        padding: 6px !important;
        border-radius: 10px !important;
        margin: 6px 0 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }}
    
    /* Selected radio button text */
    [data-testid="stSidebar"] .stRadio [role="radiogroup"] > div[data-selected="true"] label {{
        color: {theme['sidebar_hover']} !important;
        background: rgba(255, 255, 255, 0.08) !important;
        border-left-color: {theme['sidebar_accent']} !important;
        border-left-width: 3px !important;
        border-left-style: solid !important;
    }}
    
    /* Sidebar radio button text color */
    [data-testid="stSidebar"] .stRadio [role="radiogroup"] > div label {{
        color: {theme['sidebar_text']} !important;
        transition: color 0.3s ease !important;
    }}
    
    /* Sidebar info and markdown */
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stInfo,
    [data-testid="stSidebar"] .stAlert {{
        color: {theme['sidebar_text']} !important;
    }}
    
    /* Sidebar selectbox */
    [data-testid="stSidebar"] .stSelectbox label {{
        color: {theme['sidebar_text']} !important;
    }}
    
    [data-testid="stSidebar"] .stSelectbox > div > div {{
        background: rgba(255, 255, 255, 0.05) !important;
        border-color: {theme['sidebar_text']}44 !important;
        color: {theme['sidebar_text']} !important;
    }}
    
    /* Sidebar divider */
    [data-testid="stSidebar"] hr {{
        border-color: {theme['sidebar_text']}44 !important;
        margin: 1rem 0 !important;
    }}
    
    /* Sidebar theme selector */
    [data-testid="stSidebar"] .stSelectbox [data-testid="stMarkdownContainer"] {{
        color: {theme['sidebar_text']} !important;
    }}
    
    /* Sidebar data source info */
    [data-testid="stSidebar"] .stInfo {{
        background: rgba(255, 255, 255, 0.05) !important;
        border-left-color: {theme['sidebar_accent']} !important;
        color: {theme['sidebar_text']} !important;
    }}
    
    /* Sidebar icon colors */
    [data-testid="stSidebar"] .stSidebarContent .stMarkdown * {{
        color: {theme['sidebar_text']} !important;
    }}
    
    /* Hover effects for all sidebar interactive elements */
    [data-testid="stSidebar"] *:hover {{
        transition: all 0.3s ease !important;
    }}
    
    /* Sidebar scrollbar */
    [data-testid="stSidebar"] ::-webkit-scrollbar-track {{
        background: rgba(255, 255, 255, 0.05) !important;
    }}
    
    [data-testid="stSidebar"] ::-webkit-scrollbar-thumb {{
        background: {theme['sidebar_text']}44 !important;
        border-radius: 10px !important;
    }}
    
    [data-testid="stSidebar"] ::-webkit-scrollbar-thumb:hover {{
        background: {theme['sidebar_text']}66 !important;
    }}
    
    /* Custom sidebar accent elements */
    .sidebar-accent {{
        color: {theme['sidebar_accent']} !important;
    }}
    
    .sidebar-hover {{
        color: {theme['sidebar_hover']} !important;
    }}
    
    /* Theme dropdown styling - white text on dark background */
    [data-testid="stSidebar"] .stSelectbox select {{
        background: rgba(0, 0, 0, 0.3) !important;
        color: #ffffff !important;
        border-color: {theme['sidebar_text']}44 !important;
    }}
    
    [data-testid="stSidebar"] .stSelectbox option {{
        background: #1a1a1a !important;
        color: #ffffff !important;
    }}
    
    /* Ensure AI Copilot text is dark */
    .ai-content {{
        color: #1a1a1a !important;
    }}
    .ai-content h1, .ai-content h2, .ai-content h3 {{
        color: #1a1a1a !important;
    }}
    .ai-content p, .ai-content span, .ai-content div {{
        color: #1a1a1a !important;
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

# Top-level app variable for deployment compatibility
app = st
application = st
