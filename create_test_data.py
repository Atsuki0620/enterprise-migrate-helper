"""
テストデータ作成スクリプト

analyze_excel_csv_schema のテスト用に、Excel と CSV ファイルを作成します。
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

# テストデータディレクトリ
test_data_dir = Path("tests/test_data")
test_data_dir.mkdir(exist_ok=True)

# CSV ファイル: 顧客データ
customers_data = {
    "customer_id": [1, 2, 3, 4, 5],
    "name": ["山田太郎", "佐藤花子", "鈴木一郎", "田中美咲", "高橋健太"],
    "age": [25, 30, None, 28, 35],  # 欠損値を含む
    "email": ["yamada@example.com", "sato@example.com", "suzuki@example.com", None, "takahashi@example.com"],
    "registration_date": [
        "2024-01-15",
        "2024-02-20",
        "2024-03-10",
        "2024-04-05",
        "2024-05-12"
    ]
}
customers_df = pd.DataFrame(customers_data)
customers_df["registration_date"] = pd.to_datetime(customers_df["registration_date"])
customers_df.to_csv(test_data_dir / "customers.csv", index=False)
print(f"作成: {test_data_dir / 'customers.csv'}")

# Excel ファイル: 複数シートを持つ売上データ
with pd.ExcelWriter(test_data_dir / "sales_data.xlsx", engine='openpyxl') as writer:
    # シート1: 売上明細
    sales_detail = {
        "sale_id": [1001, 1002, 1003, 1004, 1005],
        "product_name": ["ノートPC", "マウス", "キーボード", None, "モニター"],  # 欠損値を含む
        "quantity": [2, 5, 3, 1, 2],
        "unit_price": [120000.0, 2500.0, 5000.0, 3000.0, 45000.0],
        "total_amount": [240000.0, 12500.0, 15000.0, 3000.0, 90000.0],
        "sale_date": [
            datetime(2024, 1, 10),
            datetime(2024, 1, 15),
            datetime(2024, 2, 1),
            datetime(2024, 2, 10),
            datetime(2024, 3, 5)
        ]
    }
    sales_df = pd.DataFrame(sales_detail)
    sales_df.to_excel(writer, sheet_name="売上明細", index=False)
    print(f"作成: {test_data_dir / 'sales_data.xlsx'}:売上明細")

    # シート2: 商品マスタ
    products = {
        "product_id": [101, 102, 103, 104, 105],
        "product_name": ["ノートPC", "マウス", "キーボード", "ヘッドセット", "モニター"],
        "category": ["PC", "周辺機器", "周辺機器", "周辺機器", "ディスプレイ"],
        "in_stock": [True, True, False, True, True],  # Boolean型
        "stock_count": [10, 50, 0, 25, 15]
    }
    products_df = pd.DataFrame(products)
    products_df.to_excel(writer, sheet_name="商品マスタ", index=False)
    print(f"作成: {test_data_dir / 'sales_data.xlsx'}:商品マスタ")

    # シート3: 在庫履歴（欠損値が多い）
    inventory = {
        "date": [datetime(2024, 1, i) for i in range(1, 6)],
        "product_id": [101, 102, None, 104, None],
        "quantity_change": [5, -10, None, 3, -2],
        "notes": ["入荷", "出荷", None, "入荷", None]
    }
    inventory_df = pd.DataFrame(inventory)
    inventory_df.to_excel(writer, sheet_name="在庫履歴", index=False)
    print(f"作成: {test_data_dir / 'sales_data.xlsx'}:在庫履歴")

print("\nテストデータの作成が完了しました！")
