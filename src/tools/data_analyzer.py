"""
データ分析ツール

本番データの Excel/CSV ファイルを分析するツールと、
スキーマ比較ツールを提供します。
"""

import json
from pathlib import Path
from agents import function_tool

from src.tools.schema_extractor import analyze_excel_csv_schema as _analyze_excel_csv_schema
from src.tools.schema_comparator import compare_data_schemas as _compare_data_schemas
from src.tools.report_generator import report_analysis_result as _report_analysis_result
from src.schemas import ProjectSchema, SchemaCompareResult


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


@function_tool
def compare_data_schemas(
    sample_project_json: str,
    production_project_json: str
) -> str:
    """
    サンプルプロジェクトと本番プロジェクトのスキーマを比較し、構造的な差異を検出します。

    このツールは、2つのプロジェクトスキーマを比較し、以下の差異を検出します：
    - テーブルの追加・削除
    - カラムの追加・削除
    - データ型の変更
    - カラム名の変更（リネーム）

    Args:
        sample_project_json: サンプルプロジェクトのスキーマ（JSON文字列）
        production_project_json: 本番プロジェクトのスキーマ（JSON文字列）

    Returns:
        比較結果を含む JSON 文字列。以下の構造を持ちます：
        {
            "sample_project": {...},
            "production_project": {...},
            "table_diffs": [
                {
                    "table_name": "テーブル名",
                    "diff_type": "added|removed|modified",
                    "column_diffs": [...]
                },
                ...
            ],
            "summary": {
                "added_tables": 追加テーブル数,
                "removed_tables": 削除テーブル数,
                "modified_tables": 変更テーブル数,
                "added_columns": 追加カラム数,
                "removed_columns": 削除カラム数,
                "type_changed_columns": 型変更カラム数,
                "renamed_columns": リネームカラム数
            }
        }

    例:
        sample_schema = analyze_excel_csv_schema("/path/to/sample/data")
        production_schema = analyze_excel_csv_schema("/path/to/production/data")
        compare_result = compare_data_schemas(sample_schema, production_schema)
    """
    try:
        # JSON 文字列を ProjectSchema に変換
        sample_dict = json.loads(sample_project_json)
        production_dict = json.loads(production_project_json)

        sample_project = ProjectSchema(**sample_dict)
        production_project = ProjectSchema(**production_dict)

        # スキーマを比較
        compare_result = _compare_data_schemas(sample_project, production_project)

        # 結果を JSON 文字列に変換
        result_dict = compare_result.model_dump()
        result_json = json.dumps(result_dict, ensure_ascii=False, indent=2)

        return result_json

    except json.JSONDecodeError as e:
        error_msg = f"JSON パースエラー: {str(e)}"
        return json.dumps({"error": error_msg}, ensure_ascii=False, indent=2)
    except Exception as e:
        error_msg = f"スキーマ比較エラー: {str(e)}"
        return json.dumps({"error": error_msg}, ensure_ascii=False, indent=2)


@function_tool
def report_analysis_result(compare_result_json: str) -> str:
    """
    スキーマ比較結果を人間が読みやすい日本語の Markdown レポートとして整形します。

    このツールは、`compare_data_schemas` の結果を受け取り、
    テーブルやカラムの差異を分かりやすく記述した Markdown 形式のレポートを生成します。

    Args:
        compare_result_json: スキーマ比較結果（SchemaCompareResult の JSON文字列）

    Returns:
        Markdown 形式のレポート文字列。以下の内容が含まれます：
        - プロジェクト情報
        - 差分サマリ（追加/削除/変更されたテーブル・カラムの数）
        - テーブルごとの差分詳細
          - 追加されたテーブル
          - 削除されたテーブル
          - 変更されたテーブル（カラムレベルの差分を含む）

    例:
        compare_result = compare_data_schemas(sample_schema, production_schema)
        markdown_report = report_analysis_result(compare_result)
    """
    try:
        # JSON 文字列を SchemaCompareResult に変換
        compare_result_dict = json.loads(compare_result_json)
        compare_result = SchemaCompareResult(**compare_result_dict)

        # Markdown レポートを生成
        markdown_report = _report_analysis_result(compare_result)

        return markdown_report

    except json.JSONDecodeError as e:
        error_msg = f"JSON パースエラー: {str(e)}"
        return f"# エラー\n\n{error_msg}"
    except Exception as e:
        error_msg = f"レポート生成エラー: {str(e)}"
        return f"# エラー\n\n{error_msg}"
