"""
スキーマ比較ツール

サンプルプロジェクトと本番プロジェクトのスキーマを比較し、
構造的な差異を検出する機能を提供します。
"""

import logging
from typing import Dict, List, Set, Tuple, Optional

from src.schemas import (
    ProjectSchema,
    TableSchema,
    ColumnSchema,
    ColumnDiff,
    TableDiff,
    SchemaCompareResult,
)

# ロギング設定
logger = logging.getLogger(__name__)


def compare_data_schemas(
    sample_project: ProjectSchema,
    production_project: ProjectSchema,
) -> SchemaCompareResult:
    """
    サンプルプロジェクトと本番プロジェクトのスキーマを比較し、差分を検出する。

    Args:
        sample_project: サンプルプロジェクトのスキーマ
        production_project: 本番プロジェクトのスキーマ

    Returns:
        SchemaCompareResult: 比較結果（差分情報を含む）
    """
    logger.info(
        f"スキーマ比較を開始: サンプル='{sample_project.project_name}', "
        f"本番='{production_project.project_name}'"
    )

    # テーブル名のマッピングを作成
    sample_tables_map = {table.name: table for table in sample_project.tables}
    production_tables_map = {table.name: table for table in production_project.tables}

    sample_table_names = set(sample_tables_map.keys())
    production_table_names = set(production_tables_map.keys())

    # テーブルレベルの差分を検出
    table_diffs: List[TableDiff] = []

    # 追加されたテーブル（本番にのみ存在）
    added_tables = production_table_names - sample_table_names
    for table_name in added_tables:
        table_diffs.append(
            TableDiff(
                table_name=table_name,
                diff_type="added",
                column_diffs=[]
            )
        )
        logger.info(f"テーブル追加を検出: {table_name}")

    # 削除されたテーブル（サンプルにのみ存在）
    removed_tables = sample_table_names - production_table_names
    for table_name in removed_tables:
        table_diffs.append(
            TableDiff(
                table_name=table_name,
                diff_type="removed",
                column_diffs=[]
            )
        )
        logger.info(f"テーブル削除を検出: {table_name}")

    # 両方に存在するテーブル（カラムレベルの比較が必要）
    common_tables = sample_table_names & production_table_names
    for table_name in common_tables:
        sample_table = sample_tables_map[table_name]
        production_table = production_tables_map[table_name]

        column_diffs = _compare_table_columns(
            table_name, sample_table, production_table
        )

        if column_diffs:
            table_diffs.append(
                TableDiff(
                    table_name=table_name,
                    diff_type="modified",
                    column_diffs=column_diffs
                )
            )
            logger.info(f"テーブル変更を検出: {table_name} (カラム差分数: {len(column_diffs)})")

    # 集計情報を計算
    summary = _calculate_summary(table_diffs)

    logger.info(
        f"スキーマ比較完了: 追加テーブル={summary['added_tables']}, "
        f"削除テーブル={summary['removed_tables']}, "
        f"変更テーブル={summary['modified_tables']}, "
        f"追加カラム={summary['added_columns']}, "
        f"削除カラム={summary['removed_columns']}, "
        f"型変更カラム={summary['type_changed_columns']}, "
        f"リネームカラム={summary['renamed_columns']}"
    )

    return SchemaCompareResult(
        sample_project=sample_project,
        production_project=production_project,
        table_diffs=table_diffs,
        summary=summary
    )


def _compare_table_columns(
    table_name: str,
    sample_table: TableSchema,
    production_table: TableSchema,
) -> List[ColumnDiff]:
    """
    同一テーブル内のカラムを比較し、差分を検出する。

    Args:
        table_name: テーブル名
        sample_table: サンプル側のテーブルスキーマ
        production_table: 本番側のテーブルスキーマ

    Returns:
        List[ColumnDiff]: カラムレベルの差分リスト
    """
    column_diffs: List[ColumnDiff] = []

    # カラム名のマッピングを作成
    sample_columns_map = {col.name: col for col in sample_table.columns}
    production_columns_map = {col.name: col for col in production_table.columns}

    sample_column_names = set(sample_columns_map.keys())
    production_column_names = set(production_columns_map.keys())

    # 両方に存在するカラム（型変更をチェック）
    common_columns = sample_column_names & production_column_names
    for col_name in common_columns:
        sample_col = sample_columns_map[col_name]
        production_col = production_columns_map[col_name]

        # データ型の比較
        if sample_col.dtype != production_col.dtype:
            column_diffs.append(
                ColumnDiff(
                    table_name=table_name,
                    sample_column_name=col_name,
                    production_column_name=col_name,
                    diff_type="type_changed",
                    detail={
                        "sample_dtype": sample_col.dtype,
                        "production_dtype": production_col.dtype,
                    }
                )
            )

    # サンプルにのみ存在するカラム
    sample_only_columns = sample_column_names - production_column_names

    # 本番にのみ存在するカラム
    production_only_columns = production_column_names - sample_column_names

    # リネーム候補を検出
    rename_pairs = _detect_renames(
        table_name,
        sample_only_columns,
        production_only_columns,
        sample_columns_map,
        production_columns_map
    )

    # リネーム候補を ColumnDiff に追加
    renamed_sample_cols = set()
    renamed_production_cols = set()
    for sample_col_name, production_col_name, reason in rename_pairs:
        column_diffs.append(
            ColumnDiff(
                table_name=table_name,
                sample_column_name=sample_col_name,
                production_column_name=production_col_name,
                diff_type="renamed",
                detail={
                    "reason": reason,
                    "sample_dtype": sample_columns_map[sample_col_name].dtype,
                    "production_dtype": production_columns_map[production_col_name].dtype,
                }
            )
        )
        renamed_sample_cols.add(sample_col_name)
        renamed_production_cols.add(production_col_name)

    # リネーム以外の削除されたカラム
    for col_name in sample_only_columns - renamed_sample_cols:
        column_diffs.append(
            ColumnDiff(
                table_name=table_name,
                sample_column_name=col_name,
                production_column_name=None,
                diff_type="removed",
                detail={
                    "sample_dtype": sample_columns_map[col_name].dtype,
                }
            )
        )

    # リネーム以外の追加されたカラム
    for col_name in production_only_columns - renamed_production_cols:
        column_diffs.append(
            ColumnDiff(
                table_name=table_name,
                sample_column_name=None,
                production_column_name=col_name,
                diff_type="added",
                detail={
                    "production_dtype": production_columns_map[col_name].dtype,
                }
            )
        )

    return column_diffs


