-- =============================================================================
-- Project: SQL Sales & Inventory Optimization Analysis
-- Script: 02_complex_inventory_analysis.sql
-- Description: Complex multi-table joins, subqueries, and window aggregations
--              analyzing inventory turnover, stockout risks, category profitability,
--              and supply chain bottlenecks.
-- =============================================================================

-- Query 1: Inventory Turnover Ratio & Days Sales of Inventory (DSI / DOH)
-- Utilizes multi-table joins between Sales, Inventory, and Product dimensions
SELECT
    p.category,
    p.product_sku,
    p.product_name,
    inv_agg.total_on_hand_stock,
    ROUND(inv_agg.current_inventory_valuation, 2) AS current_inventory_valuation,
    ROUND(sales_agg.annual_cogs, 2) AS annual_cogs,
    -- Inventory Turnover = Annual COGS / Current Inventory Value
    ROUND(
        sales_agg.annual_cogs / NULLIF(inv_agg.current_inventory_valuation, 0), 
        2
    ) AS inventory_turnover_ratio,
    -- Days Sales of Inventory (DSI) = (Current Inventory Value / Annual COGS) * 365
    ROUND(
        (inv_agg.current_inventory_valuation / NULLIF(sales_agg.annual_cogs, 0)) * 365, 
        1
    ) AS days_sales_of_inventory_dsi
FROM dim_products p
JOIN (
    -- Subquery 1: Aggregate Current Inventory across all regional warehouses
    SELECT
        product_sku,
        SUM(current_stock) AS total_on_hand_stock,
        SUM(inventory_valuation) AS current_inventory_valuation
    FROM inventory_stock
    GROUP BY product_sku
) inv_agg ON p.product_sku = inv_agg.product_sku
JOIN (
    -- Subquery 2: Aggregate 12-Month Sales and COGS
    SELECT
        product_sku,
        SUM(units_sold) AS total_units_sold,
        SUM(total_cogs) AS annual_cogs,
        SUM(gross_revenue) AS annual_revenue
    FROM fact_sales_orders
    GROUP BY product_sku
) sales_agg ON p.product_sku = sales_agg.product_sku
ORDER BY inventory_turnover_ratio DESC;

-- Query 2: Warehouse Stockout Risk & Reorder Priority Classification
-- Compares live stock against dynamic Reorder Point (ROP = (Demand * LeadTime) + SafetyStock)
SELECT
    w.warehouse_name,
    w.location,
    p.product_sku,
    p.product_name,
    i.current_stock,
    i.avg_daily_demand,
    i.lead_time_days,
    i.safety_stock,
    i.reorder_point,
    -- Projected Days of Supply Remaining
    ROUND(i.current_stock / NULLIF(i.avg_daily_demand, 0), 1) AS days_of_supply_remaining,
    -- Actionable Stock Alert Logic
    CASE
        WHEN i.current_stock < (i.reorder_point * 0.5) THEN 'CRITICAL STOCKOUT RISK (< 50% ROP)'
        WHEN i.current_stock < i.reorder_point THEN 'REORDER REQUIRED (Below Safety Threshold)'
        WHEN i.current_stock > (i.reorder_point * 3.5) THEN 'OVERSTOCKED (Capital Tied)'
        ELSE 'OPTIMAL HEALTHY STOCK'
    END AS stock_health_status,
    ROUND(i.inventory_valuation, 2) AS tied_working_capital
FROM inventory_stock i
JOIN dim_warehouses w ON i.warehouse_id = w.warehouse_id
JOIN dim_products p ON i.product_sku = p.product_sku
WHERE i.current_stock < i.reorder_point -- Filter specifically for replenishment attention
ORDER BY days_of_supply_remaining ASC;

-- Query 3: Category-Level Profitability & Carrying Cost Drag
-- Evaluates gross margin versus annual inventory holding costs to identify stagnant lines
SELECT
    p.category,
    COUNT(DISTINCT p.product_sku) AS active_skus,
    SUM(s.units_sold) AS total_units_sold,
    ROUND(SUM(s.gross_revenue), 2) AS total_revenue,
    ROUND(SUM(s.gross_margin), 2) AS total_gross_margin,
    ROUND((SUM(s.gross_margin) / SUM(s.gross_revenue)) * 100, 2) AS gross_margin_pct,
    -- Annual Holding Cost = On-Hand Stock * Holding Cost per Unit
    ROUND(SUM(inv.current_stock * p.annual_holding_cost_per_unit), 2) AS total_annual_holding_cost,
    -- Net Profit Contribution after Carrying Costs
    ROUND(SUM(s.gross_margin) - SUM(inv.current_stock * p.annual_holding_cost_per_unit), 2) AS net_profit_contribution
FROM dim_products p
JOIN fact_sales_orders s ON p.product_sku = s.product_sku
JOIN inventory_stock inv ON p.product_sku = inv.product_sku AND s.warehouse_id = inv.warehouse_id
GROUP BY p.category
ORDER BY net_profit_contribution DESC;

-- Query 4: Supply Chain Bottlenecks & Warehouse Storage Saturation
SELECT
    w.warehouse_id,
    w.warehouse_name,
    w.capacity_sqft,
    w.utilization_pct,
    COUNT(DISTINCT i.product_sku) AS stored_skus,
    SUM(i.current_stock) AS total_units_stored,
    ROUND(SUM(i.inventory_valuation), 2) AS total_warehouse_stock_value,
    AVG(i.lead_time_days) AS avg_replenishment_lead_time_days,
    CASE
        WHEN w.utilization_pct >= 90.0 THEN 'CRITICAL BOTTLENECK: High Risk of Overflow'
        WHEN w.utilization_pct >= 80.0 THEN 'WARNING: Space Constrained'
        ELSE 'HEALTHY CAPACITY'
    END AS space_capacity_alert
FROM dim_warehouses w
JOIN inventory_stock i ON w.warehouse_id = i.warehouse_id
GROUP BY w.warehouse_id, w.warehouse_name, w.capacity_sqft, w.utilization_pct
ORDER BY w.utilization_pct DESC;
