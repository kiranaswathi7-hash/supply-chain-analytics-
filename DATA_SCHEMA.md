# Data Schema and Table Relationships
## Manufacturing Supply Chain Analytics PoC

### Table Overview

| File | Rows | Columns | Purpose |
|------|------|---------|---------|
| items_master.csv | 200 | 5 | Master data for all items (FG and RM) |
| suppliers.csv | 50 | 4 | Supplier master data |
| customers.csv | 100 | 4 | Customer master data |
| inventory.csv | 600 | 4 | Current stock levels by location |
| purchase_orders.csv | 1000 | 6 | Purchase orders to suppliers |
| goods_receipts.csv | 1000 | 5 | Receipts against purchase orders |
| sales_orders.csv | 2000 | 8 | Customer sales orders |
| production_orders.csv | 1500 | 6 | Manufacturing orders |
| production_order_components.csv | 9375 | 5 | Component requirements per MO |
| bom_header.csv | 100 | 4 | BOM definitions (header) |
| bom_lines.csv | 619 | 3 | BOM component lines |

---

### Table Relationships and Join Keys

#### 1. **BOM Structure**
```
bom_header (BOM_ID, FG_Item_ID) 
    ↓ (BOM_ID)
bom_lines (BOM_ID, Component_Item_ID, Qty_Per_Unit)
```
- **Join Key**: `BOM_ID`
- **Purpose**: Defines which raw materials (RM) are needed to produce each finished good (FG)

#### 2. **Production Orders**
```
production_orders (Prod_Order_No, FG_Item_ID, Status)
    ↓ (Prod_Order_No)
production_order_components (Prod_Order_No, Component_Item_ID, Required_Qty, Available_Qty, Shortage_Qty)
```
- **Join Key**: `Prod_Order_No`
- **Purpose**: Links manufacturing orders to their component requirements and shortages
- **Note**: `Shortage_Qty` is pre-calculated in the data (Required_Qty - Available_Qty)

#### 3. **Sales Orders**
```
sales_orders (Sales_Order_No, FG_Item_ID, Customer_ID)
    ↓ (Customer_ID)
customers (Customer_ID)
    ↓ (FG_Item_ID)
production_orders (FG_Item_ID) [if linked to production]
```
- **Join Keys**: `Customer_ID` to customers, `FG_Item_ID` to production_orders
- **Purpose**: Links customer orders to production and customer master data

#### 4. **Purchase Orders & Goods Receipts**
```
purchase_orders (PO_No, Item_ID, Supplier_ID, Expected_Receipt_Date)
    ↓ (PO_No)
goods_receipts (PO_No, Receipt_Date)
    ↓ (Supplier_ID)
suppliers (Supplier_ID)
    ↓ (Item_ID)
items_master (Item_ID)
```
- **Join Keys**: `PO_No` for PO-to-receipt, `Supplier_ID` to suppliers, `Item_ID` to items_master
- **Purpose**: Tracks supplier performance and material receipts

#### 5. **Inventory**
```
inventory (Item_ID, Warehouse, Qty_On_Hand)
    ↓ (Item_ID)
items_master (Item_ID, Item_Type, Reorder_Point)
```
- **Join Key**: `Item_ID`
- **Purpose**: Links stock levels to item master data for reorder point checks

---

### Key Column Details

#### items_master.csv
- `Item_ID`: Unique identifier for items (FGxxxx or RMxxxx)
- `Item_Type`: Distinguishes FG (Finished Goods) from RM (Raw Materials)
- `Reorder_Point`: Minimum stock level before reorder is needed
- `Unit_Cost`: Cost per unit

#### inventory.csv
- `Item_ID`: Links to items_master
- `Warehouse`: Warehouse/stock location
- `Qty_On_Hand`: Current stock quantity

#### production_order_components.csv
- `Shortage_Qty`: Pre-calculated shortage (Required_Qty - Available_Qty)
- If `Shortage_Qty > 0`, the production order is blocked due to component shortage

#### sales_orders.csv
- `Sales_Status`: Order status (Open, Released, Shipped, etc.)
- `Unit_Price`: Price per unit for revenue calculation

#### purchase_orders.csv
- `Expected_Receipt_Date`: When the PO was expected to arrive

#### goods_receipts.csv
- `Receipt_Date`: Actual date when goods were received
- **Delay Calculation**: `Receipt_Date - Expected_Receipt_Date`

---

### Item Type Convention
- **FGxxxx**: Finished Goods items (e.g., FG0001, FG0020)
- **RMxxxx**: Raw Material items (e.g., RM0111, RM0476)
- This convention is used consistently across all tables
