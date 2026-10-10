-- =============================================================================
-- Project: SQL Sales & Inventory Optimization Analysis
-- Script: 01_inventory_schema.sql
-- Description: DDL Schema for Supply Chain Warehouse & Inventory Database.
-- =============================================================================

DROP TABLE IF EXISTS fact_sales_orders;
DROP TABLE IF EXISTS inventory_stock;
DROP TABLE IF EXISTS dim_products;
DROP TABLE IF EXISTS dim_warehouses;
DROP TABLE IF EXISTS dim_suppliers;

-- 1. Dimension: Suppliers
CREATE TABLE dim_suppliers (
    supplier_id       VARCHAR(20) PRIMARY KEY,
    supplier_name     VARCHAR(100) NOT NULL,
    country           VARCHAR(50) NOT NULL,
    reliability_score DECIMAL(3, 2) DEFAULT 0.95 -- 0.00 to 1.00 score
);

-- 2. Dimension: Warehouses
CREATE TABLE dim_warehouses (
    warehouse_id      VARCHAR(20) PRIMARY KEY,
    warehouse_name    VARCHAR(100) NOT NULL,
    location          VARCHAR(100) NOT NULL,
    capacity_sqft     INT NOT NULL,
    utilization_pct   DECIMAL(5, 2) NOT NULL
);

-- 3. Dimension: Products
CREATE TABLE dim_products (
    product_sku                   VARCHAR(30) PRIMARY KEY,
    product_name                  VARCHAR(150) NOT NULL,
    category                      VARCHAR(80) NOT NULL,
    supplier_id                   VARCHAR(20) NOT NULL,
    unit_selling_price            DECIMAL(10, 2) NOT NULL,
    unit_cost                     DECIMAL(10, 2) NOT NULL,
    annual_holding_cost_per_unit  DECIMAL(8, 2) NOT NULL,
    CONSTRAINT fk_prod_supplier FOREIGN KEY (supplier_id) REFERENCES dim_suppliers(supplier_id)
);

-- 4. Inventory Stock Snapshot
CREATE TABLE inventory_stock (
    stock_id              INT PRIMARY KEY AUTO_INCREMENT,
    warehouse_id          VARCHAR(20) NOT NULL,
    product_sku           VARCHAR(30) NOT NULL,
    current_stock         INT NOT NULL,
    avg_daily_demand      DECIMAL(8, 2) NOT NULL,
    lead_time_days        INT NOT NULL,
    safety_stock          INT NOT NULL,
    reorder_point         INT NOT NULL,
    max_storage_threshold INT NOT NULL,
    inventory_valuation   DECIMAL(14, 2) NOT NULL,
    CONSTRAINT fk_inv_wh FOREIGN KEY (warehouse_id) REFERENCES dim_warehouses(warehouse_id),
    CONSTRAINT fk_inv_prod FOREIGN KEY (product_sku) REFERENCES dim_products(product_sku)
);

-- 5. Fact Table: Sales Transactions
CREATE TABLE fact_sales_orders (
    order_id           VARCHAR(30) PRIMARY KEY,
    order_date         DATE NOT NULL,
    product_sku        VARCHAR(30) NOT NULL,
    warehouse_id       VARCHAR(20) NOT NULL,
    units_sold         INT NOT NULL,
    unit_selling_price DECIMAL(10, 2) NOT NULL,
    unit_cost          DECIMAL(10, 2) NOT NULL,
    gross_revenue      DECIMAL(12, 2) NOT NULL,
    total_cogs         DECIMAL(12, 2) NOT NULL,
    gross_margin       DECIMAL(12, 2) NOT NULL,
    CONSTRAINT fk_sales_prod FOREIGN KEY (product_sku) REFERENCES dim_products(product_sku),
    CONSTRAINT fk_sales_wh FOREIGN KEY (warehouse_id) REFERENCES dim_warehouses(warehouse_id)
);

-- Performance Indexes
CREATE INDEX idx_inv_sku_wh ON inventory_stock(product_sku, warehouse_id);
CREATE INDEX idx_sales_date ON fact_sales_orders(order_date);
CREATE INDEX idx_sales_sku ON fact_sales_orders(product_sku);
