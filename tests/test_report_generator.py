"""
レポート生成機能のテスト

report_analysis_result 関数の動作を検証するテストコード
"""

import pytest
from src.tools.report_generator import report_analysis_result
from src.schemas import (
    ProjectSchema,
    TableSchema,
    ColumnSchema,
    SchemaCompareResult,
    TableDiff,
    ColumnDiff,
)


class TestReportGenerator:
    """レポート生成機能のテストクラス"""

    def test_no_differences_report(self):
        """差分がない場合のレポート生成"""
        schema = ProjectSchema(
            project_name="test",
            tables=[
                TableSchema(
                    name="users",
                    columns=[ColumnSchema(name="id", dtype="int64", nullable=False)]
                )
            ]
        )

        compare_result = SchemaCompareResult(
            sample_project=schema,
            production_project=schema,
            table_diffs=[],
            summary={
                "added_tables": 0,
                "removed_tables": 0,
                "modified_tables": 0,
                "added_columns": 0,
                "removed_columns": 0,
                "type_changed_columns": 0,
                "renamed_columns": 0,
            }
        )

        report = report_analysis_result(compare_result)

        # Markdown 文字列が返されることを確認
        assert isinstance(report, str)
        assert len(report) > 0

        # タイトルが含まれていることを確認
        assert "# 本番データとサンプルデータの構造差分レポート" in report

        # サマリが含まれていることを確認
        assert "## 概要" in report
        assert "### 差分サマリ" in report

        # 差分がないことが記述されていることを確認
        assert "差分は検出されませんでした" in report

    def test_table_added_report(self):
        """テーブル追加のレポート生成"""
        sample = ProjectSchema(
            project_name="sample",
            tables=[
                TableSchema(name="users", columns=[])
            ]
        )

        production = ProjectSchema(
            project_name="production",
            tables=[
                TableSchema(name="users", columns=[]),
                TableSchema(name="orders", columns=[])
            ]
        )

        compare_result = SchemaCompareResult(
            sample_project=sample,
            production_project=production,
            table_diffs=[
                TableDiff(table_name="orders", diff_type="added", column_diffs=[])
            ],
            summary={
                "added_tables": 1,
                "removed_tables": 0,
                "modified_tables": 0,
                "added_columns": 0,
                "removed_columns": 0,
                "type_changed_columns": 0,
                "renamed_columns": 0,
            }
        )

        report = report_analysis_result(compare_result)

        # サマリに追加テーブル数が含まれていることを確認
        assert "**追加テーブル数**: 1" in report

        # 追加されたテーブルセクションが含まれていることを確認
        assert "### 追加されたテーブル" in report
        assert "`orders`" in report

    def test_table_removed_report(self):
        """テーブル削除のレポート生成"""
        sample = ProjectSchema(
            project_name="sample",
            tables=[
                TableSchema(name="users", columns=[]),
                TableSchema(name="old_table", columns=[])
            ]
        )

        production = ProjectSchema(
            project_name="production",
            tables=[
                TableSchema(name="users", columns=[])
            ]
        )

        compare_result = SchemaCompareResult(
            sample_project=sample,
            production_project=production,
            table_diffs=[
                TableDiff(table_name="old_table", diff_type="removed", column_diffs=[])
            ],
            summary={
                "added_tables": 0,
                "removed_tables": 1,
                "modified_tables": 0,
                "added_columns": 0,
                "removed_columns": 0,
                "type_changed_columns": 0,
                "renamed_columns": 0,
            }
        )

        report = report_analysis_result(compare_result)

        # サマリに削除テーブル数が含まれていることを確認
        assert "**削除テーブル数**: 1" in report

        # 削除されたテーブルセクションが含まれていることを確認
        assert "### 削除されたテーブル" in report
        assert "`old_table`" in report

    def test_column_changes_report(self):
        """カラム変更のレポート生成"""
        sample = ProjectSchema(
            project_name="sample",
            tables=[TableSchema(name="users", columns=[])]
        )

        production = ProjectSchema(
            project_name="production",
            tables=[TableSchema(name="users", columns=[])]
        )

        compare_result = SchemaCompareResult(
            sample_project=sample,
            production_project=production,
            table_diffs=[
                TableDiff(
                    table_name="users",
                    diff_type="modified",
                    column_diffs=[
                        ColumnDiff(
                            table_name="users",
                            sample_column_name=None,
                            production_column_name="age",
                            diff_type="added",
                            detail={"production_dtype": "int64"}
                        ),
                        ColumnDiff(
                            table_name="users",
                            sample_column_name="nickname",
                            production_column_name=None,
                            diff_type="removed",
                            detail={"sample_dtype": "object"}
                        ),
                        ColumnDiff(
                            table_name="users",
                            sample_column_name="created_at",
                            production_column_name="created_at",
                            diff_type="type_changed",
                            detail={
                                "sample_dtype": "datetime64[ns]",
                                "production_dtype": "object"
                            }
                        ),
                        ColumnDiff(
                            table_name="users",
                            sample_column_name="user_name",
                            production_column_name="username",
                            diff_type="renamed",
                            detail={"reason": "normalized_name_match"}
                        ),
                    ]
                )
            ],
            summary={
                "added_tables": 0,
                "removed_tables": 0,
                "modified_tables": 1,
                "added_columns": 1,
                "removed_columns": 1,
                "type_changed_columns": 1,
                "renamed_columns": 1,
            }
        )

        report = report_analysis_result(compare_result)

        # サマリに各種カラム変更数が含まれていることを確認
        assert "**追加カラム数**: 1" in report
        assert "**削除カラム数**: 1" in report
        assert "**型変更カラム数**: 1" in report
        assert "**推定リネームカラム数**: 1" in report

        # 変更されたテーブルセクションが含まれていることを確認
        assert "### 変更されたテーブル" in report
        assert "#### テーブル: `users`" in report

        # 追加されたカラムセクション
        assert "##### 追加されたカラム" in report
        assert "`age`" in report

        # 削除されたカラムセクション
        assert "##### 削除されたカラム" in report
        assert "`nickname`" in report

        # 型が変更されたカラムセクション
        assert "##### 型が変更されたカラム" in report
        assert "`created_at`" in report
        assert "`datetime64[ns]`" in report
        assert "`object`" in report

        # リネームされたカラムセクション
        assert "##### 名前が変更された可能性のあるカラム" in report
        assert "`user_name`" in report
        assert "`username`" in report

    def test_report_structure(self):
        """レポートの構造を検証"""
        sample = ProjectSchema(
            project_name="サンプルプロジェクト",
            tables=[]
        )

        production = ProjectSchema(
            project_name="本番プロジェクト",
            tables=[]
        )

        compare_result = SchemaCompareResult(
            sample_project=sample,
            production_project=production,
            table_diffs=[],
            summary={
                "added_tables": 0,
                "removed_tables": 0,
                "modified_tables": 0,
                "added_columns": 0,
                "removed_columns": 0,
                "type_changed_columns": 0,
                "renamed_columns": 0,
            }
        )

        report = report_analysis_result(compare_result)

        # 必須セクションが含まれていることを確認
        assert "## プロジェクト情報" in report
        assert "サンプルプロジェクト" in report
        assert "本番プロジェクト" in report

        assert "## 概要" in report
        assert "### 差分サマリ" in report

        # フッターが含まれていることを確認
        assert "`compare_data_schemas`" in report


if __name__ == "__main__":
    print("テストを実行するには pytest を使用してください:")
    print("  pytest tests/test_report_generator.py -v")
