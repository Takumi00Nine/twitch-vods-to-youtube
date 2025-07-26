# Cron設定ガイド

## 基本的なcron設定

### 1. crontabを編集
```bash
crontab -e
```

### 2. 毎日午前9時に実行する設定例
```bash
# 毎日午前9時に実行
0 9 * * * /bin/bash /home/takumi009/work/twitch-vods-to-youtube/run_upload.sh

# 毎日午前6時に実行
0 6 * * * /bin/bash /home/takumi009/work/twitch-vods-to-youtube/run_upload.sh

# 毎日午前0時に実行
0 0 * * * /bin/bash /home/takumi009/work/twitch-vods-to-youtube/run_upload.sh
```

## cron設定の説明

### 時間指定の形式
```
分 時 日 月 曜日 コマンド
```

### よく使う設定例
```bash
# 毎日午前9時
0 9 * * * /path/to/run_upload.sh

# 毎日午前6時と午後6時
0 6,18 * * * /path/to/run_upload.sh

# 毎週月曜日の午前9時
0 9 * * 1 /path/to/run_upload.sh

# 毎月1日の午前9時
0 9 1 * * /path/to/run_upload.sh

# 毎時0分（1時間ごと）
0 * * * * /path/to/run_upload.sh
```

## 環境変数の設定

cronで実行する場合、環境変数が読み込まれない可能性があります。以下の方法で解決できます：

### 方法1: crontabで環境変数を設定
```bash
# crontabの先頭に追加
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
HOME=/home/takumi009

# 環境変数を設定
TWITCH_CLIENT_ID=your_twitch_client_id
TWITCH_CLIENT_SECRET=your_twitch_client_secret
TWITCH_CHANNEL_NAME=your_channel_name
YOUTUBE_CLIENT_ID=your_youtube_client_id
YOUTUBE_CLIENT_SECRET=your_youtube_client_secret

# 実行コマンド
0 9 * * * /bin/bash /home/takumi009/work/twitch-vods-to-youtube/run_upload.sh
```

### 方法2: .envファイルを使用
`.env`ファイルをプロジェクトディレクトリに配置し、`run_upload.sh`で読み込むように設定済みです。

## ログの確認

### 実行ログの確認
```bash
# 最新のログを確認
ls -la logs/
tail -f logs/upload_$(date +%Y%m%d)*.log

# すべてのログを確認
cat logs/upload_*.log
```

### cronの実行ログを確認
```bash
# cronの実行ログを確認
sudo tail -f /var/log/syslog | grep CRON

# または
sudo journalctl -f | grep CRON
```

## トラブルシューティング

### 1. パスの問題
絶対パスを使用してください：
```bash
# 正しい例
0 9 * * * /bin/bash /home/takumi009/work/twitch-vods-to-youtube/run_upload.sh

# 間違った例
0 9 * * * ./run_upload.sh
```

### 2. 権限の問題
```bash
# 実行権限を確認
ls -la run_upload.sh

# 必要に応じて権限を付与
chmod +x run_upload.sh
```

### 3. 環境変数の問題
```bash
# 手動でテスト実行
cd /home/takumi009/work/twitch-vods-to-youtube
./run_upload.sh
```

### 4. Python環境の問題
```bash
# 仮想環境を使用している場合
0 9 * * * /home/takumi009/work/twitch-vods-to-youtube/venv/bin/python /home/takumi009/work/twitch-vods-to-youtube/main.py
```

## 推奨設定

### 毎日午前9時に実行（推奨）
```bash
0 9 * * * /home/takumi009/work/twitch-vods-to-youtube/run_upload.sh
```

この設定により、前日の配信アーカイブが毎日午前9時に自動的にYouTubeにアップロードされます。 