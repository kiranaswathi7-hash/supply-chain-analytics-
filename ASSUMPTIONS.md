# Assumptions and Open Questions
## Manufacturing Supply Chain Analytics PoC

This document outlines the assumptions made during the development of this Streamlit application and identifies any open questions or areas for future enhancement.

---

### Data Assumptions

#### 1. **Revenue Calculation**
- **Assumption**: Total Revenue is calculated from ALL sales orders (pipeline value), not just shipped orders.
- **Formula**: `SUM(Ordered_Qty * Unit_Price)` across all sales orders
- **Rationale**: This represents the total order book value. If realized revenue is needed, filter by `Sales_Status = 'Shipped'`.

#### 2. **Sales-to-Production Link**
- **Assumption**: Sales orders are linked to production orders via `FG_Item_ID` only.
- **Limitation**: There is no direct foreign key between `sales_orders` and `production_orders`.
- **Impact**: The AI Copilot's "Can we fulfill SO?" query finds all production orders for the same FG item, which may include orders not specifically linked to that sales order.
- **Future Enhancement**: Add a `Linked_Prod_Order_No` column to sales_orders for direct linking.

#### 3. **Reorder Point Logic**
- **Assumption**: Items with `Qty_On_Hand < Reorder_Point` are considered "Low Stock".
- **Assumption**: Items with `Qty_On_Hand = 0` are "Critical" (stockout).
- **Assumption**: Items with `Qty_On_Hand > (Reorder_Point * 2)` are "Overstock".
- **Note**: These thresholds can be adjusted in the code if business requirements differ.

#### 4. **Blocked Production Orders**
- **Assumption**: A production order is "blocked" if ANY of its components has `Shortage_Qty > 0`.
- **Data Source**: The `production_order_components.csv` already contains pre-calculated `Shortage_Qty`.
- **Rationale**: This simplifies the logic compared to dynamically calculating shortages from BOM and inventory.

#### 5. **Supplier Delay Calculation**
- **Assumption**: Delay is calculated as `Receipt_Date - Expected_Receipt_Date` (from goods_receipts and purchase_orders).
- **Limitation**: This measures delay against expected date, not true lead time.
- **Note**: If PO creation date exists, true lead time would be `Receipt_Date - PO_Creation_Date`.

#### 6. **Risk Score Weights**
- **Assumption**: Overall Risk Score uses weighted formula:
  - Inventory Risk: 30%
  - Production Risk: 40%
  - Supplier Risk: 30%
- **Rationale**: Production risk is weighted higher as it directly impacts customer delivery.
- **Adjustment**: These weights can be modified in `data_loader.py` if business priorities differ.

#### 7. **Date Formats**
- **Assumption**: All date columns in CSVs are in ISO format (YYYY-MM-DD) and parse correctly with `pd.to_datetime()`.
- **Handled**: Date parsing is done during data load in `data_loader.py`.

#### 8. **Item Type Convention**
- **Assumption**: Items starting with "FG" are Finished Goods, "RM" are Raw Materials.
- **Usage**: This convention is used for filtering and categorization in various dashboards.
- **Note**: The `Item_Type` column in items_master.csv explicitly defines this.

---

### Technical Assumptions

#### 1. **Data Location**
- **Assumption**: All CSV files are located in the `csv files` subdirectory relative to the project root.
- **Path**: `Path(__file__).parent / "csv files"`

#### 2. **Streamlit Caching**
- **Assumption**: Data is cached for 1 hour (`@st.cache_data(ttl=3600)`) to improve performance.
- **Impact**: Changes to CSV files won't be reflected until cache expires or Streamlit is restarted.

#### 3. **AI Copilot Rule-Based Logic**
- **Assumption**: The AI Copilot uses regex-based keyword matching, not actual NLP/LLM.
- **Limitation**: It only understands specific query patterns documented in the UI.
- **Future Enhancement**: The code structure allows easy swapping with a real LLM API call.

#### 4. **Chart Libraries**
- **Assumption**: All charts use Plotly (no Matplotlib) as specified in requirements.
- **Rationale**: Plotly provides interactive charts which are better for dashboard exploration.

---

### Open Questions / Future Enhancements

#### 1. **Sales Order Fulfillment Logic**
- **Question**: Should fulfillment check consider existing finished goods inventory, or only production orders?
- **Current**: Only checks production orders for component shortages.
- **Enhancement**: Add logic to check if FG item is already in stock and can be shipped directly.

#### 2. **Production Order Status Mapping**
- **Question**: What are the valid production order statuses and which ones indicate "blocked"?
- **Current**: Uses component shortage to determine blocking, not status field.
- **Enhancement**: Add status-based blocking logic (e.g., "On Hold", "Blocked" statuses).

#### 3. **Multi-Location Inventory**
- **Question**: Should reorder point checks be location-specific or global?
- **Current**: Global check (sums all locations for an item).
- **Enhancement**: Add location-specific reorder point logic if needed.

#### 4. **BOM Versioning**
- **Question**: How should multiple BOM versions be handled?
- **Current**: Uses single BOM per FG item (Version column exists but not used).
- **Enhancement**: Add logic to select active BOM version based on date or status.

#### 5. **Real-Time Data**
- **Question**: Is real-time data integration needed?
- **Current**: Static CSV files loaded on app start.
- **Enhancement**: Connect to live ERP database via SQL or API.

#### 6. **User Authentication**
- **Question**: Is user authentication/authorization needed?
- **Current**: No authentication (open access).
- **Enhancement**: Add Streamlit authentication for role-based access.

---

### Known Limitations

1. **No Direct SO-MO Link**: Sales orders cannot be directly traced to specific production orders without additional data.
2. **Static Data**: Dashboard uses CSV snapshots, not real-time ERP data.
3. **Rule-Based AI**: The chatbot has limited query understanding compared to a real LLM.
4. **Single User**: No multi-user support or concurrent session handling.
5. **No Data Validation**: Assumes CSV data is clean and properly formatted.

---

### Testing Recommendations

Before deploying to production, test with:

1. **Edge Cases**: Zero inventory, empty datasets, missing dates
2. **Performance**: Large datasets (100k+ rows)
3. **Browser Compatibility**: Chrome, Firefox, Safari, Edge
4. **Mobile Responsiveness**: Test on mobile devices
5. **Query Variations**: Test AI Copilot with different phrasings of the same question

---

### Version Information

- **Python**: 3.10+
- **Streamlit**: Latest stable
- **Pandas**: Latest stable
- **Plotly**: Latest stable
- **Build Date**: July 2026
