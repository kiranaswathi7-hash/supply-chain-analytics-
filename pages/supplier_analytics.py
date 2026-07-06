"""
Supplier Analytics Page
Supplier performance, lead times, and delay analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pages.data_loader import load_all_data, calculate_kpi_metrics

def show():
    st.markdown('<h1 class="main-title">🚚 Supplier Analytics</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Load data
    data = load_all_data()
    metrics = calculate_kpi_metrics(data)
    
    # Calculate supplier-specific metrics
    po_gr = metrics['po_gr'].copy()
    
    # Merge with supplier info
    po_gr_supplier = po_gr.merge(
        data['suppliers'][['Supplier_ID', 'Supplier_Name']],
        on='Supplier_ID',
        how='left'
    )
    
    # Calculate per-supplier metrics
    supplier_metrics = po_gr_supplier.groupby('Supplier_ID').agg({
        'Supplier_Name': 'first',
        'Delay_Days': ['count', 'sum', 'mean', lambda x: (x > 0).sum()]
    }).reset_index()
    supplier_metrics.columns = ['Supplier_ID', 'Supplier_Name', 'Total_POs', 'Total_Delay_Days', 'Avg_Delay_Days', 'Delayed_POs']
    supplier_metrics['On_Time_Rate'] = ((supplier_metrics['Total_POs'] - supplier_metrics['Delayed_POs']) / supplier_metrics['Total_POs'] * 100).round(2)
    supplier_metrics['Delay_Rate'] = (supplier_metrics['Delayed_POs'] / supplier_metrics['Total_POs'] * 100).round(2)
    
    # Calculate average lead time (Receipt_Date - PO_Date if available, otherwise use Expected_Date as proxy)
    # Since we don't have PO_Date, we'll use Expected_Date as a proxy for lead time calculation
    po_gr_supplier['Lead_Time_Days'] = (po_gr_supplier['Receipt_Date'] - po_gr_supplier['Expected_Date']).dt.days
    avg_lead_time = po_gr_supplier['Lead_Time_Days'].mean()
    
    # Suppliers at risk (delay rate > 20%)
    suppliers_at_risk = supplier_metrics[supplier_metrics['Delay_Rate'] > 20].shape[0]
    
    # KPI Cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{avg_lead_time:.1f} days</div>
            <div class="kpi-label">Avg Lead Time (Delay)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #ff6b6b;">
            <div class="kpi-value" style="color: #ff6b6b;">{metrics['delayed_pos']:,}</div>
            <div class="kpi-label">Delayed POs</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #ff6b6b;">
            <div class="kpi-value" style="color: #ff6b6b;">{suppliers_at_risk:,}</div>
            <div class="kpi-label">Suppliers At Risk (>20% delay)</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Supplier Ranking Chart
    st.subheader("📊 Supplier Ranking by On-Time Delivery")
    
    supplier_ranking = supplier_metrics.sort_values('On_Time_Rate', ascending=True).head(15)
    
    fig_ranking = px.bar(
        supplier_ranking,
        x='On_Time_Rate',
        y='Supplier_Name',
        title='Supplier On-Time Delivery Rate (Bottom 15)',
        orientation='h',
        color='On_Time_Rate',
        color_continuous_scale='RdYlGn',
        range_color=[0, 100]
    )
    fig_ranking.update_layout(xaxis_title="On-Time Delivery Rate (%)", yaxis_title="Supplier")
    st.plotly_chart(fig_ranking, use_container_width=True)
    
    st.markdown("---")
    
    # Delay Analysis Table
    st.subheader("📋 Delay Analysis (Expected vs Actual Receipt)")
    
    # Prepare delay analysis table
    delay_analysis = po_gr_supplier[po_gr_supplier['Delay_Days'] > 0].copy()
    delay_analysis = delay_analysis.sort_values('Delay_Days', ascending=False)
    
    delay_cols = ['PO_No', 'Supplier_ID', 'Supplier_Name', 'Item_ID', 'Expected_Date', 'Receipt_Date', 'Delay_Days']
    delay_analysis = delay_analysis[delay_cols]
    
    if len(delay_analysis) > 0:
        # Filters
        col_filter1, col_filter2 = st.columns(2)
        
        with col_filter1:
            filter_supplier = st.selectbox(
                'Filter by Supplier',
                ['All'] + list(delay_analysis['Supplier_Name'].unique())
            )
        
        with col_filter2:
            min_delay = st.number_input(
                'Minimum Delay Days',
                min_value=0,
                max_value=int(delay_analysis['Delay_Days'].max()),
                value=0
            )
        
        # Apply filters
        display_delays = delay_analysis.copy()
        if filter_supplier != 'All':
            display_delays = display_delays[display_delays['Supplier_Name'] == filter_supplier]
        display_delays = display_delays[display_delays['Delay_Days'] >= min_delay]
        
        st.dataframe(
            display_delays,
            use_container_width=True,
            column_config={
                'Delay_Days': st.column_config.NumberColumn(format="%d"),
                'Expected_Date': st.column_config.DateColumn(format="YYYY-MM-DD"),
                'Receipt_Date': st.column_config.DateColumn(format="YYYY-MM-DD")
            }
        )
        
        # Download button
        csv = display_delays.to_csv(index=False)
        st.download_button(
            label="Download Delay Analysis CSV",
            data=csv,
            file_name='supplier_delay_analysis.csv',
            mime='text/csv'
        )
    else:
        st.success("✅ No delayed purchase orders found!")
    
    st.markdown("---")
    
    # Supplier Performance Summary Table
    st.subheader("🏆 Supplier Performance Summary")
    
    supplier_display = supplier_metrics[['Supplier_ID', 'Supplier_Name', 'Total_POs', 'Delayed_POs', 'On_Time_Rate', 'Avg_Delay_Days', 'Delay_Rate']].copy()
    supplier_display = supplier_display.sort_values('Delay_Rate', ascending=False)
    
    st.dataframe(
        supplier_display,
        use_container_width=True,
        column_config={
            'On_Time_Rate': st.column_config.ProgressColumn(
                'On-Time Rate',
                format="%.1f%%",
                min_value=0,
                max_value=100
            ),
            'Avg_Delay_Days': st.column_config.NumberColumn(format="%.1f"),
            'Delay_Rate': st.column_config.NumberColumn(format="%.1f%%")
        }
    )
    
    st.markdown("---")
    
    # Delay Distribution Chart
    st.subheader("📈 Delay Distribution by Supplier")
    
    fig_delay_dist = px.box(
        po_gr_supplier,
        x='Supplier_Name',
        y='Delay_Days',
        title='Delay Days Distribution by Supplier',
        color='Supplier_Name'
    )
    fig_delay_dist.update_layout(xaxis_title="Supplier", yaxis_title="Delay Days")
    st.plotly_chart(fig_delay_dist, use_container_width=True)
