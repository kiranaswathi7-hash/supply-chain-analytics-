"""
AI Copilot / Chatbot Page
Rule-based natural language query interface for supply chain questions
"""

import streamlit as st
import pandas as pd
import re
from pages.data_loader import load_all_data, calculate_kpi_metrics

def show():
    st.markdown('<h1 class="main-title">🤖 AI Copilot</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("""
    <div style="padding: 1rem; background-color: #f0f2f6; border-radius: 0.5rem; margin-bottom: 1rem;">
        <strong>Ask me questions about your supply chain data:</strong>
        <ul style="margin-top: 0.5rem;">
            <li>"Which items are below reorder point?"</li>
            <li>"Which production orders are blocked?"</li>
            <li>"Which supplier has maximum delay?"</li>
            <li>"Can we fulfill SO<order_id>?"</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    data = load_all_data()
    metrics = calculate_kpi_metrics(data)
    
    # Chat interface
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your supply chain..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process the query
        with st.chat_message("assistant"):
            response = process_query(prompt, data, metrics)
            st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    # Clear chat button
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

def process_query(query, data, metrics):
    """
    Process natural language query using keyword/intent matching.
    Returns a formatted response based on the query type.
    """
    query_lower = query.lower().strip()
    
    # Query 1: Items below reorder point
    if re.search(r'items?.*below.*reorder|reorder.*point|low.*stock', query_lower):
        return get_items_below_reorder_point(data)
    
    # Query 2: Blocked production orders
    elif re.search(r'blocked.*production|production.*blocked|mo.*blocked|blocked.*mo', query_lower):
        return get_blocked_production_orders(data)
    
    # Query 3: Supplier with maximum delay
    elif re.search(r'supplier.*maximum.*delay|supplier.*most.*delay|worst.*supplier|supplier.*delay', query_lower):
        return get_supplier_max_delay(data, metrics)
    
    # Query 4: Sales order fulfillment check
    elif re.search(r'can we fulfill|fulfill.*so|sales.*order.*fulfill', query_lower):
        # Extract order ID
        so_match = re.search(r'so\d+', query_lower, re.IGNORECASE)
        if so_match:
            so_id = so_match.group(0).upper()
            return check_so_fulfillment(so_id, data)
        else:
            return "❌ Please provide a Sales Order ID (e.g., 'Can we fulfill SO00001?')"
    
    # Default: Unknown query
    else:
        return """🤔 I didn't understand that question. Here are some questions I can answer:

- **"Which items are below reorder point?"** - Shows items with stock below reorder level
- **"Which production orders are blocked?"** - Shows MOs blocked due to component shortages
- **"Which supplier has maximum delay?"** - Identifies the supplier with worst delay performance
- **"Can we fulfill SO<order_id>?"** - Checks if a sales order can be fulfilled (e.g., "Can we fulfill SO00001?")

Try asking one of these!"""

def get_items_below_reorder_point(data):
    """Get items below reorder point"""
    inv_analysis = data['inventory'].merge(
        data['items_master'][['Item_ID', 'Item_Type', 'Reorder_Point', 'Description']],
        on='Item_ID',
        how='left'
    )
    
    inv_analysis['Shortage'] = inv_analysis['Reorder_Point'] - inv_analysis['Qty_On_Hand']
    critical_items = inv_analysis[inv_analysis['Qty_On_Hand'] < inv_analysis['Reorder_Point']].copy()
    
    if len(critical_items) == 0:
        return "✅ No items are below reorder point. All inventory levels are healthy!"
    
    critical_items = critical_items.sort_values('Shortage', ascending=False)
    
    response = f"⚠️ Found **{len(critical_items)}** items below reorder point:\n\n"
    response += "| Item ID | Description | Type | Location | On Hand | Reorder Point | Shortage |\n"
    response += "|---------|-------------|------|----------|---------|---------------|----------|\n"
    
    for _, row in critical_items.head(20).iterrows():
        response += f"| {row['Item_ID']} | {row['Description']} | {row['Item_Type']} | {row['Location']} | {row['Qty_On_Hand']} | {row['Reorder_Point']} | {row['Shortage']} |\n"
    
    if len(critical_items) > 20:
        response += f"\n*...and {len(critical_items) - 20} more items*"
    
    return response

def get_blocked_production_orders(data):
    """Get blocked production orders"""
    blocked_mo = data['production_order_components'][
        data['production_order_components']['Shortage_Qty'] > 0
    ]['Prod_Order_No'].unique()
    
    if len(blocked_mo) == 0:
        return "✅ No production orders are blocked. All can proceed!"
    
    # Get details for blocked MOs
    blocked_details = data['production_order_components'][
        data['production_order_components']['Shortage_Qty'] > 0
    ].merge(
        data['production_orders'][['Prod_Order_No', 'FG_Item_ID', 'Planned_Qty', 'Due_Date', 'Status']],
        on='Prod_Order_No',
        how='left'
    )
    
    blocked_details = blocked_details.sort_values(['Prod_Order_No', 'Shortage_Qty'], ascending=[True, False])
    
    response = f"🚫 Found **{len(blocked_mo)}** blocked production orders:\n\n"
    response += "| MO No | FG Item | Planned Qty | Due Date | Status | Component | Shortage |\n"
    response += "|-------|---------|-------------|----------|--------|------------|----------|\n"
    
    for _, row in blocked_details.head(30).iterrows():
        response += f"| {row['Prod_Order_No']} | {row['FG_Item_ID']} | {row['Planned_Qty']} | {row['Due_Date'].strftime('%Y-%m-%d')} | {row['Status']} | {row['Component_Item_ID']} | {row['Shortage_Qty']} |\n"
    
    if len(blocked_details) > 30:
        response += f"\n*...and {len(blocked_details) - 30} more component shortages*"
    
    return response

def get_supplier_max_delay(data, metrics):
    """Get supplier with maximum delay"""
    po_gr = metrics['po_gr'].copy()
    po_gr_supplier = po_gr.merge(
        data['suppliers'][['Supplier_ID', 'Supplier_Name']],
        on='Supplier_ID',
        how='left'
    )
    
    supplier_delay = po_gr_supplier.groupby('Supplier_ID').agg({
        'Supplier_Name': 'first',
        'Delay_Days': ['mean', 'count', lambda x: (x > 0).sum()]
    }).reset_index()
    supplier_delay.columns = ['Supplier_ID', 'Supplier_Name', 'Avg_Delay_Days', 'Total_POs', 'Delayed_POs']
    supplier_delay['Delay_Rate'] = (supplier_delay['Delayed_POs'] / supplier_delay['Total_POs'] * 100).round(2)
    
    worst_supplier = supplier_delay.sort_values('Avg_Delay_Days', ascending=False).iloc[0]
    
    response = f"📉 **Supplier with Maximum Delay:**\n\n"
    response += f"- **Supplier:** {worst_supplier['Supplier_Name']} ({worst_supplier['Supplier_ID']})\n"
    response += f"- **Average Delay:** {worst_supplier['Avg_Delay_Days']:.1f} days\n"
    response += f"- **Total POs:** {int(worst_supplier['Total_POs'])}\n"
    response += f"- **Delayed POs:** {int(worst_supplier['Delayed_POs'])}\n"
    response += f"- **Delay Rate:** {worst_supplier['Delay_Rate']}%\n"
    
    return response

def check_so_fulfillment(so_id, data):
    """Check if a sales order can be fulfilled"""
    # Find the sales order
    so = data['sales_orders'][data['sales_orders']['Sales_Order_No'] == so_id]
    
    if len(so) == 0:
        return f"❌ Sales Order {so_id} not found in the system."
    
    so = so.iloc[0]
    fg_item = so['FG_Item_ID']
    
    # Find production orders for this FG item
    mo_list = data['production_orders'][data['production_orders']['FG_Item_ID'] == fg_item]
    
    if len(mo_list) == 0:
        return f"ℹ️ No production orders found for FG Item {fg_item}. This might be a stock item or production hasn't been planned yet."
    
    # Check if any of the MOs have component shortages
    mo_nos = mo_list['Prod_Order_No'].tolist()
    mo_components = data['production_order_components'][
        data['production_order_components']['Prod_Order_No'].isin(mo_nos)
    ]
    
    blocked_components = mo_components[mo_components['Shortage_Qty'] > 0]
    
    if len(blocked_components) == 0:
        return f"✅ **Yes, SO{so_id} can likely be fulfilled.**\n\n" \
               f"- FG Item: {fg_item}\n" \
               f"- Ordered Qty: {so['Ordered_Qty']}\n" \
               f"- Linked Production Orders: {len(mo_list)}\n" \
               f"- No component shortages detected for linked MOs."
    else:
        blocked_mo_nos = blocked_components['Prod_Order_No'].unique()
        response = f"❌ **No, SO{so_id} cannot be fulfilled due to component shortages.**\n\n"
        response += f"- FG Item: {fg_item}\n"
        response += f"- Ordered Qty: {so['Ordered_Qty']}\n"
        response += f"- Linked Production Orders: {len(mo_list)}\n"
        response += f"- **Blocked MOs:** {len(blocked_mo_nos)}\n\n"
        response += "**Blocking Components:**\n\n"
        response += "| MO No | Component | Required | Available | Shortage |\n"
        response += "|-------|------------|-----------|-----------|----------|\n"
        
        for _, row in blocked_components.head(10).iterrows():
            response += f"| {row['Prod_Order_No']} | {row['Component_Item_ID']} | {row['Required_Qty']} | {row['Available_Qty']} | {row['Shortage_Qty']} |\n"
        
        if len(blocked_components) > 10:
            response += f"\n*...and {len(blocked_components) - 10} more component shortages*"
        
        return response
