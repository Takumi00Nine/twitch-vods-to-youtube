#!/bin/bash

# Twitch配信アーカイブ YouTube自動アップロード実行スクリプト

# スクリプトのディレクトリに移動
cd "$(dirname "$0")"

# .envファイルの存在チェック
if [ ! -f ".env" ]; then
    echo "$(date): エラー: .envファイルが見つかりません" | tee -a "$LOG_FILE"
    echo ".env.exampleを参考に.envファイルを作成してください"
    exit 1
fi

# ログファイルの設定
LOG_DIR="./logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/upload_$(date +%Y%m%d_%H%M%S).log"

# 実行開始ログ
echo "$(date): アップロード処理を開始します" | tee -a "$LOG_FILE"

# Python仮想環境がある場合はアクティベート
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "$(date): 仮想環境をアクティベートしました" | tee -a "$LOG_FILE"
fi

# メインスクリプトを実行
python main.py 2>&1 | tee -a "$LOG_FILE"

# 実行終了ログ
echo "$(date): アップロード処理が完了しました" | tee -a "$LOG_FILE"

# 古いログファイルを削除（30日以上前）
find "$LOG_DIR" -name "upload_*.log" -mtime +30 -delete 