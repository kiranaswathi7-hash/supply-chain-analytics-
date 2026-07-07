"""
Shared data loading utility for all dashboard pages
"""

import pandas as pd
import streamlit as st
import json
from pathlib import Path
from datetime import datetime

# Load theme configurations from JSON file
def load_themes():
    """Load themes from themes.json file"""
    theme_file = Path(__file__).parent.parent / "themes.json"
    try:
        with open(theme_file, 'r') as f:
            theme_data = json.load(f)
            return theme_data['themes']
    except FileNotFoundError:
        # Fallback to default themes if file not found
        return {
            "Peacock Deep": {
                "app_bg": "linear-gradient(135deg, #0a0e27, #0d1b3e, #1a2f5a)",
                "sidebar_bg": "#0a0e27",
                "card_bg": "rgba(255, 255, 255, 0.07)",
                "text_color": "#E8F0FE",
                "title_color": "#4fc3f7",
                "accent_color": "#4fc3f7",
                "border_color": "#4fc3f7",
                "kpi_value": "#FFFFFF",
                "kpi_label": "#B3E5FC",
                "header_color": "#FFFFFF",
                "chart_bg": "rgba(255, 255, 255, 0.05)",
                "chart_text": "#E8F0FE",
                "chart_axis": "#E8F0FE",
                "button_bg": "#0288d1",
                "button_hover": "#01579b",
                "color_scale": "Blues"
            }
        }

THEMES = load_themes()

def get_theme_colors():
    """Get current theme colors from session state"""
    theme_name = st.session_state.get("theme", "Cyberpunk")
    return THEMES.get(theme_name, THEMES["Cyberpunk"])

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_all_data():
    """
    Load all CSV files from the 'csv files' directory.
    Cached to improve performance across page navigations.
    """
    data_dir = Path(__file__).parent.parent / "csv files"
    
    data = {
        'items_master': pd.read_csv(data_dir / 'items_master.csv'),
        'suppliers': pd.read_csv(data_dir / 'suppliers.csv'),
        'customers': pd.read_csv(data_dir / 'customers.csv'),
        'inventory': pd.read_csv(data_dir / 'inventory.csv'),
        'purchase_orders': pd.read_csv(data_dir / 'purchase_orders.csv'),
        'goods_receipts': pd.read_csv(data_dir / 'goods_receipts.csv'),
        'sales_orders': pd.read_csv(data_dir / 'sales_orders.csv'),
        'production_orders': pd.read_csv(data_dir / 'production_orders.csv'),
        'production_order_components': pd.read_csv(data_dir / 'production_order_components.csv'),
        'bom_header': pd.read_csv(data_dir / 'bom_header.csv'),
        'bom_lines': pd.read_csv(data_dir / 'bom_lines.csv')
    }
    
    # Calculate available quantity (Current_Stock - Reserved_Qty)
    data['inventory']['Qty_On_Hand'] = data['inventory']['Current_Stock'] - data['inventory']['Reserved_Qty']
    data['sales_orders']['Order_Date'] = pd.to_datetime(data['sales_orders']['Order_Date'])
    data['sales_orders']['Requested_Delivery_Date'] = pd.to_datetime(data['sales_orders']['Requested_Delivery_Date'])
    data['purchase_orders']['Expected_Receipt_Date'] = pd.to_datetime(data['purchase_orders']['Expected_Receipt_Date'])
    data['goods_receipts']['Receipt_Date'] = pd.to_datetime(data['goods_receipts']['Receipt_Date'])
    data['production_orders']['Due_Date'] = pd.to_datetime(data['production_orders']['Due_Date'])
    
    return data

def calculate_kpi_metrics(data):
    """
    Calculate common KPI metrics used across dashboards.
    Returns a dictionary with pre-calculated metrics.
    """
    # Total Revenue (from all sales orders - pipeline value)
    data['sales_orders']['Revenue'] = data['sales_orders']['Ordered_Qty'] * data['sales_orders']['Unit_Price']
    total_revenue = data['sales_orders']['Revenue'].sum()
    
    # Open Sales Orders
    open_so = data['sales_orders'][data['sales_orders']['Sales_Status'] == 'Open'].shape[0]
    
    # Blocked Production Orders (any component shortage)
    blocked_mo = data['production_order_components'][data['production_order_components']['Shortage_Qty'] > 0]['Prod_Order_No'].nunique()
    
    # Total Production Orders
    total_mo = data['production_orders'].shape[0]
    
    # Low Stock Items (below reorder point)
    inv_with_master = data['inventory'].merge(data['items_master'][['Item_ID', 'Reorder_Point']], on='Item_ID', how='left')
    low_stock = inv_with_master[inv_with_master['Qty_On_Hand'] < inv_with_master['Reorder_Point']]['Item_ID'].nunique()
    
    # Critical Items (zero stock)
    critical_items = data['inventory'][data['inventory']['Qty_On_Hand'] == 0]['Item_ID'].nunique()
    
    # Overstock Items (more than 2x reorder point)
    overstock = inv_with_master[inv_with_master['Qty_On_Hand'] > (inv_with_master['Reorder_Point'] * 2)]['Item_ID'].nunique()
    
    # Supplier Delay Analysis
    po_gr = data['purchase_orders'].merge(
        data['goods_receipts'][['PO_No', 'Receipt_Date']], 
        on='PO_No', 
        how='left'
    )
    po_gr['Delay_Days'] = (po_gr['Receipt_Date'] - po_gr['Expected_Receipt_Date']).dt.days
    delayed_pos = po_gr[po_gr['Delay_Days'] > 0].shape[0]
    
    # Components Short
    components_short = data['production_order_components'][data['production_order_components']['Shortage_Qty'] > 0].shape[0]
    
    # Overall Risk Score (weighted)
    inventory_risk = (low_stock / data['items_master'].shape[0]) * 100 if data['items_master'].shape[0] > 0 else 0
    production_risk = (blocked_mo / total_mo) * 100 if total_mo > 0 else 0
    supplier_risk = (delayed_pos / data['purchase_orders'].shape[0]) * 100 if data['purchase_orders'].shape[0] > 0 else 0
    overall_risk = (inventory_risk * 0.3) + (production_risk * 0.4) + (supplier_risk * 0.3)
    
    return {
        'total_revenue': total_revenue,
        'open_so': open_so,
        'blocked_mo': blocked_mo,
        'total_mo': total_mo,
        'low_stock': low_stock,
        'critical_items': critical_items,
        'overstock': overstock,
        'delayed_pos': delayed_pos,
        'components_short': components_short,
        'overall_risk': overall_risk,
        'inventory_risk': inventory_risk,
        'production_risk': production_risk,
        'supplier_risk': supplier_risk,
        'po_gr': po_gr  # Merged PO and goods receipts for further analysis
    }
