# KPI Formulas and Business Logic
## Manufacturing Supply Chain Analytics PoC

---

### 1. Executive Dashboard KPIs

#### Total Revenue
**Formula**: `SUM(sales_orders.Ordered_Qty * sales_orders.Unit_Price)`
- Filter: All sales orders (or only Shipped status?)
- **Assumption**: Calculate from all orders for total pipeline value, or only Shipped for realized revenue

#### Open Sales Orders
**Formula**: `COUNT(sales_orders WHERE Sales_Status = 'Open')`
- **Assumption**: 'Open' status indicates active, unfulfilled orders

#### Blocked Production Orders
**Formula**: `COUNT(production_orders WHERE Prod_Order_No IN (SELECT DISTINCT Prod_Order_No FROM production_order_components WHERE Shortage_Qty > 0))`
- **Logic**: A production order is blocked if any of its components has a shortage

#### Overall Risk Score
**Formula**: Weighted score based on:
- Inventory Risk (Low Stock Items / Total Items)
- Production Risk (Blocked MOs / Total MOs)
- Supplier Risk (Delayed POs / Total POs)
- **Calculation**: `(Inventory_Risk_Score * 0.3) + (Production_Risk_Score * 0.4) + (Supplier_Risk_Score * 0.3)`
- Scale: 0-100 (higher = more risk)

#### Sales Trend Line Chart
**Formula**: Group sales_orders by `Order_Date` (month), sum revenue
- X-axis: Month
- Y-axis: Revenue

#### Risk Summary Pie Chart
**Formula**: Count of items by risk category
- Categories: Low Stock, Critical, Overstock, Normal
- Based on inventory vs reorder point analysis

---

### 2. Inventory Risk Dashboard KPIs

#### Low Stock Items
**Formula**: `COUNT(DISTINCT inventory.Item_ID WHERE Qty_On_Hand < items_master.Reorder_Point)`
- Join: inventory → items_master on Item_ID
- **Logic**: Items below reorder point but not critical

#### Critical Items
**Formula**: `COUNT(DISTINCT inventory.Item_ID WHERE Qty_On_Hand = 0)`
- **Logic**: Items with zero stock (stockout)

#### Overstock Items
**Formula**: `COUNT(DISTINCT inventory.Item_ID WHERE Qty_On_Hand > (Reorder_Point * 2))`
- **Logic**: Items with more than 2x reorder point (excess inventory)

#### Stock Levels by Warehouse (Bar Chart)
**Formula**: Group inventory by Location, sum Qty_On_Hand
- X-axis: Location
- Y-axis: Total Quantity

#### Critical Inventory Items Table
**Formula**: Join inventory + items_master where `Qty_On_Hand < Reorder_Point`
- Columns: Item_ID, Item_Type, Location, Qty_On_Hand, Reorder_Point, Shortage
- Sortable/filterable

---

### 3. Supplier Analytics KPIs

#### Average Lead Time
**Formula**: `AVG(goods_receipts.Receipt_Date - purchase_orders.Expected_Receipt_Date)`
- Join: goods_receipts → purchase_orders on PO_No
- **Note**: This is actually average delay, not lead time
- **Alternative**: Use average of (Receipt_Date - PO_Date) if PO_Date exists

#### Delayed Purchase Orders
**Formula**: `COUNT(goods_receipts WHERE Receipt_Date > purchase_orders.Expected_Receipt_Date)`
- Join: goods_receipts → purchase_orders on PO_No

#### Suppliers At Risk
**Formula**: `COUNT(DISTINCT suppliers WHERE Delay_Rate > 20%)`
- **Delay_Rate**: Delayed POs / Total POs per supplier
- **Threshold**: Suppliers with >20% delay rate

#### Supplier Ranking Chart
**Formula**: Calculate on-time delivery % per supplier
- `On-Time % = (1 - (Delayed POs / Total POs)) * 100`
- Sort by on-time % (descending) or by average delay days

#### Delay Analysis Table
**Formula**: Join purchase_orders + goods_receipts + suppliers
- Columns: PO_No, Supplier_ID, Item_ID, Expected_Receipt_Date, Receipt_Date, Delay_Days
- Delay_Days = Receipt_Date - Expected_Receipt_Date
- Sort by Delay_Days (descending)

---

### 4. Production Risk Dashboard KPIs

#### Total Manufacturing Orders
**Formula**: `COUNT(production_orders)`

#### Blocked Manufacturing Orders
**Formula**: `COUNT(DISTINCT production_order_components.Prod_Order_No WHERE Shortage_Qty > 0)`
- **Logic**: Count unique production orders with any component shortage

#### Components Short
**Formula**: `COUNT(production_order_components WHERE Shortage_Qty > 0)`
- **Logic**: Total number of component shortages across all MOs

#### Component Shortage Heatmap
**Formula**: Matrix of Production Orders vs Raw Materials
- Rows: Prod_Order_No
- Columns: Component_Item_ID
- Values: Shortage_Qty (color-coded by severity)
- Filter: Only show where Shortage_Qty > 0

#### Blocked Production Orders Table
**Formula**: Join production_orders + production_order_components + items_master
- Columns: Prod_Order_No, FG_Item_ID, Planned_Qty, Due_Date, Status, Component_Item_ID, Shortage_Qty
- Filter: WHERE Shortage_Qty > 0
- Sort by Shortage_Qty (descending)

---

### 5. AI Copilot Query Logic

#### Query: "Which items are below reorder point?"
**Logic**: Join inventory + items_master, filter where `Qty_On_Hand < Reorder_Point`
- Return: Item_ID, Item_Type, Qty_On_Hand, Reorder_Point

#### Query: "Which production orders are blocked?"
**Logic**: Filter production_order_components where `Shortage_Qty > 0`, get distinct Prod_Order_No
- Return: Prod_Order_No, FG_Item_ID, Status, Due_Date

#### Query: "Which supplier has maximum delay?"
**Logic**: 
1. Join purchase_orders + goods_receipts
2. Calculate delay per PO: `Receipt_Date - Expected_Receipt_Date`
3. Group by Supplier_ID, calculate average delay
4. Sort by average delay descending, take top 1
- Return: Supplier_ID, Supplier_Name, Avg_Delay_Days, Delayed_POs

#### Query: "Can we fulfill SO<order_id>?"
**Logic**:
1. Get FG_Item_ID from sales_orders for the given Sales_Order_No
2. Find linked production_order(s) by FG_Item_ID (or direct link if exists)
3. Check production_order_components for any Shortage_Qty > 0
4. If no shortages → "Yes, can fulfill"
5. If shortages exist → "No, blocked due to component shortages: [list components]"
- Return: Fulfillment status, blocking components (if any)

---

### Data Loading Strategy

**Central Data Loading Function**:
```python
def load_all_data():
    data_dir = Path(__file__).parent / "csv files"
    return {
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
```

**Date Parsing**: Convert date columns to datetime objects during load
- Order_Date, Requested_Delivery_Date (sales_orders)
- Expected_Receipt_Date (purchase_orders)
- Receipt_Date (goods_receipts)
- Due_Date (production_orders)
