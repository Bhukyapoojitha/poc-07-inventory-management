# Inventory Management & Procurement Operations Manual

## POC-07 Retail Inventory Reference Guide

### Section 1: Introduction to Inventory Management

Inventory management is the process of ordering, storing, and using inventory. Effective inventory management ensures products are available when customers need them while minimizing carrying costs and avoiding overstock situations.

This system manages:

- Product catalog management
- Stock level tracking
- Purchase order management
- Stock movement recording

All inventory changes are recorded as stock movements for full auditability.

---

### Section 2: Product Catalog and SKU System

Every product has a unique SKU in the format:

SKU-{CATEGORY_PREFIX}-{NNNN}

Category Prefixes:

- GRO : Grocery
- ELC : Electronics
- CLO : Clothing
- HHD : Household
- PRC : Personal Care

Examples:

- SKU-GRO-0042
- SKU-ELC-0015

Each product contains:

- unit_price
- cost_price
- unit_of_measure
- reorder_point
- reorder_quantity

---

### Section 3: Stock Levels and Reorder Points

Every product has:

- quantity_on_hand
- quantity_reserved
- quantity_available

Formula:

quantity_available = quantity_on_hand - quantity_reserved

Reorder Point Formula:

reorder point = average daily demand × lead time + safety stock

Example:

10 units/day × 5 days + 20 safety stock = 70 units

---

### Section 4: Stock Alert System

Low Stock Alert:

Triggered when:

quantity_available <= reorder_point

Out Of Stock Alert:

Triggered when:

quantity_available = 0

Reorder Suggested Alert:

Generated using historical consumption patterns.

---

### Section 5: Purchase Order Process

PO Status Flow:

1. Draft
2. Submitted
3. Acknowledged
4. Received
5. Cancelled

PO Number Format:

PO-{YEAR}-{NNNN}

Example:

PO-2026-0042

When PO is received:

- StockMovement(receipt) is created
- Stock is updated
- Alerts are resolved

---

### Section 6: Supplier Management

Supplier fields:

- supplier_code
- lead_time_days
- payment_terms_days
- is_active

Only active suppliers should receive new purchase orders.

---

### Section 7: Stock Movement Recording

Movement Types:

- receipt
- sale
- adjustment
- transfer
- return

Every movement includes:

- reference_number
- timestamp
- recorded_by

---

### Section 8: Inventory Valuation

Inventory value is calculated using FIFO.

Formula:

total_stock_value =
cost_price × quantity_on_hand

Dashboard shows:

- total_stock_value

---

### Section 9: Reorder Quantity Calculation

EOQ Formula:

EOQ = √(2 × annual_demand × ordering_cost ÷ holding_cost)

Simple retailer formula:

reorder quantity =
daily sales × (lead time + safety stock period)

---

### Section 10: Procurement Officer Responsibilities

Responsibilities:

- Monitor low stock alerts
- Review supplier catalogs
- Create purchase orders
- Follow supplier acknowledgements
- Coordinate deliveries

POs above ₹50,000 require approval.

---

### Section 11: Stock Count and Reconciliation

Types:

- Cycle Count
- Full Count

Discrepancies require:

StockMovement(adjustment)

---

### Section 12: Category Management

Grocery:
High volume and short shelf life.

Electronics:
High cost and lower movement.

Clothing:
Seasonal demand.

Household:
Predictable demand.

Personal Care:
High volume and brand sensitive.

---

### Section 13: Reporting and Analytics

Reports:

- Slow moving stock
- Stock turn ratio
- Fill rate
- Days on hand

Store Manager reviews weekly reports.

Inventory Analyst prepares monthly trend reports.

---

### Section 14: System Integration

Integrations:

- POS
- Supplier Portal
- Finance System

Manual stock movements can be entered when integration is unavailable.

---

### Section 15: Troubleshooting

Problem:
Negative stock quantity

Solution:
Create StockMovement(adjustment).

Problem:
Duplicate low stock alerts

Solution:
Check for unresolved alerts before creating a new alert.

Problem:
PO received but stock not updated

Solution:
Verify receive endpoint executed successfully.

Problem:
SKU not found by supplier

Solution:
Verify supplier catalog and supplier_id mapping.