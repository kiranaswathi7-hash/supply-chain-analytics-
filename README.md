# Manufacturing Supply Chain Analytics

A multi-page Streamlit dashboard for ERP-style supply chain analytics, built as a Proof of Concept (PoC) using sample data similar to Microsoft Dynamics NAV / D365.

## Features

### 📊 Executive Dashboard
- Total Revenue (pipeline value)
- Open Sales Orders count
- Blocked Production Orders count
- Overall Risk Score (weighted composite metric)
- Sales trend line chart over time
- Risk summary pie chart by category
- Sales orders distribution by status

### 📦 Inventory Risk Dashboard
- Low Stock Items count
- Critical Items (zero stock) count
- Overstock Items count
- Stock levels bar chart by warehouse/location
- Critical inventory items table (sortable/filterable)
- Inventory health distribution pie chart

### 🚚 Supplier Analytics
- Average Lead Time (delay metric)
- Delayed Purchase Orders count
- Suppliers At Risk (>20% delay rate)
- Supplier ranking chart by on-time delivery
- Delay analysis table (expected vs actual receipt dates)
- Supplier performance summary table
- Delay distribution box plot by supplier

### 🏭 Production Risk Dashboard
- Total Manufacturing Orders count
- Blocked Manufacturing Orders count
- Component Shortages count
- Component shortage heatmap (MOs vs Components)
- Blocked production orders table with blocking reasons
- Production orders distribution by status
- Top components with most shortages

### 🤖 AI Copilot
Rule-based natural language query interface (no external API required):
- "Which items are below reorder point?"
- "Which production orders are blocked?"
- "Which supplier has maximum delay?"
- "Can we fulfill SO<order_id>?"

## Tech Stack

- **Python**: 3.10+
- **Streamlit**: Multi-page application framework
- **Pandas**: Data processing and joins
- **Plotly**: Interactive charts (all visualizations)
- **NumPy**: Calculations
- **OpenPyXL**: Excel export/import support

## Project Structure

```
python streamlit project/
├── app.py                          # Main application entry point
├── requirements.txt                # Python dependencies
├── explore_data.py                # Data exploration script
├── DATA_SCHEMA.md                  # Table relationships documentation
├── KPI_FORMULAS.md                # KPI calculation logic
├── ASSUMPTIONS.md                 # Assumptions and known limitations
├── README.md                      # This file
├── csv files/                     # Data directory (contains CSV files)
│   ├── items_master.csv
│   ├── suppliers.csv
│   ├── customers.csv
│   ├── inventory.csv
│   ├── purchase_orders.csv
│   ├── goods_receipts.csv
│   ├── sales_orders.csv
│   ├── production_orders.csv
│   ├── production_order_components.csv
│   ├── bom_header.csv
│   └── bom_lines.csv
└── pages/                         # Streamlit pages
    ├── __init__.py
    ├── data_loader.py             # Shared data loading utility
    ├── executive_dashboard.py     # Executive Dashboard page
    ├── inventory_risk.py          # Inventory Risk Dashboard page
    ├── supplier_analytics.py      # Supplier Analytics page
    ├── production_risk.py        # Production Risk Dashboard page
    └── ai_copilot.py             # AI Copilot page
```

## Setup Instructions

### 1. Prerequisites
- Python 3.10 or higher installed
- pip (Python package manager)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Prepare Data
Ensure all CSV files are placed in the `csv files` directory:
- items_master.csv
- suppliers.csv
- customers.csv
- inventory.csv
- purchase_orders.csv
- goods_receipts.csv
- sales_orders.csv
- production_orders.csv
- production_order_components.csv
- bom_header.csv
- bom_lines.csv

### 4. Run the Application
```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## Data Schema

The application uses 11 CSV files with the following key relationships:

- **BOM**: bom_header ↔ bom_lines via BOM_ID
- **Production**: production_orders ↔ production_order_components via Prod_Order_No
- **Sales**: sales_orders ↔ customers via Customer_ID, ↔ production_orders via FG_Item_ID
- **Purchasing**: purchase_orders ↔ goods_receipts via PO_No, ↔ suppliers via Supplier_ID
- **Inventory**: inventory ↔ items_master via Item_ID

For detailed schema information, see [DATA_SCHEMA.md](DATA_SCHEMA.md)

## KPI Formulas

All KPI calculations are documented in [KPI_FORMULAS.md](KPI_FORMULAS.md), including:
- Revenue calculation logic
- Reorder point checks
- Component shortage detection
- Supplier delay analysis
- Risk score weighting

## Assumptions & Limitations

This PoC makes several assumptions about the data and business logic. For a complete list, see [ASSUMPTIONS.md](ASSUMPTIONS.md).

Key assumptions:
- Revenue is calculated from all sales orders (pipeline value)
- Sales orders link to production orders via FG_Item_ID (no direct foreign key)
- Production orders are blocked if any component has Shortage_Qty > 0
- Supplier delay is calculated as Receipt_Date - Expected_Receipt_Date
- Risk score uses 30% inventory, 40% production, 30% supplier weights

## Usage

### Navigation
Use the sidebar to navigate between the 5 dashboard pages:
1. Executive Dashboard
2. Inventory Risk Dashboard
3. Supplier Analytics
4. Production Risk Dashboard
5. AI Copilot

### AI Copilot
The AI Copilot uses rule-based keyword matching (no external API required). Try these queries:
- "Which items are below reorder point?"
- "Which production orders are blocked?"
- "Which supplier has maximum delay?"
- "Can we fulfill SO00001?"

### Data Export
Most tables include a download button to export data as CSV for further analysis.

## Future Enhancements

Potential improvements for production deployment:
- Direct ERP database integration (SQL/API)
- Real-time data refresh
- User authentication/authorization
- More sophisticated AI/LLM integration
- Location-specific reorder point logic
- Direct sales-to-production order linking
- BOM versioning support

## Troubleshooting

### Issue: "File not found" errors
**Solution**: Ensure all CSV files are in the `csv files` directory with correct names.

### Issue: Charts not displaying
**Solution**: Check that Plotly is installed correctly: `pip install plotly --upgrade`

### Issue: Data not refreshing
**Solution**: The data is cached for 1 hour. Restart Streamlit to clear cache: press Ctrl+C in terminal and run `streamlit run app.py` again.

## License

This is a Proof of Concept project for demonstration purposes.

## Contact

For questions or issues, please refer to the documentation files:
- DATA_SCHEMA.md - Data structure and relationships
- KPI_FORMULAS.md - Business logic and calculations
- ASSUMPTIONS.md - Assumptions and known limitations
