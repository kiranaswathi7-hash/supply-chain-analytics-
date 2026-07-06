"""
Production Risk Dashboard Page
Manufacturing order status, component shortages, and production blocking analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pages.data_loader import load_all_data, calculate_kpi_metrics, get_theme_colors

def show():
    st.markdown('<h1 class="main-title">🏭 Production Risk Dashboard</h1>', unsafe_allow_html=True)
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
            <div class="kpi-value">{metrics['total_mo']:,}</div>
            <div class="kpi-label">Total Manufacturing Orders</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #ff6b6b;">
            <div class="kpi-value" style="color: #ff6b6b;">{metrics['blocked_mo']:,}</div>
            <div class="kpi-label">Blocked Manufacturing Orders</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #ffd43b;">
            <div class="kpi-value" style="color: #ffd43b;">{metrics['components_short']:,}</div>
            <div class="kpi-label">Component Shortages</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Component Shortage Heatmap
    st.subheader("🔥 Component Shortage Heatmap")
    
    # Prepare heatmap data
    shortage_data = data['production_order_components'][
        data['production_order_components']['Shortage_Qty'] > 0
    ].copy()
    
    if len(shortage_data) > 0:
        # Pivot for heatmap
        heatmap_pivot = shortage_data.pivot_table(
            index='Prod_Order_No',
            columns='Component_Item_ID',
            values='Shortage_Qty',
            fill_value=0
        )
        
        # Limit to top 20 MOs and top 15 components for readability
        top_mo = shortage_data['Prod_Order_No'].value_counts().head(20).index
        top_components = shortage_data['Component_Item_ID'].value_counts().head(15).index
        
        heatmap_pivot = heatmap_pivot.loc[top_mo, top_components]
        
        fig_heatmap = px.imshow(
            heatmap_pivot,
            title='Component Shortages by Production Order',
            color_continuous_scale=theme['color_scale'],
            labels=dict(x="Component Item", y="Production Order", color="Shortage Qty"),
            aspect='auto'
        )
        fig_heatmap.update_layout(
            xaxis_title="Component Item ID",
            yaxis_title="Production Order No",
            plot_bgcolor=theme['chart_bg'],
            paper_bgcolor=theme['chart_bg'],
            font=dict(color=theme['chart_text']),
            xaxis=dict(color=theme['chart_axis']),
            yaxis=dict(color=theme['chart_axis'])
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
    else:
        st.success("✅ No component shortages found - all production orders can proceed!")
    
    st.markdown("---")
    
    # Blocked Production Orders Table
    st.subheader("🚫 Blocked Production Orders with Component Shortages")
    
    # Merge production orders with components and items master
    blocked_mo_data = data['production_order_components'][
        data['production_order_components']['Shortage_Qty'] > 0
    ].copy()
    
    if len(blocked_mo_data) > 0:
        # Join with production orders to get FG item and status
        blocked_mo_full = blocked_mo_data.merge(
            data['production_orders'][['Prod_Order_No', 'FG_Item_ID', 'Production_Line', 'Planned_Qty', 'Due_Date', 'Status']],
            on='Prod_Order_No',
            how='left'
        )
        
        # Join with items master to get component description
        blocked_mo_full = blocked_mo_full.merge(
            data['items_master'][['Item_ID', 'Item_Name', 'Item_Type']],
            left_on='Component_Item_ID',
            right_on='Item_ID',
            how='left'
        )
        
        # Prepare display columns
        display_cols = [
            'Prod_Order_No',
            'FG_Item_ID',
            'Production_Line',
            'Planned_Qty',
            'Due_Date',
            'Status',
            'Component_Item_ID',
            'Item_Name',
            'Required_Qty',
            'Available_Qty',
            'Shortage_Qty'
        ]
        
        blocked_mo_display = blocked_mo_full[display_cols].sort_values(['Prod_Order_No', 'Shortage_Qty'], ascending=[True, False])
        
        # Filters
        col_filter1, col_filter2 = st.columns(2)
        
        with col_filter1:
            filter_line = st.selectbox(
                'Filter by Production Line',
                ['All'] + list(blocked_mo_full['Production_Line'].unique())
            )
        
        with col_filter2:
            filter_status = st.selectbox(
                'Filter by Status',
                ['All'] + list(blocked_mo_full['Status'].unique())
            )
        
        # Apply filters
        display_blocked = blocked_mo_display.copy()
        if filter_line != 'All':
            display_blocked = display_blocked[display_blocked['Production_Line'] == filter_line]
        if filter_status != 'All':
            display_blocked = display_blocked[display_blocked['Status'] == filter_status]
        
        st.dataframe(
            display_blocked,
            use_container_width=True,
            column_config={
                'Planned_Qty': st.column_config.NumberColumn(format="%d"),
                'Required_Qty': st.column_config.NumberColumn(format="%d"),
                'Available_Qty': st.column_config.NumberColumn(format="%d"),
                'Shortage_Qty': st.column_config.NumberColumn(format="%d"),
                'Due_Date': st.column_config.DateColumn(format="YYYY-MM-DD")
            }
        )
        
        # Download button
        csv = display_blocked.to_csv(index=False)
        st.download_button(
            label="Download Blocked MOs CSV",
            data=csv,
            file_name='blocked_production_orders.csv',
            mime='text/csv'
        )
    else:
        st.success("✅ No blocked production orders found!")
    
    st.markdown("---")
    
    # Production Orders by Status
    st.subheader("📊 Production Orders by Status")
    
    mo_status = data['production_orders']['Status'].value_counts().reset_index()
    mo_status.columns = ['Status', 'Count']
    
    fig_mo_status = px.bar(
        mo_status,
        x='Status',
        y='Count',
        title='Production Orders Distribution',
        color='Count',
        color_continuous_scale=theme['color_scale']
    )
    fig_mo_status.update_layout(
        xaxis_title="Status",
        yaxis_title="Count",
        plot_bgcolor=theme['chart_bg'],
        paper_bgcolor=theme['chart_bg'],
        font=dict(color=theme['chart_text']),
        xaxis=dict(color=theme['chart_axis']),
        yaxis=dict(color=theme['chart_axis'])
    )
    st.plotly_chart(fig_mo_status, use_container_width=True)
    
    st.markdown("---")
    
    # Top Shortage Components
    st.subheader("🔝 Top Components with Most Shortages")
    
    component_shortage_summary = data['production_order_components'][
        data['production_order_components']['Shortage_Qty'] > 0
    ].groupby('Component_Item_ID').agg({
        'Shortage_Qty': ['sum', 'count'],
        'Required_Qty': 'sum'
    }).reset_index()
    component_shortage_summary.columns = ['Component_Item_ID', 'Total_Shortage_Qty', 'Affected_MOs', 'Total_Required_Qty']
    component_shortage_summary = component_shortage_summary.sort_values('Total_Shortage_Qty', ascending=False).head(10)
    
    if len(component_shortage_summary) > 0:
        # Add item descriptions
        component_shortage_summary = component_shortage_summary.merge(
            data['items_master'][['Item_ID', 'Item_Name']],
            left_on='Component_Item_ID',
            right_on='Item_ID',
            how='left'
        )
        
        fig_top_shortage = px.bar(
            component_shortage_summary,
            x='Total_Shortage_Qty',
            y='Item_Name',
            title='Top 10 Components by Total Shortage Quantity',
            orientation='h',
            color='Total_Shortage_Qty',
            color_continuous_scale=theme['color_scale']
        )
        fig_top_shortage.update_layout(
        xaxis_title="Total Shortage Quantity",
        yaxis_title="Component",
        plot_bgcolor=theme['chart_bg'],
        paper_bgcolor=theme['chart_bg'],
        font=dict(color=theme['chart_text']),
        xaxis=dict(color=theme['chart_axis']),
        yaxis=dict(color=theme['chart_axis'])
    )
        st.plotly_chart(fig_top_shortage, use_container_width=True)
    else:
        st.info("No component shortages to display.")
