"""
Inventory Risk Dashboard Page
Stock levels, reorder point analysis, and critical inventory items
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pages.data_loader import load_all_data, calculate_kpi_metrics, get_theme_colors

def show():
    st.markdown('<h1 class="main-title">📦 Inventory Risk Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Get current theme colors
    theme = get_theme_colors()
    
    # Load data
    data = load_all_data()
    metrics = calculate_kpi_metrics(data)
    
    # KPI Cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{metrics['low_stock']:,}</div>
            <div class="kpi-label">Low Stock Items</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #ff6b6b;">
            <div class="kpi-value" style="color: #ff6b6b;">{metrics['critical_items']:,}</div>
            <div class="kpi-label">Critical Items (Zero Stock)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #ffd43b;">
            <div class="kpi-value" style="color: #ffd43b;">{metrics['overstock']:,}</div>
            <div class="kpi-label">Overstock Items</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Stock Levels by Location
    st.subheader("🏭 Stock Levels by Warehouse/Location")
    
    location_stock = data['inventory'].groupby('Warehouse')['Qty_On_Hand'].sum().reset_index()
    location_stock = location_stock.sort_values('Qty_On_Hand', ascending=False)
    
    fig_location = px.bar(
        location_stock,
        x='Warehouse',
        y='Qty_On_Hand',
        title='Total Stock by Location',
        color='Qty_On_Hand',
        color_continuous_scale=theme['color_scale']
    )
    fig_location.update_layout(
        xaxis_title="Location",
        yaxis_title="Quantity on Hand",
        plot_bgcolor=theme['chart_bg'],
        paper_bgcolor=theme['chart_bg'],
        font=dict(color=theme['chart_text']),
        xaxis=dict(color=theme['chart_axis']),
        yaxis=dict(color=theme['chart_axis'])
    )
    st.plotly_chart(fig_location, use_container_width=True)
    
    st.markdown("---")
    
    # Critical Inventory Items Table
    st.subheader("⚠️ Critical Inventory Items (Below Reorder Point)")
    
    # Merge inventory with items_master to get reorder point
    inv_analysis = data['inventory'].merge(
        data['items_master'][['Item_ID', 'Item_Type', 'Reorder_Point', 'Item_Name']],
        on='Item_ID',
        how='left'
    )
    
    # Calculate shortage
    inv_analysis['Shortage'] = inv_analysis['Reorder_Point'] - inv_analysis['Qty_On_Hand']
    inv_analysis['Shortage'] = inv_analysis['Shortage'].apply(lambda x: max(0, x))
    
    # Filter items below reorder point
    critical_items = inv_analysis[inv_analysis['Qty_On_Hand'] < inv_analysis['Reorder_Point']].copy()
    
    # Add risk category
    def get_risk_category(row):
        if row['Qty_On_Hand'] == 0:
            return 'Critical (Zero Stock)'
        elif row['Shortage'] > row['Reorder_Point']:
            return 'Severe Shortage'
        else:
            return 'Low Stock'
    
    critical_items['Risk_Category'] = critical_items.apply(get_risk_category, axis=1)
    
    if len(critical_items) > 0:
        # Display filters
        col_filter1, col_filter2 = st.columns(2)
        
        with col_filter1:
            filter_location = st.selectbox(
                'Filter by Location',
                ['All'] + list(critical_items['Warehouse'].unique())
            )
        
        with col_filter2:
            filter_risk = st.selectbox(
                'Filter by Risk Category',
                ['All'] + list(critical_items['Risk_Category'].unique())
            )
        
        # Apply filters
        display_items = critical_items.copy()
        if filter_location != 'All':
            display_items = display_items[display_items['Warehouse'] == filter_location]
        if filter_risk != 'All':
            display_items = display_items[display_items['Risk_Category'] == filter_risk]
        
        # Prepare display columns
        display_cols = [
            'Item_ID',
            'Item_Name',
            'Item_Type',
            'Warehouse',
            'Qty_On_Hand',
            'Reorder_Point',
            'Shortage',
            'Risk_Category'
        ]
        
        display_items = display_items[display_cols].sort_values('Shortage', ascending=False)
        
        st.dataframe(
            display_items,
            use_container_width=True,
            column_config={
                'Qty_On_Hand': st.column_config.NumberColumn(format="%d"),
                'Reorder_Point': st.column_config.NumberColumn(format="%d"),
                'Shortage': st.column_config.NumberColumn(format="%d"),
                'Risk_Category': st.column_config.SelectboxColumn(
                    options=['Critical (Zero Stock)', 'Severe Shortage', 'Low Stock']
                )
            }
        )
        
        # Download button
        csv = display_items.to_csv(index=False)
        st.download_button(
            label="Download Critical Items CSV",
            data=csv,
            file_name='critical_inventory_items.csv',
            mime='text/csv'
        )
    else:
        st.success("✅ No critical inventory items found - all items are above reorder point!")
    
    st.markdown("---")
    
    # Inventory Health Overview
    st.subheader("📊 Inventory Health Overview")
    
    # Calculate inventory health metrics
    total_items = data['items_master'].shape[0]
    healthy_items = total_items - metrics['low_stock']
    
    health_data = pd.DataFrame({
        'Category': ['Healthy', 'Low Stock', 'Critical (Zero Stock)', 'Overstock'],
        'Count': [
            healthy_items,
            metrics['low_stock'] - metrics['critical_items'],
            metrics['critical_items'],
            metrics['overstock']
        ]
    })
    
    fig_health = px.pie(
        health_data,
        values='Count',
        names='Category',
        title='Inventory Health Distribution',
        hole=0.4,
        color_discrete_map={
            'Healthy': '#51cf66',
            'Low Stock': '#ffd43b',
            'Critical (Zero Stock)': '#ff6b6b',
            'Overstock': '#845ef7'
        }
    )
    fig_health.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_health, use_container_width=True)
