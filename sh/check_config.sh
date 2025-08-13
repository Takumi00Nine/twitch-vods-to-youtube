#!/bin/bash

# 設定確認スクリプト
# Twitch/YouTube設定の確認を行います

echo "=================================================="
echo "Twitch/YouTube設定確認スクリプト"
echo "=================================================="

# プロジェクトルートディレクトリに移動
cd "$(dirname "$0")/.."

# .envファイルの存在確認
if [ ! -f "env/.env" ]; then
    echo "❌ env/.envファイルが見つかりません"
    echo "env/.envファイルを作成してください"
    exit 1
fi

# 仮想環境の確認
if [ ! -d "venv" ]; then
    echo "❌ 仮想環境(venv)が見つかりません"
    echo "python -m venv venv で仮想環境を作成してください"
    exit 1
fi

# 仮想環境をアクティベート
echo "仮想環境をアクティベート中..."
source venv/bin/activate

# 依存関係の確認
echo "依存関係を確認中..."
if ! python -c "import requests, google.auth, yt_dlp, pytz" 2>/dev/null; then
    echo "❌ 必要な依存関係がインストールされていません"
    echo "pip install -r requirements.txt を実行してください"
    exit 1
fi

# appディレクトリに移動してcheck_config.pyを実行
echo "設定確認を開始します..."
cd app
python check_config.py "$@"

# 終了コードを取得
exit_code=$?

echo "=================================================="
if [ $exit_code -eq 0 ]; then
    echo "✅ 設定確認が完了しました"
else
    echo "❌ 設定確認でエラーが発生しました"
fi
echo "=================================================="

exit $exit_code 