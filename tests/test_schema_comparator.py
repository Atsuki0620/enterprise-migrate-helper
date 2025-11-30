"""
スキーマ比較機能のテスト

compare_data_schemas 関数の動作を検証するテストコード
"""

import pytest
from src.tools.schema_comparator import compare_data_schemas
from src.schemas import (
    ProjectSchema,
    TableSchema,
    ColumnSchema,
    SchemaCompareResult,
)


class TestSchemaComparator:
    """スキーマ比較機能のテストクラス"""

    def test_no_differences(self):
        """差分がない場合のテスト"""
        # 同一のスキーマを作成
        schema = ProjectSchema(
            project_name="test",
            tables=[
                TableSchema(
                    name="users",
                    columns=[
                        ColumnSchema(name="id", dtype="int64", nullable=False),
                        ColumnSchema(name="name", dtype="object", nullable=False),
                    ]
                )
            ]
        )

        result = compare_data_schemas(schema, schema)

        assert isinstance(result, SchemaCompareResult)
        assert result.summary["added_tables"] == 0
        assert result.summary["removed_tables"] == 0
        assert result.summary["modified_tables"] == 0
        assert result.summary["added_columns"] == 0
        assert result.summary["removed_columns"] == 0
        assert result.summary["type_changed_columns"] == 0
        assert result.summary["renamed_columns"] == 0

    def test_table_added(self):
        """テーブル追加のテスト"""
        sample = ProjectSchema(
            project_name="sample",
            tables=[
                TableSchema(
                    name="users",
                    columns=[ColumnSchema(name="id", dtype="int64", nullable=False)]
                )
            ]
        )

        production = ProjectSchema(
            project_name="production",
            tables=[
                TableSchema(
                    name="users",
                    columns=[ColumnSchema(name="id", dtype="int64", nullable=False)]
                ),
                TableSchema(
                    name="orders",
                    columns=[ColumnSchema(name="id", dtype="int64", nullable=False)]
                )
            ]
        )

        result = compare_data_schemas(sample, production)

        assert result.summary["added_tables"] == 1
        assert result.summary["removed_tables"] == 0

        # added テーブルが検出されているか確認
        added_table_diff = next((td for td in result.table_diffs if td.diff_type == "added"), None)
        assert added_table_diff is not None
        assert added_table_diff.table_name == "orders"

    def test_table_removed(self):
        """テーブル削除のテスト"""
        sample = ProjectSchema(
            project_name="sample",
            tables=[
                TableSchema(
                    name="users",
                    columns=[ColumnSchema(name="id", dtype="int64", nullable=False)]
                ),
                TableSchema(
                    name="products",
                    columns=[ColumnSchema(name="id", dtype="int64", nullable=False)]
                )
            ]
        )

        production = ProjectSchema(
            project_name="production",
            tables=[
                TableSchema(
                    name="users",
                    columns=[ColumnSchema(name="id", dtype="int64", nullable=False)]
                )
            ]
        )

        result = compare_data_schemas(sample, production)

        assert result.summary["added_tables"] == 0
        assert result.summary["removed_tables"] == 1

        # removed テーブルが検出されているか確認
        removed_table_diff = next((td for td in result.table_diffs if td.diff_type == "removed"), None)
        assert removed_table_diff is not None
        assert removed_table_diff.table_name == "products"

    def test_column_added(self):
        """カラム追加のテスト"""
        sample = ProjectSchema(
            project_name="sample",
            tables=[
                TableSchema(
                    name="users",
                    columns=[
                        ColumnSchema(name="id", dtype="int64", nullable=False),
                    ]
                )
            ]
        )

        production = ProjectSchema(
            project_name="production",
            tables=[
                TableSchema(
                    name="users",
                    columns=[
                        ColumnSchema(name="id", dtype="int64", nullable=False),
                        ColumnSchema(name="age", dtype="int64", nullable=True),
                    ]
                )
            ]
        )

        result = compare_data_schemas(sample, production)

        assert result.summary["added_columns"] == 1
        assert result.summary["removed_columns"] == 0

        # modified テーブルが検出されているか確認
        modified_table_diff = next((td for td in result.table_diffs if td.diff_type == "modified"), None)
        assert modified_table_diff is not None
        assert len(modified_table_diff.column_diffs) == 1

        # added カラムが検出されているか確認
        added_col_diff = modified_table_diff.column_diffs[0]
        assert added_col_diff.diff_type == "added"
        assert added_col_diff.production_column_name == "age"
        assert added_col_diff.sample_column_name is None

    def test_column_removed(self):
        """カラム削除のテスト"""
        sample = ProjectSchema(
            project_name="sample",
            tables=[
                TableSchema(
                    name="users",
                    columns=[
                        ColumnSchema(name="id", dtype="int64", nullable=False),
                        ColumnSchema(name="nickname", dtype="object", nullable=True),
                    ]
                )
            ]
        )

        production = ProjectSchema(
            project_name="production",
            tables=[
                TableSchema(
                    name="users",
                    columns=[
                        ColumnSchema(name="id", dtype="int64", nullable=False),
                    ]
                )
            ]
        )

        result = compare_data_schemas(sample, production)

        assert result.summary["added_columns"] == 0
        assert result.summary["removed_columns"] == 1

        # removed カラムが検出されているか確認
        modified_table_diff = next((td for td in result.table_diffs if td.diff_type == "modified"), None)
        assert modified_table_diff is not None

        removed_col_diff = modified_table_diff.column_diffs[0]
        assert removed_col_diff.diff_type == "removed"
        assert removed_col_diff.sample_column_name == "nickname"
        assert removed_col_diff.production_column_name is None

    def test_type_changed(self):
        """データ型変更のテスト"""
        sample = ProjectSchema(
            project_name="sample",
            tables=[
                TableSchema(
                    name="users",
                    columns=[
                        ColumnSchema(name="created_at", dtype="datetime64[ns]", nullable=False),
                    ]
                )
            ]
        )

        production = ProjectSchema(
            project_name="production",
            tables=[
                TableSchema(
                    name="users",
                    columns=[
                        ColumnSchema(name="created_at", dtype="object", nullable=False),
                    ]
                )
            ]
        )

        result = compare_data_schemas(sample, production)

        assert result.summary["type_changed_columns"] == 1

        # type_changed カラムが検出されているか確認
        modified_table_diff = next((td for td in result.table_diffs if td.diff_type == "modified"), None)
        assert modified_table_diff is not None

        type_changed_col_diff = modified_table_diff.column_diffs[0]
        assert type_changed_col_diff.diff_type == "type_changed"
        assert type_changed_col_diff.sample_column_name == "created_at"
        assert type_changed_col_diff.production_column_name == "created_at"
        assert type_changed_col_diff.detail["sample_dtype"] == "datetime64[ns]"
        assert type_changed_col_diff.detail["production_dtype"] == "object"

    def test_column_renamed(self):
        """カラムリネームのテスト"""
        sample = ProjectSchema(
            project_name="sample",
            tables=[
                TableSchema(
                    name="users",
                    columns=[
                        ColumnSchema(name="id", dtype="int64", nullable=False),
                        ColumnSchema(name="user_name", dtype="object", nullable=False),
                    ]
                )
            ]
        )

        production = ProjectSchema(
            project_name="production",
            tables=[
                TableSchema(
                    name="users",
                    columns=[
                        ColumnSchema(name="id", dtype="int64", nullable=False),
                        ColumnSchema(name="username", dtype="object", nullable=False),
                    ]
                )
            ]
        )

        result = compare_data_schemas(sample, production)

        assert result.summary["renamed_columns"] == 1
        assert result.summary["added_columns"] == 0
        assert result.summary["removed_columns"] == 0

        # renamed カラムが検出されているか確認
        modified_table_diff = next((td for td in result.table_diffs if td.diff_type == "modified"), None)
        assert modified_table_diff is not None

        renamed_col_diff = modified_table_diff.column_diffs[0]
        assert renamed_col_diff.diff_type == "renamed"
        assert renamed_col_diff.sample_column_name == "user_name"
        assert renamed_col_diff.production_column_name == "username"

    def test_complex_changes(self):
        """複雑な変更のテスト（複数の差分が混在）"""
        sample = ProjectSchema(
            project_name="sample",
            tables=[
                TableSchema(
                    name="users",
                    columns=[
                        ColumnSchema(name="id", dtype="int64", nullable=False),
                        ColumnSchema(name="old_column", dtype="object", nullable=True),
                        ColumnSchema(name="type_change", dtype="int64", nullable=False),
                    ]
                ),
                TableSchema(
                    name="old_table",
                    columns=[ColumnSchema(name="id", dtype="int64", nullable=False)]
                )
            ]
        )

        production = ProjectSchema(
            project_name="production",
            tables=[
                TableSchema(
                    name="users",
                    columns=[
                        ColumnSchema(name="id", dtype="int64", nullable=False),
                        ColumnSchema(name="new_column", dtype="object", nullable=True),
                        ColumnSchema(name="type_change", dtype="float64", nullable=False),
                    ]
                ),
                TableSchema(
                    name="new_table",
                    columns=[ColumnSchema(name="id", dtype="int64", nullable=False)]
                )
            ]
        )

        result = compare_data_schemas(sample, production)

        # テーブルの追加・削除
        assert result.summary["added_tables"] == 1
        assert result.summary["removed_tables"] == 1

        # カラムの追加・削除
        assert result.summary["added_columns"] == 1
        assert result.summary["removed_columns"] == 1

        # 型変更
        assert result.summary["type_changed_columns"] == 1


if __name__ == "__main__":
    print("テストを実行するには pytest を使用してください:")
    print("  pytest tests/test_schema_comparator.py -v")
