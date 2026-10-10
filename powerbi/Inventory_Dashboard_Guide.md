# Power BI Supply Chain & Inventory Optimization Dashboard

## 1. Dimensional Model Setup
- **Central Fact Table**: `Fact_Sales_Orders` (`order_id`, `order_date`, `product_sku`, `warehouse_id`, `units_sold`, `gross_revenue`, `total_cogs`, `gross_margin`).
- **Snapshot Table**: `Inventory_Stock` (`warehouse_id`, `product_sku`, `current_stock`, `reorder_point`, `inventory_valuation`).
- **Dimension 1**: `Dim_Products` (`product_sku`, `product_name`, `category`, `unit_cost`, `annual_holding_cost_per_unit`).
- **Dimension 2**: `Dim_Warehouses` (`warehouse_id`, `warehouse_name`, `location`, `capacity_sqft`, `utilization_pct`).
- **Dimension 3**: `Dim_Suppliers` (`supplier_id`, `supplier_name`, `reliability_score`).

## 2. Interactive Dashboard Layout

### Executive KPI Strip:
- `Total Inventory Valuation ($)`: Locked working capital.
- `Inventory Turnover Ratio`: Benchmark turnover rate.
- `Days Sales of Inventory (DSI)`: Velocity of liquidation.
- `Stockout Alert Count`: Immediate purchasing reorder trigger.
- `Warehouse Bottleneck Alert`: Warehouses at >90% physical capacity.

### Visual 1: Stock Health Matrix (Heatmap / Scatter Plot)
- **X-Axis**: `Days of Supply Remaining`
- **Y-Axis**: `Inventory Valuation ($)`
- **Color by Status**: Red (Stockout imminent), Green (Optimal), Gray (Overstocked / Idle capital).

### Visual 2: Category Profitability vs Holding Cost Drag
- Clustered Bar chart comparing `Total Gross Margin` side-by-side with `Annual Holding Cost` by product category.

### Visual 3: Warehouse Capacity & Lead Time Map
- Geographic bubble map indicating warehouse physical storage capacity utilization (%) and average vendor lead time in days.
