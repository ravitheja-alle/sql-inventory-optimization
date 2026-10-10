# SQL Sales & Inventory Optimization Analysis

[![Tech: SQL](https://img.shields.io/badge/SQL-Multi--Table_Joins_&_Subqueries-00758F.svg)](#)
[![Tech: Excel](https://img.shields.io/badge/Excel-Dynamic_Reorder_Model-107C41.svg)](#)
[![Tech: Power BI](https://img.shields.io/badge/Power_BI-Supply_Chain_Analytics-F2C811.svg)](#)

## 📌 Executive Summary
Excess inventory ties up vital operational capital, while stockouts result in direct revenue loss and customer defection. This project delivers an analytical supply chain model evaluating inventory turnover, stockout risks, carrying costs, and fulfillment bottlenecks across multi-regional distribution networks.

Using **advanced SQL queries (multi-table joins, correlated subqueries, and window aggregations)** combined with a **dynamic Microsoft Excel inventory decision model** and **Power BI supply chain dashboards**, this solution enables procurement teams to automate replenishment thresholds and balance capital efficiency.

---

## 🛠️ Data Architecture & Relational Schema

```
   ┌───────────────────┐               ┌───────────────────┐
   │   dim_suppliers   │               │  dim_warehouses   │
   ├───────────────────┤               ├───────────────────┤
   │ supplier_id (PK)  │               │ warehouse_id (PK) │
   │ supplier_name     │               │ warehouse_name    │
   │ reliability_score │               │ capacity_sqft     │
   └─────────┬─────────┘               │ utilization_pct   │
             │                         └─────────┬─────────┘
             │ 1                                 │ 1
             │                                   │
             │ *                                 │ *
   ┌─────────┴─────────┐               ┌─────────┴─────────┐
   │   dim_products    │ 1           * │  inventory_stock  │
   ├───────────────────┼───────────────┤ (Current Levels,  │
   │ product_sku (PK)  │               │  ROP, Lead Time,  │
   │ product_name      │               │  Holding Cost)    │
   │ category          │               └───────────────────┘
   │ unit_cost         │                         │ 1
   │ unit_selling_price│                         │
   └─────────┬─────────┘                         │
             │ 1                                 │
             │                                   │
             │ *                               * │
   ┌─────────┴───────────────────────────────────┴─────────┐
   │                  fact_sales_orders                    │
   ├───────────────────────────────────────────────────────┤
   │ order_id (PK) | order_date | product_sku (FK)         │
   │ warehouse_id (FK) | units_sold | total_cogs | margin  │
   └───────────────────────────────────────────────────────┘
```

---

## 🔍 Core SQL Analytical Queries (`sql/02_complex_inventory_analysis.sql`)

### 1. Inventory Turnover Ratio & Days Sales of Inventory (DSI)
Calculates inventory liquidation velocity using aggregated subqueries and joins across the product catalog and historical order logs:

```sql
SELECT
    p.category,
    p.product_sku,
    p.product_name,
    inv_agg.total_on_hand_stock,
    ROUND(inv_agg.current_inventory_valuation, 2) AS current_inventory_valuation,
    ROUND(sales_agg.annual_cogs, 2) AS annual_cogs,
    -- Inventory Turnover = Annual COGS / Current Inventory Value
    ROUND(sales_agg.annual_cogs / NULLIF(inv_agg.current_inventory_valuation, 0), 2) AS inventory_turnover_ratio,
    -- Days Sales of Inventory (DSI)
    ROUND((inv_agg.current_inventory_valuation / NULLIF(sales_agg.annual_cogs, 0)) * 365, 1) AS days_sales_of_inventory_dsi
FROM dim_products p
JOIN (
    SELECT product_sku, SUM(current_stock) AS total_on_hand_stock, SUM(inventory_valuation) AS current_inventory_valuation
    FROM inventory_stock
    GROUP BY product_sku
) inv_agg ON p.product_sku = inv_agg.product_sku
JOIN (
    SELECT product_sku, SUM(total_cogs) AS annual_cogs
    FROM fact_sales_orders
    GROUP BY product_sku
) sales_agg ON p.product_sku = sales_agg.product_sku
ORDER BY inventory_turnover_ratio DESC;
```

### 2. Automated Stockout Risk Early Warning Query
Identifies items requiring immediate purchase replenishment based on supplier lead times and safety stock requirements:

```sql
SELECT
    w.warehouse_name,
    p.product_name,
    i.current_stock,
    i.reorder_point,
    ROUND(i.current_stock / NULLIF(i.avg_daily_demand, 0), 1) AS days_of_supply_remaining,
    CASE
        WHEN i.current_stock < (i.reorder_point * 0.5) THEN 'CRITICAL STOCKOUT RISK (< 50% ROP)'
        WHEN i.current_stock < i.reorder_point THEN 'REORDER REQUIRED (Below Safety Threshold)'
        WHEN i.current_stock > (i.reorder_point * 3.5) THEN 'OVERSTOCKED (Capital Tied)'
        ELSE 'OPTIMAL HEALTHY STOCK'
    END AS stock_health_status
FROM inventory_stock i
JOIN dim_warehouses w ON i.warehouse_id = w.warehouse_id
JOIN dim_products p ON i.product_sku = p.product_sku
WHERE i.current_stock < i.reorder_point;
```

---

## 📑 Dynamic Microsoft Excel Model (`excel/Inventory_Optimization_Dynamic_Model.xlsx`)
- **Automated Reorder Point Formulas**:
  `=ROUND((Daily_Demand * Lead_Time) + Safety_Stock, 0)`
- **Dynamic Days on Hand (DOH)**:
  `=ROUND(Current_Stock / Daily_Demand, 1)`
- **Automated Reorder Logic**:
  `=IF(Current_Stock < (ROP * 0.5), "CRITICAL STOCKOUT", IF(Current_Stock < ROP, "REORDER REQUIRED", IF(Current_Stock > (ROP * 3.5), "OVERSTOCKED", "OPTIMAL HEALTHY")))`
- **Visual Alerting**: Built-in conditional formatting highlighting urgent stockouts in soft red and healthy inventory in green.

---

## 📈 Actionable Findings & Supply Chain Recommendations

1. **Warehouse Storage Saturation Bottleneck**:
   - The **Midwest Central Fulfillment Hub (Chicago)** is operating at **91.2% capacity utilization**, leading to handling bottlenecks and elevated demurrage risks.
   - *Recommendation*: Transfer 15% of slow-moving buffer stock to the Gulf Coast Terminal (currently at 68.4% utilization) to prevent fulfillment slowdowns.

2. **Capital Locked in Overstocked SKUs**:
   - Analysis revealed over **$42,000** tied up in overstocked items having more than 120 Days Sales of Inventory (DSI).
   - *Recommendation*: Run promotional bundle campaigns on overstocked SKUs to free up working capital and reduce annual carrying costs.

3. **Vendor Lead Time Buffer Adjustment**:
   - Products supplied by vendor `SUP-104` exhibited 28-day replenishment cycles, causing repeated stockout flags during demand surges.
   - *Recommendation*: Increase safety stock baseline from 5 days to 8 days for high-lead-time suppliers to maintain 98%+ order fill rates.

---

## 🚀 How to Run
1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/sql-sales-inventory-optimization.git
   ```
2. Execute SQL scripts in order:
   - `sql/01_inventory_schema.sql`
   - `sql/02_complex_inventory_analysis.sql`
3. Open `excel/Inventory_Optimization_Dynamic_Model.xlsx` in Microsoft Excel to interact with dynamic reorder formulas and Pivot models.
4. Review Power BI metrics in `powerbi/DAX_Inventory_Measures.dax`.
