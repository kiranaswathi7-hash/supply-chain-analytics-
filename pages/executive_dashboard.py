"""
Executive Dashboard Page
High-level KPIs and trends for supply chain leadership
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pages.data_loader import load_all_data, calculate_kpi_metrics, get_theme_colors

def show():
    st.markdown('<h1 class="main-title">📊 Executive Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Get current theme colors
    theme = get_theme_colors()
    
    # Load data
    data = load_all_data()
    metrics = calculate_kpi_metrics(data)
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">${metrics['total_revenue']:,.0f}</div>
            <div class="kpi-label">Total Revenue (Pipeline)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{metrics['open_so']:,}</div>
            <div class="kpi-label">Open Sales Orders</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{metrics['blocked_mo']:,}</div>
            <div class="kpi-label">Blocked Production Orders</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        risk_color = "#ff6b6b" if metrics['overall_risk'] > 50 else "#51cf66" if metrics['overall_risk'] < 25 else "#ffd43b"
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: {risk_color};">
            <div class="kpi-value" style="color: {risk_color};">{metrics['overall_risk']:.1f}</div>
            <div class="kpi-label">Overall Risk Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts Row
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📈 Sales Trend Over Time")
        
        # Prepare sales trend data
        sales_trend = data['sales_orders'].copy()
        sales_trend['Order_Month'] = sales_trend['Order_Date'].dt.to_period('M').astype(str)
        monthly_sales = sales_trend.groupby('Order_Month').agg({
            'Revenue': 'sum',
            'Ordered_Qty': 'sum'
        }).reset_index()
        monthly_sales = monthly_sales.sort_values('Order_Month')
        
        fig_sales = px.line(
            monthly_sales,
            x='Order_Month',
            y='Revenue',
            title='Monthly Revenue Trend',
            markers=True
        )
        fig_sales.update_layout(
            xaxis_title="Month",
            yaxis_title="Revenue ($)",
            hovermode='x unified',
            plot_bgcolor=theme['chart_bg'],
            paper_bgcolor=theme['chart_bg'],
            font=dict(color=theme['chart_text']),
            xaxis=dict(color=theme['chart_axis']),
            yaxis=dict(color=theme['chart_axis'])
        )
        st.plotly_chart(fig_sales, use_container_width=True)
    
    with col_right:
        st.subheader("🎯 Risk Summary by Category")
        
        # Prepare risk category data
        risk_data = pd.DataFrame({
            'Category': ['Inventory Risk', 'Production Risk', 'Supplier Risk'],
            'Score': [metrics['inventory_risk'], metrics['production_risk'], metrics['supplier_risk']]
        })
        
        fig_risk = px.pie(
            risk_data,
            values='Score',
            names='Category',
            title='Risk Distribution',
            hole=0.4
        )
        fig_risk.update_traces(textposition='inside', textinfo='percent+label')
        fig_risk.update_layout(
            showlegend=True,
            plot_bgcolor=theme['chart_bg'],
            paper_bgcolor=theme['chart_bg'],
            font=dict(color=theme['chart_text']),
            legend=dict(font=dict(color=theme['chart_text']))
        )
        st.plotly_chart(fig_risk, use_container_width=True)
    
    st.markdown("---")
    
    # Additional Metrics Row
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.metric("Low Stock Items", metrics['low_stock'], delta=None)
        st.metric("Critical Items (Zero Stock)", metrics['critical_items'], delta=None)
    
    with col_b:
        st.metric("Overstock Items", metrics['overstock'], delta=None)
        st.metric("Delayed Purchase Orders", metrics['delayed_pos'], delta=None)
    
    with col_c:
        st.metric("Total Production Orders", metrics['total_mo'], delta=None)
        st.metric("Component Shortages", metrics['components_short'], delta=None)
    
    st.markdown("---")
    
    # Sales Orders by Status
    st.subheader("📋 Sales Orders by Status")
    so_status = data['sales_orders']['Sales_Status'].value_counts().reset_index()
    so_status.columns = ['Status', 'Count']
    
    fig_so_status = px.bar(
        so_status,
        x='Status',
        y='Count',
        title='Sales Orders Distribution',
        color='Count',
        color_continuous_scale=theme['color_scale']
    )
    fig_so_status.update_layout(
        xaxis_title="Status",
        yaxis_title="Count",
        plot_bgcolor=theme['chart_bg'],
        paper_bgcolor=theme['chart_bg'],
        font=dict(color=theme['chart_text']),
        xaxis=dict(color=theme['chart_axis']),
        yaxis=dict(color=theme['chart_axis'])
    )
    st.plotly_chart(fig_so_status, use_container_width=True)
