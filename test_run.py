"""
analyze_excel_csv_schema の動作確認スクリプト
"""

from src.tools.schema_extractor import analyze_excel_csv_schema
from pathlib import Path

# テストデータディレクトリ
test_data_dir = Path("tests/test_data")

print("=" * 70)
print("analyze_excel_csv_schema の動作確認")
print("=" * 70)
print()

# スキーマを抽出
print(f"対象ディレクトリ: {test_data_dir}")
print("-" * 70)
print()

project_schema = analyze_excel_csv_schema(test_data_dir, project_name="テストプロジェクト")

print(f"プロジェクト名: {project_schema.project_name}")
print(f"テーブル数: {len(project_schema.tables)}")
print()

# 各テーブルの情報を表示
for i, table in enumerate(project_schema.tables, 1):
    print(f"[{i}] テーブル名: {table.name}")
    print(f"    ファイルパス: {table.path}")
    print(f"    カラム数: {len(table.columns)}")
    print()

    # カラムの詳細を表示（最初の3つのみ）
    for j, column in enumerate(table.columns[:3], 1):
        print(f"    カラム {j}: {column.name}")
        print(f"      データ型: {column.dtype}")
        print(f"      欠損値: {column.nullable}")
        print(f"      サンプル値: {column.example_values[:3]}")
        print()

    if len(table.columns) > 3:
        print(f"    ... 他 {len(table.columns) - 3} カラム")
        print()

print("=" * 70)
print("動作確認完了")
print("=" * 70)
