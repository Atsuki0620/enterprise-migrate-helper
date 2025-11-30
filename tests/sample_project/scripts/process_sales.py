"""
Sales Data Processing Script

Reads sales transaction data and generates aggregated summary report.
"""

import pandas as pd
from pathlib import Path


def process_sales_data(input_path: str, output_path: str) -> None:
    """
    Process sales data and generate summary report.

    Args:
        input_path: Path to input CSV file
        output_path: Path to output summary CSV file
    """
    # Read input data
    df = pd.read_csv(input_path)

    # Validate date format
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])

    # Aggregate by region and category
    summary = df.groupby(['region', 'product_category']).agg(
        transaction_count=('transaction_id', 'count'),
        total_sales=('total_amount', 'sum')
    ).reset_index()

    # Sort by total sales descending
    summary = summary.sort_values('total_sales', ascending=False)

    # Output to CSV
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    summary.to_csv(output_path, index=False)

    print(f"Summary generated: {output_path}")


if __name__ == "__main__":
    base_dir = Path(__file__).parent.parent
    input_file = base_dir / "data" / "sales_sample.csv"
    output_file = base_dir / "output" / "sales_summary.csv"

    process_sales_data(str(input_file), str(output_file))
