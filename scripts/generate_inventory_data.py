import os
import pandas as pd
import numpy as np
import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows

BASE_DIR = r"C:\Users\Ravitheja\.gemini\antigravity\scratch\data-analyst-portfolio\03-sql-inventory-optimization"
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "sql"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "excel"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "powerbi"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "scripts"), exist_ok=True)

np.random.seed(42)

# 1. Product Master Data
products_data = [
    ("SKU-INV-001", "Industrial Smart Sensor Hub", "Industrial IoT", "SUP-101", 145.00, 72.00, 4.50),
    ("SKU-INV-002", "Heavy-Duty Hydraulic Seal Kit", "Mechanical Hardware", "SUP-102", 38.50, 14.20, 1.20),
    ("SKU-INV-003", "Precision CNC Drill Bit Set", "Tools & Machining", "SUP-103", 89.00, 41.00, 2.80),
    ("SKU-INV-004", "Modular Pneumatic Valve 24V", "Pneumatics", "SUP-101", 112.00, 56.50, 3.90),
    ("SKU-INV-005", "Thermal Imaging Diagnostic Unit", "Testing & Measurement", "SUP-104", 420.00, 230.00, 12.00),
    ("SKU-INV-006", "Automated Conveyor Roller 50mm", "Material Handling", "SUP-102", 28.00, 11.00, 1.10),
    ("SKU-INV-007", "Servo Motor Controller Board", "Industrial IoT", "SUP-103", 195.00, 95.00, 5.50),
    ("SKU-INV-008", "High-Torque Stepper Motor NEMA23", "Electromechanical", "SUP-104", 64.00, 29.50, 2.20),
    ("SKU-INV-009", "Fiber Optic Industrial Transceiver", "Networking", "SUP-105", 85.00, 37.00, 2.50),
    ("SKU-INV-010", "Lithium-Ion Backup Pack 48V", "Power Systems", "SUP-105", 350.00, 190.00, 10.00)
]

df_products = pd.DataFrame(products_data, columns=[
    "product_sku", "product_name", "category", "supplier_id", "unit_selling_price", "unit_cost", "annual_holding_cost_per_unit"
])
df_products.to_csv(os.path.join(BASE_DIR, "data", "dim_products.csv"), index=False)

# 2. Warehouses Master Data
warehouses_data = [
    ("WH-EAST-01", "Northeast Distribution Hub", "New Jersey, USA", 120000, 84.5),
    ("WH-MIDW-02", "Midwest Central Fulfillment", "Chicago, USA", 185000, 91.2),
    ("WH-WEST-03", "Pacific Coast Logistics Hub", "California, USA", 140000, 78.0),
    ("WH-SOUT-04", "Gulf Coast Terminal", "Texas, USA", 95000, 68.4)
]
df_warehouses = pd.DataFrame(warehouses_data, columns=[
    "warehouse_id", "warehouse_name", "location", "capacity_sqft", "utilization_pct"
])
df_warehouses.to_csv(os.path.join(BASE_DIR, "data", "dim_warehouses.csv"), index=False)

# 3. Inventory Stock Levels across Warehouses
inventory_rows = []
for p in products_data:
    sku = p[0]
    unit_cost = p[5]
    for w in warehouses_data:
        wh_id = w[0]
        # Realistic metrics
        avg_daily_sales = np.random.uniform(2.5, 12.0)
        lead_time_days = np.random.choice([7, 10, 14, 21, 28])
        safety_stock = int(avg_daily_sales * 5) # 5 days safety stock
        lead_time_demand = int(avg_daily_sales * lead_time_days)
        reorder_point = lead_time_demand + safety_stock
        
        # Current stock with deliberate variety (some stockouts, some healthy, some overstocked)
        stock_scenario = np.random.choice(["critical", "healthy", "healthy", "overstocked", "reorder"])
        if stock_scenario == "critical":
            current_stock = int(avg_daily_sales * np.random.uniform(1, 3))
        elif stock_scenario == "reorder":
            current_stock = int(reorder_point * np.random.uniform(0.7, 0.95))
        elif stock_scenario == "healthy":
            current_stock = int(reorder_point * np.random.uniform(1.2, 2.0))
        else: # overstocked
            current_stock = int(reorder_point * np.random.uniform(3.5, 5.5))
            
        inventory_rows.append({
            "warehouse_id": wh_id,
            "product_sku": sku,
            "current_stock": current_stock,
            "avg_daily_demand": round(avg_daily_sales, 1),
            "lead_time_days": lead_time_days,
            "safety_stock": safety_stock,
            "reorder_point": reorder_point,
            "max_storage_threshold": int(reorder_point * 5),
            "inventory_valuation": round(current_stock * unit_cost, 2)
        })

