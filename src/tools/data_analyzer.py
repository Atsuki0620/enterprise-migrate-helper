"""
データ分析ツール

本番データの Excel/CSV ファイルを分析するツールを提供します。
"""

import json
from pathlib import Path
from agents import function_tool

from src.tools.schema_extractor import analyze_excel_csv_schema as _analyze_excel_csv_schema


@function_tool
def analyze_excel_csv_schema(root_dir: str, project_name: str | None = None) -> str:
    """
    指定ディレクトリ配下の Excel / CSV ファイルからスキーマ情報を抽出します。

    このツールは、本番データが格納されているディレクトリを分析し、
    各ファイルとそのカラム構造を詳細に抽出します。抽出される情報には、
    カラム名、データ型、欠損値の有無、サンプル値などが含まれます。

    Args:
        root_dir: 本番データが格納されているディレクトリパス（絶対パスまたは相対パス）
        project_name: プロジェクト名（任意）。指定しない場合はディレクトリ名が使用されます

    Returns:
        スキーマ情報を含む JSON 文字列。以下の構造を持ちます：
        {
            "project_name": "プロジェクト名",
            "tables": [
                {
                    "name": "テーブル名（ファイル名:シート名 または ファイル名）",
                    "path": "ファイルの物理パス",
                    "columns": [
                        {
                            "name": "カラム名",
                            "dtype": "データ型",
                            "nullable": true/false,
                            "example_values": ["サンプル値1", "サンプル値2", ...],
                            "notes": "補足情報（任意）"
                        },
                        ...
                    ]
                },
                ...
            ]
        }

    例:
        analyze_excel_csv_schema("/path/to/production/data", "本番データ分析")
    """
    try:
        # スキーマを抽出
        project_schema = _analyze_excel_csv_schema(root_dir, project_name)

        # Pydantic モデルを JSON 文字列に変換
        # model_dump() で辞書に変換し、json.dumps() で JSON 文字列化
        schema_dict = project_schema.model_dump()
        result_json = json.dumps(schema_dict, ensure_ascii=False, indent=2)

        return result_json

    except Exception as e:
        # エラーメッセージを返す
        error_msg = f"スキーマ抽出エラー: {str(e)}"
        return json.dumps({"error": error_msg}, ensure_ascii=False, indent=2)
