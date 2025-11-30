"""
スキーマ抽出ツール

Excel/CSVファイルからスキーマ情報を抽出する機能を提供します。
"""

import logging
from pathlib import Path
from typing import Union, List
import pandas as pd

from src.schemas import ProjectSchema, TableSchema, ColumnSchema

# ロギング設定
logger = logging.getLogger(__name__)


def analyze_excel_csv_schema(
    root_dir: Union[str, Path],
    project_name: str | None = None
) -> ProjectSchema:
    """
    指定ディレクトリ配下の Excel / CSV からスキーマ情報を抽出し、ProjectSchema として返す。

    Args:
        root_dir: 本番データが格納されているディレクトリパス（str or Path）
        project_name: 任意。ProjectSchema.project_name にセットするための名前

    Returns:
        ProjectSchema: 抽出されたスキーマ情報

    Raises:
        ValueError: root_dir が存在しないディレクトリの場合
    """
    root_path = Path(root_dir).resolve()

    if not root_path.exists():
        raise ValueError(f"指定されたディレクトリが存在しません: {root_path}")

    if not root_path.is_dir():
        raise ValueError(f"指定されたパスはディレクトリではありません: {root_path}")

    logger.info(f"スキーマ抽出を開始: {root_path}")

    tables: List[TableSchema] = []

    # Excel および CSV ファイルを再帰的に探索
    excel_files = list(root_path.rglob("*.xlsx")) + list(root_path.rglob("*.xls"))
    csv_files = list(root_path.rglob("*.csv"))

    total_files = len(excel_files) + len(csv_files)
    logger.info(f"対象ファイル数: Excel={len(excel_files)}, CSV={len(csv_files)}, 合計={total_files}")

    # Excel ファイルの処理
    for excel_file in excel_files:
        try:
            tables.extend(_process_excel_file(excel_file))
        except Exception as e:
            logger.warning(f"Excel ファイルの読み込みに失敗しました: {excel_file} - {e}")

    # CSV ファイルの処理
    for csv_file in csv_files:
        try:
            table = _process_csv_file(csv_file)
            if table:
                tables.append(table)
        except Exception as e:
            logger.warning(f"CSV ファイルの読み込みに失敗しました: {csv_file} - {e}")

    logger.info(f"生成された TableSchema 数: {len(tables)}")

    return ProjectSchema(
        project_name=project_name or root_path.name,
        tables=tables
    )


def _process_excel_file(file_path: Path) -> List[TableSchema]:
    """
    Excel ファイルを読み込み、各シートから TableSchema を生成する。

    Args:
        file_path: Excel ファイルのパス

    Returns:
        List[TableSchema]: 各シートの TableSchema のリスト
    """
    tables = []

    try:
        # すべてのシート名を取得
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names

        for sheet_name in sheet_names:
            try:
                # シートをDataFrameとして読み込み
                df = pd.read_excel(file_path, sheet_name=sheet_name)

                # テーブル名を "ファイル名.xlsx:シート名" の形式で作成
                table_name = f"{file_path.name}:{sheet_name}"

                # ColumnSchema のリストを生成
                columns = _extract_column_schemas(df)

                # TableSchema を作成
                table = TableSchema(
                    name=table_name,
                    path=str(file_path),
                    columns=columns
                )
                tables.append(table)

                logger.info(f"Excel シートを処理しました: {table_name} (カラム数: {len(columns)})")

            except Exception as e:
                logger.warning(f"Excel シートの読み込みに失敗しました: {file_path}:{sheet_name} - {e}")

    except Exception as e:
        logger.warning(f"Excel ファイルのオープンに失敗しました: {file_path} - {e}")

    return tables


def _process_csv_file(file_path: Path) -> TableSchema | None:
    """
    CSV ファイルを読み込み、TableSchema を生成する。

    Args:
        file_path: CSV ファイルのパス

    Returns:
        TableSchema | None: 生成された TableSchema、または失敗時は None
    """
    try:
        # CSV をDataFrameとして読み込み
        df = pd.read_csv(file_path)

        # テーブル名を拡張子なしのファイル名とする
        table_name = file_path.stem

        # ColumnSchema のリストを生成
        columns = _extract_column_schemas(df)

        # TableSchema を作成
        table = TableSchema(
            name=table_name,
            path=str(file_path),
            columns=columns
        )

        logger.info(f"CSV ファイルを処理しました: {table_name} (カラム数: {len(columns)})")

        return table

    except Exception as e:
        logger.warning(f"CSV ファイルの読み込みに失敗しました: {file_path} - {e}")
        return None


def _extract_column_schemas(df: pd.DataFrame) -> List[ColumnSchema]:
    """
    DataFrame からカラムスキーマのリストを抽出する。

    Args:
        df: pandas DataFrame

    Returns:
        List[ColumnSchema]: ColumnSchema のリスト
    """
    columns = []

    for col_name in df.columns:
        # データ型を取得
        dtype_str = str(df[col_name].dtype)

        # 欠損値の有無を判定
        has_nulls = df[col_name].isna().any()

        # サンプル値を取得（最大5件、欠損値を除外）
        sample_values = df[col_name].dropna().head(5).astype(str).tolist()

        # ColumnSchema を作成
        column = ColumnSchema(
            name=str(col_name),
            dtype=dtype_str,
            nullable=bool(has_nulls),
            example_values=sample_values
        )
        columns.append(column)

    return columns
