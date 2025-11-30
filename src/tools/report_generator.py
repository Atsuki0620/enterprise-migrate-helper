"""
レポート生成ツール

スキーマ比較結果を人間が読みやすい日本語の Markdown レポートとして整形します。
"""

from src.schemas import SchemaCompareResult, TableDiff, ColumnDiff


def report_analysis_result(compare_result: SchemaCompareResult) -> str:
    """
    スキーマ比較結果を、人間が読みやすい日本語の Markdown 文字列として整形する。

    Args:
        compare_result: スキーマ比較結果

    Returns:
        str: Markdown 形式のレポート文字列
    """
    lines = []

    # タイトル
    lines.append("# 本番データとサンプルデータの構造差分レポート")
    lines.append("")

    # プロジェクト情報
    lines.append("## プロジェクト情報")
    lines.append("")
    lines.append(f"- **サンプルプロジェクト**: {compare_result.sample_project.project_name or '(名前なし)'}")
    lines.append(f"- **本番プロジェクト**: {compare_result.production_project.project_name or '(名前なし)'}")
    lines.append("")

    # サマリ
    lines.append("## 概要")
    lines.append("")
    lines.append("このレポートは、サンプルデータと本番データのスキーマ構造を比較し、")
    lines.append("検出された差異を詳細に記述したものです。テーブルやカラムの追加・削除、")
    lines.append("データ型の変更、カラム名の変更など、構造的な違いを把握できます。")
    lines.append("")

    summary = compare_result.summary

    lines.append("### 差分サマリ")
    lines.append("")
    lines.append(f"- **追加テーブル数**: {summary.get('added_tables', 0)}")
    lines.append(f"- **削除テーブル数**: {summary.get('removed_tables', 0)}")
    lines.append(f"- **変更テーブル数**: {summary.get('modified_tables', 0)}")
    lines.append(f"- **追加カラム数**: {summary.get('added_columns', 0)}")
    lines.append(f"- **削除カラム数**: {summary.get('removed_columns', 0)}")
    lines.append(f"- **型変更カラム数**: {summary.get('type_changed_columns', 0)}")
    lines.append(f"- **推定リネームカラム数**: {summary.get('renamed_columns', 0)}")
    lines.append("")

    # 差分がない場合
    if not compare_result.table_diffs:
        lines.append("**差分は検出されませんでした。サンプルデータと本番データの構造は一致しています。**")
        lines.append("")
        # フッターを追加してから返す
        lines.append("---")
        lines.append("")
        lines.append("このレポートは、`compare_data_schemas` ツールによって自動生成されました。")
        lines.append("")
        return "\n".join(lines)

    # テーブルごとの差分詳細
    lines.append("## テーブルごとの差分詳細")
    lines.append("")

    # テーブルの追加
    added_tables = [td for td in compare_result.table_diffs if td.diff_type == "added"]
    if added_tables:
        lines.append("### 追加されたテーブル")
        lines.append("")
        lines.append("本番データにのみ存在し、サンプルデータには存在しないテーブルです。")
        lines.append("これらのテーブルは、本番環境で新たに追加された可能性があります。")
        lines.append("")
        for table_diff in added_tables:
            lines.append(f"- `{table_diff.table_name}`")
        lines.append("")

    # テーブルの削除
    removed_tables = [td for td in compare_result.table_diffs if td.diff_type == "removed"]
    if removed_tables:
        lines.append("### 削除されたテーブル")
        lines.append("")
        lines.append("サンプルデータにのみ存在し、本番データには存在しないテーブルです。")
        lines.append("これらのテーブルは、本番環境では使用されていない可能性があります。")
        lines.append("")
        for table_diff in removed_tables:
            lines.append(f"- `{table_diff.table_name}`")
        lines.append("")

    # 変更されたテーブル
    modified_tables = [td for td in compare_result.table_diffs if td.diff_type == "modified"]
    if modified_tables:
        lines.append("### 変更されたテーブル")
        lines.append("")
        lines.append("サンプルデータと本番データの両方に存在するが、カラム構成に差異があるテーブルです。")
        lines.append("各テーブルについて、検出された差異を詳細に記述します。")
        lines.append("")

        for table_diff in modified_tables:
            lines.append(f"#### テーブル: `{table_diff.table_name}`")
            lines.append("")

            # カラムごとの差分を分類
            added_cols = [cd for cd in table_diff.column_diffs if cd.diff_type == "added"]
            removed_cols = [cd for cd in table_diff.column_diffs if cd.diff_type == "removed"]
            type_changed_cols = [cd for cd in table_diff.column_diffs if cd.diff_type == "type_changed"]
            renamed_cols = [cd for cd in table_diff.column_diffs if cd.diff_type == "renamed"]

            # 追加されたカラム
            if added_cols:
                lines.append("##### 追加されたカラム")
                lines.append("")
                lines.append("本番データにのみ存在するカラムです。")
                lines.append("")
                for col_diff in added_cols:
                    dtype = col_diff.detail.get("production_dtype", "不明")
                    lines.append(f"- `{col_diff.production_column_name}` (型: `{dtype}`)")
                lines.append("")

            # 削除されたカラム
            if removed_cols:
                lines.append("##### 削除されたカラム")
                lines.append("")
                lines.append("サンプルデータにのみ存在するカラムです。")
                lines.append("")
                for col_diff in removed_cols:
                    dtype = col_diff.detail.get("sample_dtype", "不明")
                    lines.append(f"- `{col_diff.sample_column_name}` (型: `{dtype}`)")
                lines.append("")

            # 型が変更されたカラム
            if type_changed_cols:
                lines.append("##### 型が変更されたカラム")
                lines.append("")
                lines.append("カラム名は同じだが、データ型が異なるカラムです。")
                lines.append("型の不一致は、データ処理やバリデーションに影響を与える可能性があります。")
                lines.append("")

                # テーブル形式で出力
                lines.append("| カラム名 | サンプルの型 | 本番の型 |")
                lines.append("|----------|-------------|----------|")
                for col_diff in type_changed_cols:
                    col_name = col_diff.sample_column_name or col_diff.production_column_name
                    sample_dtype = col_diff.detail.get("sample_dtype", "不明")
                    production_dtype = col_diff.detail.get("production_dtype", "不明")
                    lines.append(f"| `{col_name}` | `{sample_dtype}` | `{production_dtype}` |")
                lines.append("")

            # 名前が変更された可能性のあるカラム
            if renamed_cols:
                lines.append("##### 名前が変更された可能性のあるカラム")
                lines.append("")
                lines.append("カラム名は異なるが、命名規則や文字列の類似性から")
                lines.append("リネームされた可能性が高いと推定されるカラムです。")
                lines.append("")

                # テーブル形式で出力
                lines.append("| サンプル側のカラム名 | 本番側のカラム名 | 推定理由 |")
                lines.append("|---------------------|-----------------|---------|")
                for col_diff in renamed_cols:
                    sample_name = col_diff.sample_column_name or "不明"
                    production_name = col_diff.production_column_name or "不明"
                    reason = col_diff.detail.get("reason", "不明")

                    # 理由を日本語に変換
                    reason_ja = {
                        "normalized_name_match": "正規化後の名前が一致",
                        "substring_match": "部分文字列の一致"
                    }.get(reason, reason)

                    lines.append(f"| `{sample_name}` | `{production_name}` | {reason_ja} |")
                lines.append("")

    # フッター
    lines.append("---")
    lines.append("")
    lines.append("このレポートは、`compare_data_schemas` ツールによって自動生成されました。")
    lines.append("")

    return "\n".join(lines)
