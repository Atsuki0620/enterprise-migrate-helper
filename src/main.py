#!/usr/bin/env python3
"""
プロジェクト移行支援エージェント - メインスクリプト
OpenAI Assistants APIを使用した基本的な接続テストを実行します。
"""

import os
import sys
import time
import traceback
from dotenv import load_dotenv
from openai import OpenAI


def main():
    """
    メイン処理
    OpenAI Assistants APIの接続テストを実行します。
    """
    print("=== OpenAI Assistants API 接続テスト ===\n")

    # 1. 環境変数の読み込み
    print("1. 環境変数を読み込んでいます...")
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("エラー: OPENAI_API_KEYが設定されていません。", file=sys.stderr)
        print(".envファイルを作成し、OPENAI_API_KEYを設定してください。", file=sys.stderr)
        sys.exit(1)

    # APIキーから引用符（通常のものと特殊なUnicode文字）を削除
    # '\u201c' = " (左ダブルクォーテーション)
    # '\u201d' = " (右ダブルクォーテーション)
    # '\u2018' = ' (左シングルクォーテーション)
    # '\u2019' = ' (右シングルクォーテーション)
    api_key = api_key.strip()
    # 通常の引用符とUnicode引用符を削除
    quote_chars = '"\'\u201c\u201d\u2018\u2019'
    api_key = api_key.strip(quote_chars)

    # クリーンアップされたAPIキーを環境変数にも設定（OpenAI SDKが直接参照する場合に備えて）
    os.environ["OPENAI_API_KEY"] = api_key

    print("✓ 環境変数の読み込み完了\n")

    # 2. OpenAIクライアントの初期化
    print("2. OpenAIクライアントを初期化しています...")
    try:
        client = OpenAI(api_key=api_key)
        print("✓ OpenAIクライアントの初期化完了\n")
    except Exception as e:
        print(f"エラー: OpenAIクライアントの初期化に失敗しました: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)

    # 3. Assistantの作成
    print("3. Assistantを作成しています...")
    try:
        assistant = client.beta.assistants.create(
            name="Project Analysis Agent",
            instructions="You are a helpful assistant that analyzes project structures.",
            model="gpt-4o"
        )
        print(f"✓ Assistantの作成完了 (ID: {assistant.id})\n")
    except Exception as e:
        print(f"エラー: Assistantの作成に失敗しました: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)

    # 4. 新しいThreadの作成
    print("4. 新しいThreadを作成しています...")
    try:
        thread = client.beta.threads.create()
        print(f"✓ Threadの作成完了 (ID: {thread.id})\n")
    except Exception as e:
        print(f"エラー: Threadの作成に失敗しました: {e}", file=sys.stderr)
        # Assistantをクリーンアップ
        cleanup_assistant(client, assistant.id)
        sys.exit(1)

    # 5. Threadへのメッセージ追加
    print("5. Threadにメッセージを追加しています...")
    try:
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content="Hello, please confirm you are working correctly."
        )
        print(f"✓ メッセージの追加完了 (ID: {message.id})\n")
    except Exception as e:
        print(f"エラー: メッセージの追加に失敗しました: {e}", file=sys.stderr)
        # Assistantをクリーンアップ
        cleanup_assistant(client, assistant.id)
        sys.exit(1)

    # 6. Runの作成と実行
    print("6. Runを作成・実行しています...")
    try:
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )
        print(f"✓ Runの作成完了 (ID: {run.id})\n")
    except Exception as e:
        print(f"エラー: Runの作成に失敗しました: {e}", file=sys.stderr)
        # Assistantをクリーンアップ
        cleanup_assistant(client, assistant.id)
        sys.exit(1)

    # 7. Runステータスのポーリング（完了まで待機）
    print("7. Runの完了を待機しています...")
    max_wait_time = 60  # 最大待機時間（秒）
    elapsed_time = 0
    poll_interval = 1  # ポーリング間隔（秒）

    try:
        while elapsed_time < max_wait_time:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )

            if run_status.status == "completed":
                print(f"✓ Runが完了しました (経過時間: {elapsed_time}秒)\n")
                break
            elif run_status.status in ["failed", "cancelled", "expired"]:
                print(f"エラー: Runが失敗しました (ステータス: {run_status.status})", file=sys.stderr)
                if run_status.last_error:
                    print(f"エラー詳細: {run_status.last_error}", file=sys.stderr)
                # Assistantをクリーンアップ
                cleanup_assistant(client, assistant.id)
                sys.exit(1)

            # ステータスを表示
            print(f"  現在のステータス: {run_status.status} (経過時間: {elapsed_time}秒)")
            time.sleep(poll_interval)
            elapsed_time += poll_interval

        if elapsed_time >= max_wait_time:
            print(f"エラー: タイムアウトしました（{max_wait_time}秒）", file=sys.stderr)
            # Assistantをクリーンアップ
            cleanup_assistant(client, assistant.id)
            sys.exit(1)

    except Exception as e:
        print(f"エラー: Runステータスの取得に失敗しました: {e}", file=sys.stderr)
        # Assistantをクリーンアップ
        cleanup_assistant(client, assistant.id)
        sys.exit(1)

    # 8. Assistantの応答を取得して表示
    print("8. Assistantの応答を取得しています...")
    try:
        messages = client.beta.threads.messages.list(
            thread_id=thread.id,
            order="asc"
        )

        # 最新のアシスタントメッセージを取得
        assistant_messages = [msg for msg in messages.data if msg.role == "assistant"]

        if assistant_messages:
            latest_message = assistant_messages[-1]
            print("✓ 応答の取得完了\n")
            print("=" * 50)
            print("Assistantからの応答:")
            print("=" * 50)

            # メッセージの内容を表示
            for content in latest_message.content:
                if content.type == "text":
                    print(content.text.value)

            print("=" * 50)
        else:
            print("警告: Assistantからの応答が見つかりませんでした。", file=sys.stderr)

    except Exception as e:
        print(f"エラー: 応答の取得に失敗しました: {e}", file=sys.stderr)
        # Assistantをクリーンアップ
        cleanup_assistant(client, assistant.id)
        sys.exit(1)

    # クリーンアップ
    print("\n9. Assistantをクリーンアップしています...")
    cleanup_assistant(client, assistant.id)

    print("\n=== テスト完了 ===")


def cleanup_assistant(client, assistant_id):
    """
    Assistantを削除してクリーンアップします。

    Args:
        client: OpenAIクライアント
        assistant_id: 削除するAssistantのID
    """
    try:
        client.beta.assistants.delete(assistant_id)
        print(f"✓ Assistant (ID: {assistant_id}) を削除しました")
    except Exception as e:
        print(f"警告: Assistantの削除に失敗しました: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
