"""
スキーマ抽出機能のテスト

analyze_excel_csv_schema 関数の動作を検証するテストコード
"""

import pytest
from pathlib import Path
from src.tools.schema_extractor import analyze_excel_csv_schema
from src.schemas import ProjectSchema, TableSchema, ColumnSchema


# テストデータのパス
TEST_DATA_DIR = Path(__file__).parent / "test_data"


class TestSchemaExtractor:
    """スキーマ抽出機能のテストクラス"""

    def test_analyze_excel_csv_schema_basic(self):
        """基本的なスキーマ抽出のテスト"""
        # テストデータディレクトリが存在することを確認
        assert TEST_DATA_DIR.exists(), f"テストデータディレクトリが存在しません: {TEST_DATA_DIR}"

        # スキーマを抽出
        project_schema = analyze_excel_csv_schema(TEST_DATA_DIR, project_name="テストプロジェクト")

        # ProjectSchema が返されることを確認
        assert isinstance(project_schema, ProjectSchema)
        assert project_schema.project_name == "テストプロジェクト"

    def test_analyze_excel_csv_schema_table_count(self):
        """テーブル数の検証"""
        project_schema = analyze_excel_csv_schema(TEST_DATA_DIR)

        # 期待されるテーブル数を確認
        # customers.csv (1テーブル) + sales_data.xlsx の3シート (3テーブル) = 4テーブル
        assert len(project_schema.tables) == 4, f"期待: 4テーブル, 実際: {len(project_schema.tables)}"

    def test_csv_schema_extraction(self):
        """CSV ファイルのスキーマ抽出を検証"""
        project_schema = analyze_excel_csv_schema(TEST_DATA_DIR)

        # customers.csv のテーブルを探す
        customers_table = None
        for table in project_schema.tables:
            if table.name == "customers":
                customers_table = table
                break

        assert customers_table is not None, "customers テーブルが見つかりません"

        # カラム数を確認（customer_id, name, age, email, registration_date）
        assert len(customers_table.columns) == 5

        # カラム名を確認
        column_names = [col.name for col in customers_table.columns]
        assert "customer_id" in column_names
        assert "name" in column_names
        assert "age" in column_names
        assert "email" in column_names
        assert "registration_date" in column_names

    def test_excel_schema_extraction(self):
        """Excel ファイルのスキーマ抽出を検証"""
        project_schema = analyze_excel_csv_schema(TEST_DATA_DIR)

        # Excel の各シートのテーブルを探す
        sales_detail_table = None
        products_table = None
        inventory_table = None

        for table in project_schema.tables:
            if "売上明細" in table.name:
                sales_detail_table = table
            elif "商品マスタ" in table.name:
                products_table = table
            elif "在庫履歴" in table.name:
                inventory_table = table

        assert sales_detail_table is not None, "売上明細テーブルが見つかりません"
        assert products_table is not None, "商品マスタテーブルが見つかりません"
        assert inventory_table is not None, "在庫履歴テーブルが見つかりません"

        # 売上明細のカラム数を確認
        assert len(sales_detail_table.columns) == 6

    def test_column_dtype_detection(self):
        """データ型の検出を検証"""
        project_schema = analyze_excel_csv_schema(TEST_DATA_DIR)

        # customers.csv のテーブルを取得
        customers_table = next((t for t in project_schema.tables if t.name == "customers"), None)
        assert customers_table is not None

        # customer_id は int64 型であるべき
        customer_id_col = next((col for col in customers_table.columns if col.name == "customer_id"), None)
        assert customer_id_col is not None
        assert "int" in customer_id_col.dtype.lower()

        # name は object (文字列) 型であるべき
        name_col = next((col for col in customers_table.columns if col.name == "name"), None)
        assert name_col is not None
        assert "object" in name_col.dtype.lower()

    def test_nullable_detection(self):
        """欠損値の検出を検証"""
        project_schema = analyze_excel_csv_schema(TEST_DATA_DIR)

        # customers.csv のテーブルを取得
        customers_table = next((t for t in project_schema.tables if t.name == "customers"), None)
        assert customers_table is not None

        # age カラムは欠損値を含む（nullable=True）
        age_col = next((col for col in customers_table.columns if col.name == "age"), None)
        assert age_col is not None
        assert age_col.nullable is True

        # customer_id カラムは欠損値を含まない（nullable=False）
        customer_id_col = next((col for col in customers_table.columns if col.name == "customer_id"), None)
        assert customer_id_col is not None
        assert customer_id_col.nullable is False

    def test_example_values_extraction(self):
        """サンプル値の抽出を検証"""
        project_schema = analyze_excel_csv_schema(TEST_DATA_DIR)

        # customers.csv のテーブルを取得
        customers_table = next((t for t in project_schema.tables if t.name == "customers"), None)
        assert customers_table is not None

        # name カラムのサンプル値を確認
        name_col = next((col for col in customers_table.columns if col.name == "name"), None)
        assert name_col is not None
        assert len(name_col.example_values) > 0
        assert "山田太郎" in name_col.example_values

    def test_nonexistent_directory(self):
        """存在しないディレクトリを指定した場合のエラーハンドリング"""
        with pytest.raises(ValueError, match="指定されたディレクトリが存在しません"):
            analyze_excel_csv_schema("/path/to/nonexistent/directory")

    def test_file_instead_of_directory(self):
        """ファイルをディレクトリとして指定した場合のエラーハンドリング"""
        # テストデータの CSV ファイルパスを使用
        csv_file = TEST_DATA_DIR / "customers.csv"
        with pytest.raises(ValueError, match="指定されたパスはディレクトリではありません"):
            analyze_excel_csv_schema(csv_file)


if __name__ == "__main__":
    # pytest がインストールされていない場合のための簡易実行
    import sys
    print("テストを実行するには pytest を使用してください:")
    print("  pytest tests/test_schema_extractor.py -v")
    sys.exit(1)