df_inventory = pd.DataFrame(inventory_rows)
df_inventory.to_csv(os.path.join(BASE_DIR, "data", "inventory_stock_levels.csv"), index=False)

# 4. Generate 1 Year of Sales Transactions for Inventory Turnover Calculations
dates = pd.date_range("2025-01-01", "2025-12-31", freq="D")
sales_records = []
for i in range(4500):
    inv_item = inventory_rows[np.random.choice(len(inventory_rows))]
    sku = inv_item["product_sku"]
    wh_id = inv_item["warehouse_id"]
    p_info = next(p for p in products_data if p[0] == sku)
    
    qty = np.random.choice([1, 2, 3, 5, 8, 12])
    tx_date = np.random.choice(dates)
    price = p_info[4]
    cost = p_info[5]
    
    sales_records.append({
        "order_id": f"SO-{70000 + i}",
        "order_date": pd.to_datetime(tx_date).strftime("%Y-%m-%d"),
        "product_sku": sku,
        "warehouse_id": wh_id,
        "units_sold": qty,
        "unit_selling_price": price,
        "unit_cost": cost,
        "gross_revenue": round(qty * price, 2),
        "total_cogs": round(qty * cost, 2),
        "gross_margin": round(qty * (price - cost), 2)
    })

df_sales = pd.DataFrame(sales_records)
df_sales.to_csv(os.path.join(BASE_DIR, "data", "sales_transactions.csv"), index=False)

# 5. Build Dynamic Excel Model using openpyxl
wb = Workbook()
ws_dash = wb.active
ws_dash.title = "Inventory Health Dashboard"

header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
alert_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid") # light red
healthy_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid") # light green
warn_fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid") # light yellow

header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
bold_font = Font(name="Calibri", size=11, bold=True)
title_font = Font(name="Calibri", size=16, bold=True, color="1F4E79")
border_thin = Border(
    left=Side(style='thin', color='D9D9D9'),
    right=Side(style='thin', color='D9D9D9'),
    top=Side(style='thin', color='D9D9D9'),
    bottom=Side(style='thin', color='D9D9D9')
)

ws_dash["A1"] = "Executive Sales & Inventory Optimization Model"
ws_dash["A1"].font = title_font
ws_dash["A2"] = "Dynamic Supply Chain Reorder & Stockout Early Warning System"
ws_dash["A2"].font = Font(italic=True, color="595959")

# Summary Metrics block
ws_dash["A4"] = "Inventory Optimization KPIs"
ws_dash["A4"].font = Font(size=13, bold=True, color="1F4E79")

tot_inv_val = df_inventory["inventory_valuation"].sum()
tot_cogs = df_sales["total_cogs"].sum()
turnover_ratio = tot_cogs / tot_inv_val
dsi_days = (tot_inv_val / tot_cogs) * 365

summary_kpis = [
    ("Metric", "Value", "Benchmark / Interpretation"),
    ("Total Capital Tied in Stock", f"${tot_inv_val:,.2f}", "Total working capital locked across all warehouses"),
    ("Annual Cost of Goods Sold (COGS)", f"${tot_cogs:,.2f}", "Total direct material acquisition costs sold"),
    ("Inventory Turnover Ratio", f"{turnover_ratio:.2f}x", "Times inventory is sold and replaced per year"),
    ("Days Sales of Inventory (DSI)", f"{dsi_days:.1f} Days", "Average days required to turn inventory into sales"),
    ("Stockout Risk Items Alert", f"{len(df_inventory[df_inventory['current_stock'] < df_inventory['reorder_point']])}", "SKU-Warehouse locations below Safety Reorder Point")
]

for r_idx, row in enumerate(summary_kpis, start=5):
    for c_idx, val in enumerate(row, start=1):
        cell = ws_dash.cell(row=r_idx, column=c_idx, value=val)
        cell.border = border_thin
        if r_idx == 5:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center")
        else:
            if c_idx == 1:
                cell.font = bold_font
            elif c_idx == 2:
                cell.alignment = Alignment(horizontal="right")