def _detect_renames(
    table_name: str,
    sample_only_columns: Set[str],
    production_only_columns: Set[str],
    sample_columns_map: Dict[str, ColumnSchema],
    production_columns_map: Dict[str, ColumnSchema],
) -> List[Tuple[str, str, str]]:
    """
    カラム名の変更（リネーム）候補を検出する。

    Args:
        table_name: テーブル名
        sample_only_columns: サンプルにのみ存在するカラム名のセット
        production_only_columns: 本番にのみ存在するカラム名のセット
        sample_columns_map: サンプル側のカラムマップ
        production_columns_map: 本番側のカラムマップ

    Returns:
        List[Tuple[str, str, str]]: (サンプルカラム名, 本番カラム名, 理由) のリスト
    """
    rename_pairs: List[Tuple[str, str, str]] = []

    for sample_col_name in sample_only_columns:
        for production_col_name in production_only_columns:
            # 正規化した名前が一致するかチェック
            normalized_sample = _normalize_column_name(sample_col_name)
            normalized_production = _normalize_column_name(production_col_name)

            if normalized_sample == normalized_production:
                rename_pairs.append(
                    (sample_col_name, production_col_name, "normalized_name_match")
                )
                logger.info(
                    f"リネーム候補を検出: {table_name}.{sample_col_name} -> "
                    f"{production_col_name} (正規化一致)"
                )
                break

            # 片方がもう片方を含む場合（長さが近い場合のみ）
            len_diff = abs(len(sample_col_name) - len(production_col_name))
            if len_diff <= 3:
                if sample_col_name.lower() in production_col_name.lower():
                    rename_pairs.append(
                        (sample_col_name, production_col_name, "substring_match")
                    )
                    logger.info(
                        f"リネーム候補を検出: {table_name}.{sample_col_name} -> "
                        f"{production_col_name} (部分文字列一致)"
                    )
                    break
                elif production_col_name.lower() in sample_col_name.lower():
                    rename_pairs.append(
                        (sample_col_name, production_col_name, "substring_match")
                    )
                    logger.info(
                        f"リネーム候補を検出: {table_name}.{sample_col_name} -> "
                        f"{production_col_name} (部分文字列一致)"
                    )
                    break

    return rename_pairs


def _normalize_column_name(name: str) -> str:
    """
    カラム名を正規化する（小文字化、アンダースコア・スペース除去）。

    Args:
        name: カラム名

    Returns:
        str: 正規化されたカラム名
    """
    return name.lower().replace("_", "").replace(" ", "").replace("-", "")


def _calculate_summary(table_diffs: List[TableDiff]) -> Dict[str, int]:
    """
    差分の集計情報を計算する。

    Args:
        table_diffs: テーブルレベルの差分リスト

    Returns:
        Dict[str, int]: 集計情報の辞書
    """
    summary = {
        "added_tables": 0,
        "removed_tables": 0,
        "modified_tables": 0,
        "added_columns": 0,
        "removed_columns": 0,
        "type_changed_columns": 0,
        "renamed_columns": 0,
    }

    for table_diff in table_diffs:
        if table_diff.diff_type == "added":
            summary["added_tables"] += 1
        elif table_diff.diff_type == "removed":
            summary["removed_tables"] += 1
        elif table_diff.diff_type == "modified":
            summary["modified_tables"] += 1

            for col_diff in table_diff.column_diffs:
                if col_diff.diff_type == "added":
                    summary["added_columns"] += 1
                elif col_diff.diff_type == "removed":
                    summary["removed_columns"] += 1
                elif col_diff.diff_type == "type_changed":
                    summary["type_changed_columns"] += 1
                elif col_diff.diff_type == "renamed":
                    summary["renamed_columns"] += 1

    return summary
