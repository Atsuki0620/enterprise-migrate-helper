# Project Overview

## Project Purpose

This project processes monthly sales data to generate summary reports. It reads raw sales transaction data, calculates aggregations by region and product category, and outputs a formatted summary.

## Sample Data Files

### sales_sample.csv

- **Location**: `data/sales_sample.csv`
- **Format**: CSV (UTF-8, comma-separated)
- **Row Count**: 100 sample records

#### Schema

| Column Name | Data Type | Description | Example Values |
|-------------|-----------|-------------|----------------|
| transaction_id | string | Unique transaction identifier | "TXN-001", "TXN-002" |
| transaction_date | string | Date in YYYY-MM-DD format | "2024-01-15" |
| region | string | Sales region code | "EAST", "WEST", "NORTH", "SOUTH" |
| product_category | string | Product category name | "Electronics", "Clothing", "Food" |
| quantity | integer | Number of items sold | 1, 5, 10 |
| unit_price | float | Price per unit in USD | 29.99, 149.50 |
| total_amount | float | Total transaction amount (quantity × unit_price) | 299.90, 747.50 |

#### Data Assumptions

- All dates are in YYYY-MM-DD format
- Numeric values use period (.) as decimal separator
- No null values in required fields
- Region codes are uppercase

## Scripts

### process_sales.py

- **Location**: `scripts/process_sales.py`
- **Purpose**: Reads sales data, aggregates by region and category, generates summary report
- **Input**: `data/sales_sample.csv`
- **Output**: `output/sales_summary.csv` (generated at runtime)

#### Dependencies

- pandas >= 2.0.0

#### Processing Flow

1. Read CSV file from data directory
2. Validate date format and numeric fields
3. Group by region and product_category
4. Calculate sum of total_amount and count of transactions
5. Sort by total_amount descending
6. Output summary to CSV

## Data Processing Flow
```
[sales_sample.csv]
    ↓ (read)
[process_sales.py]
    ↓ (aggregate)
[sales_summary.csv]
```

## Library Versions

- Python: 3.9+
- pandas: 2.0.0

## Format Assumptions

- Character encoding: UTF-8
- Date format: YYYY-MM-DD
- Decimal separator: period (.)
- CSV delimiter: comma (,)