# Inventory Stock Reorder Table with Excel Formulas
ws_dash["A13"] = "Warehouse Stock Levels & Reorder Decision Model"
ws_dash["A13"].font = Font(size=13, bold=True, color="1F4E79")

tbl_headers = [
    "Warehouse", "Product SKU", "Current Stock", "Daily Demand", 
    "Lead Time (Days)", "Safety Stock", "Reorder Point (ROP)", 
    "Days on Hand (DOH)", "Stock Status Alert", "Inventory Value ($)"
]

for c_idx, h in enumerate(tbl_headers, start=1):
    c = ws_dash.cell(row=14, column=c_idx, value=h)
    c.fill = header_fill
    c.font = header_font
    c.alignment = Alignment(horizontal="center")
    c.border = border_thin

for r_idx, row in df_inventory.iterrows():
    curr_r = 15 + r_idx
    ws_dash.cell(row=curr_r, column=1, value=row["warehouse_id"]).border = border_thin
    ws_dash.cell(row=curr_r, column=2, value=row["product_sku"]).border = border_thin
    
    c_stock = ws_dash.cell(row=curr_r, column=3, value=row["current_stock"])
    c_stock.border = border_thin
    c_stock.alignment = Alignment(horizontal="right")
    
    c_demand = ws_dash.cell(row=curr_r, column=4, value=row["avg_daily_demand"])
    c_demand.border = border_thin
    c_demand.alignment = Alignment(horizontal="right")
    
    c_lead = ws_dash.cell(row=curr_r, column=5, value=row["lead_time_days"])
    c_lead.border = border_thin
    c_lead.alignment = Alignment(horizontal="right")
    
    c_safety = ws_dash.cell(row=curr_r, column=6, value=row["safety_stock"])
    c_safety.border = border_thin
    c_safety.alignment = Alignment(horizontal="right")
    
    # Excel Formula for Reorder Point: =(Daily_Demand * Lead_Time) + Safety_Stock
    c_rop = ws_dash.cell(row=curr_r, column=7, value=f"=ROUND((D{curr_r}*E{curr_r})+F{curr_r}, 0)")
    c_rop.border = border_thin
    c_rop.alignment = Alignment(horizontal="right")
    
    # Excel Formula for Days on Hand (DOH): =Current_Stock / Daily_Demand
    c_doh = ws_dash.cell(row=curr_r, column=8, value=f"=ROUND(C{curr_r}/D{curr_r}, 1)")
    c_doh.border = border_thin
    c_doh.alignment = Alignment(horizontal="right")
    
    # Excel Formula for Stock Status Alert
    # IF(C < G*0.5, "CRITICAL STOCKOUT", IF(C < G, "REORDER REQUIRED", IF(C > G*3, "OVERSTOCKED", "HEALTHY")))
    c_alert = ws_dash.cell(row=curr_r, column=9, value=f'=IF(C{curr_r}<(G{curr_r}*0.5),"CRITICAL STOCKOUT",IF(C{curr_r}<G{curr_r},"REORDER REQUIRED",IF(C{curr_r}>(G{curr_r}*3.5),"OVERSTOCKED","OPTIMAL HEALTHY")))')
    c_alert.border = border_thin
    c_alert.alignment = Alignment(horizontal="center")
    
    # Highlight based on status
    if row["current_stock"] < row["reorder_point"] * 0.5:
        c_alert.fill = alert_fill
        c_alert.font = Font(color="9C0006", bold=True)
    elif row["current_stock"] < row["reorder_point"]:
        c_alert.fill = warn_fill
        c_alert.font = Font(color="9C6500", bold=True)
    elif row["current_stock"] > row["reorder_point"] * 3.5:
        c_alert.fill = PatternFill(start_color="EDEDED", end_color="EDEDED", fill_type="solid")
    else:
        c_alert.fill = healthy_fill
        c_alert.font = Font(color="006100")
        
    c_val = ws_dash.cell(row=curr_r, column=10, value=row["inventory_valuation"])
    c_val.border = border_thin
    c_val.number_format = '$#,##0.00'

# Auto column widths
for col in ws_dash.columns:
    max_len = max(len(str(cell.value or '')) for cell in col)
    col_letter = col[0].column_letter
    ws_dash.column_dimensions[col_letter].width = min(max(max_len + 3, 14), 35)

excel_file = os.path.join(BASE_DIR, "excel", "Inventory_Optimization_Dynamic_Model.xlsx")
wb.save(excel_file)
print("Project 3 data and Dynamic Excel model created successfully.")
