# プロジェクト移行支援エージェント

## プロジェクトの目的

このプロジェクトは、OpenAI Assistants APIを使用して、サンプルデータと本番データの構造的差異を分析するエージェントを開発します。

コーディングエージェントが作成したプロジェクト（サンプルデータを使用）と実際の本番データとの間にある構造的な違いを自動的に検出し、詳細なレポートを生成することで、プロジェクトの移行を支援します。

## セットアップ手順

### 1. 仮想環境の作成

```bash
python -m venv venv
```

または、Python 3.9以降を使用している場合:

```bash
python3 -m venv venv
```

### 2. 仮想環境のアクティベート

**Linux/macOS:**
```bash
source venv/bin/activate
```

**Windows:**
```cmd
venv\Scripts\activate
```

### 3. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 4. 環境変数の設定

`.env.example`ファイルを`.env`にコピーし、OpenAI APIキーを設定します。

```bash
cp .env.example .env
```

`.env`ファイルを編集して、有効なOpenAI APIキーを設定してください:

```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

## 実行方法

基本的な接続テストを実行するには、以下のコマンドを実行します:

```bash
python src/main.py
```

正常に動作すると、OpenAI Assistants APIとの接続が確認され、Assistantからの応答がコンソールに表示されます。

## 現在の実装状況

**Step 1 - 基本構造とAPI接続テスト** ✓ 完了

- プロジェクトディレクトリ構造の構築
- OpenAI Assistants APIとの基本的な接続テスト
- 環境設定とエラーハンドリングの実装

### 次のステップ

- Step 2: プロジェクト構造分析ツールの実装
- Step 3: データ差異検出機能の追加
- Step 4: レポート生成機能の実装

## 必要な環境

- Python 3.9以降
- OpenAI APIキー（GPT-4o対応）

## ディレクトリ構造

```
project-migration-agent/
├── src/
│   └── main.py              # メインスクリプト
├── tools/                    # ツール（後のステップで実装）
├── tests/                    # テスト（後のステップで実装）
├── requirements.txt          # 依存パッケージ一覧
├── .env.example             # 環境変数テンプレート
├── .env                     # 環境変数（gitignoreされます）
├── .gitignore               # Git除外設定
└── README.md                # このファイル
```

## ライセンス

このプロジェクトは開発中です。
