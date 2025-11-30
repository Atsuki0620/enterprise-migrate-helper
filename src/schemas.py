"""
共通スキーマモデル定義

本番データとサンプルデータのスキーマ情報を表現するための
Pydantic モデルを定義します。
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class ColumnSchema(BaseModel):
    """
    カラムのスキーマ情報を表現するモデル

    Attributes:
        name: カラム名
        dtype: データ型（"int64", "float64", "object", "datetime64[ns]" など）
        nullable: カラムに欠損値が含まれるか（True/False/None）
        example_values: サンプル値（文字列化したものを数件）
        notes: 補足情報（任意）
    """
    name: str = Field(..., description="カラム名")
    dtype: str = Field(..., description="データ型（pandas dtypeの文字列表現）")
    nullable: Optional[bool] = Field(None, description="欠損値の有無")
    example_values: List[str] = Field(default_factory=list, description="サンプル値のリスト")
    notes: Optional[str] = Field(None, description="補足情報")


class TableSchema(BaseModel):
    """
    テーブル（ファイルまたはシート）のスキーマ情報を表現するモデル

    Attributes:
        name: テーブル名（ファイル名 + シート名など）
        path: 物理ファイルパス（任意）
        columns: カラムスキーマのリスト
    """
    name: str = Field(..., description="テーブル名")
    path: Optional[str] = Field(None, description="物理ファイルパス")
    columns: List[ColumnSchema] = Field(default_factory=list, description="カラムスキーマのリスト")


class ProjectSchema(BaseModel):
    """
    プロジェクト全体のスキーマ情報を表現するモデル

    Attributes:
        project_name: プロジェクト名（任意）
        tables: テーブルスキーマのリスト
    """
    project_name: Optional[str] = Field(None, description="プロジェクト名")
    tables: List[TableSchema] = Field(default_factory=list, description="テーブルスキーマのリスト")


# ==================== スキーマ差分モデル ====================


class ColumnDiff(BaseModel):
    """
    カラムレベルの差分情報を表現するモデル

    Attributes:
        table_name: 対象テーブル名
        sample_column_name: サンプル側のカラム名（削除・リネームの場合に使用）
        production_column_name: 本番側のカラム名（追加・リネームの場合に使用）
        diff_type: 差分の種類（"added", "removed", "type_changed", "renamed"）
        detail: 差分の詳細情報（型情報、推定理由など）
    """
    table_name: str = Field(..., description="対象テーブル名")
    sample_column_name: Optional[str] = Field(None, description="サンプル側のカラム名")
    production_column_name: Optional[str] = Field(None, description="本番側のカラム名")
    diff_type: str = Field(..., description="差分の種類")
    detail: Dict[str, Any] = Field(default_factory=dict, description="差分の詳細情報")


class TableDiff(BaseModel):
    """
    テーブルレベルの差分情報を表現するモデル

    Attributes:
        table_name: 対象テーブル名
        diff_type: 差分の種類（"added", "removed", "modified"）
        column_diffs: カラムレベルの差分リスト（modified の場合のみ）
    """
    table_name: str = Field(..., description="対象テーブル名")
    diff_type: str = Field(..., description="差分の種類")
    column_diffs: List[ColumnDiff] = Field(default_factory=list, description="カラムレベルの差分リスト")


class SchemaCompareResult(BaseModel):
    """
    スキーマ比較の結果全体を表現するモデル

    Attributes:
        sample_project: サンプルプロジェクトのスキーマ
        production_project: 本番プロジェクトのスキーマ
        table_diffs: テーブルレベルの差分リスト
        summary: 差分の集計情報
    """
    sample_project: ProjectSchema = Field(..., description="サンプルプロジェクトのスキーマ")
    production_project: ProjectSchema = Field(..., description="本番プロジェクトのスキーマ")
    table_diffs: List[TableDiff] = Field(default_factory=list, description="テーブルレベルの差分リスト")
    summary: Dict[str, Any] = Field(default_factory=dict, description="差分の集計情報")
