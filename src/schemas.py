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
