# Twitch配信アーカイブ YouTube自動アップロード

Twitch APIを使用して前日分の配信アーカイブを自動的にYouTubeにアップロードするPythonスクリプトです。

## 機能

- Twitch APIを使用した配信アーカイブの自動取得
- YouTube APIを使用した動画の自動アップロード
- 日本時間（JST）での前日分動画の自動取得
- スケジュール実行（毎日指定時刻に自動実行）
- 手動実行（指定した日数前の動画をアップロード）
- 動画長の制限機能（YouTubeの12時間制限を超える動画はスキップ）
- 古いファイルの自動クリーンアップ
- 動画説明にTwitchチャンネルURLを自動追加

## 必要な環境

- Python 3.7以上
- yt-dlp（動画ダウンロード・情報取得用）- pipでインストール
- pytz（タイムゾーン処理用）- pipでインストール

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```



### 3. API設定

#### Twitch API設定
1. [Twitch Developer Console](https://dev.twitch.tv/console) にアクセス
2. 新しいアプリケーションを作成
3. Client IDとClient Secretを取得

#### YouTube API設定
1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成
3. **YouTube Data API v3**を有効化：
   - 「APIとサービス」→「ライブラリ」
   - 「YouTube Data API v3」を検索して有効化
4. **OAuth 2.0クライアントID**を作成：
   - 「APIとサービス」→「認証情報」
   - 「認証情報を作成」→「OAuth 2.0クライアントID」
   - アプリケーションの種類：「デスクトップアプリケーション」
   - 名前：任意（例：「Twitch VOD Uploader」）
5. **client_secret.json**をダウンロードしてプロジェクトルートに配置

### 4. .envファイルの設定

`.env.example`を参考に`.env`ファイルを作成して以下の設定を追加：

```bash
# テンプレートをコピー
cp .env.example .env

# .envファイルを編集
nano .env
```

`.env`ファイルの内容例：

```env
# Twitch API設定
TWITCH_CLIENT_ID=your_twitch_client_id
TWITCH_CLIENT_SECRET=your_twitch_client_secret
TWITCH_CHANNEL_NAME=your_channel_name
TWITCH_CHANNEL_URL=https://www.twitch.tv/your_channel_name

# アップロード設定
DOWNLOAD_DIR=./downloads
MAX_VIDEO_LENGTH=43200  # 12時間（YouTubeの制限）
```

## 使用方法

### 設定確認
```bash
# 設定確認スクリプト（推奨）
./check_config.sh

# または直接実行
python check_config.py
```

### 前日の動画をアップロード
```bash
# 直接実行
python main.py

# またはシェルスクリプト経由（推奨）
bash run_upload.sh
```

### 手動で指定した日数前の動画をアップロード
```bash
python main.py --manual 2  # 2日前の動画
```

### スケジュール実行（cron使用）
```bash
# crontabを編集
crontab -e

# 毎日午前9時に実行する設定例
0 9 * * * /path/to/twitch-vods-to-youtube/run_upload.sh
```

詳細な設定方法は `cron_setup.md` を参照してください。

## ファイル構成

```
twitch-vods-to-youtube/
├── main.py              # メインスクリプト
├── config.py            # 設定管理
├── twitch_api.py        # Twitch API処理
├── youtube_api.py       # YouTube API処理
├── video_downloader.py  # 動画ダウンロード処理
├── upload_manager.py    # アップロード管理
├── run_upload.sh        # cron実行用シェルスクリプト
├── check_config.sh      # 設定確認用シェルスクリプト
├── cron_setup.md        # cron設定ガイド
├── check_config.py      # 設定確認ツール
├── .env.example         # .envファイルのテンプレート
├── requirements.txt     # 依存関係
├── README.md           # このファイル
├── .env                # API設定ファイル（要作成）
├── client_secret.json # YouTube API認証ファイル（要配置）
├── downloads/          # ダウンロードディレクトリ（自動作成）
└── logs/               # 実行ログディレクトリ（自動作成）
```

## 設定項目

| 項目 | 説明 | デフォルト値 |
|------|------|-------------|
| `TWITCH_CLIENT_ID` | Twitch API Client ID | - |
| `TWITCH_CLIENT_SECRET` | Twitch API Client Secret | - |
| `TWITCH_CHANNEL_NAME` | 対象チャンネル名 | - |
| `TWITCH_CHANNEL_URL` | TwitchチャンネルURL（動画説明に含まれる） | `https://www.twitch.tv/{TWITCH_CHANNEL_NAME}` |
| `DOWNLOAD_DIR` | ダウンロードディレクトリ | `./downloads` |
| `MAX_VIDEO_LENGTH` | 最大動画長（秒） | `43200`（12時間） |



## YouTubeの制限について

### 動画の長さ制限
- **認証済みアカウント**: 最大12時間（43,200秒）
- **未認証アカウント**: 最大15分（900秒）

### ファイルサイズ制限
- **一般的なアカウント**: 128GB
- **認証済みアカウント**: 256GB

### 推奨設定
- 認証済みアカウントの場合: `MAX_VIDEO_LENGTH=43200`（12時間）
- 未認証アカウントの場合: `MAX_VIDEO_LENGTH=900`（15分）
- 動画分割が必要な場合: `ENABLE_VIDEO_SPLIT=true`

## 注意事項

- 初回実行時にYouTube APIの認証が必要です
- 認証時に複数のチャンネルがある場合は、正しいチャンネルを選択してください
- 動画の長さが`MAX_VIDEO_LENGTH`を超える場合はスキップされます
- アップロード成功後、ローカルファイルは自動的に削除されます
- 古いファイルは7日後に自動的に削除されます
- cronで実行する場合は、絶対パスを使用してください
- 実行ログは`logs/`ディレクトリに保存されます
- 同じファイル名の動画が既に存在する場合はダウンロードをスキップします

## APIキーの有効期限について

### Twitch API
- **アクセストークン**: 24時間で期限切れ
- **自動更新**: 期限切れ時に自動的に再取得
- **Client ID/Secret**: 永続的（変更時は手動更新が必要）

### YouTube API
- **アクセストークン**: 1時間で期限切れ
- **リフレッシュトークン**: 永続的（手動で無効化するまで有効）
- **自動更新**: 期限切れ時に自動的に更新
- **認証エラー**: 自動的に再認証を試行

### 推奨事項
- 定期的にログを確認してAPIエラーがないかチェック
- 長期間運用する場合は、APIキーの有効期限を定期的に確認
- 認証エラーが頻発する場合は、手動で再認証を実行

## トラブルシューティング



### Twitch API認証エラー
1. `.env`ファイルにClient IDとClient Secretが正しく設定されているか確認
2. Twitch Developer Consoleでアプリケーションが正しく設定されているか確認

### .envファイルエラー
1. `.env`ファイルが存在するか確認
2. `.env.example`を参考に`.env`ファイルを作成
3. すべての必要な設定値が入力されているか確認
4. `./check_config.sh`で詳細な設定確認を実行

### 動画ダウンロードエラー
1. yt-dlpが正しくインストールされているか確認
2. インターネット接続を確認
3. 同じファイル名の動画が既に存在する場合はスキップされます

### YouTube認証エラー
1. `client_secret.json`ファイルが正しく配置されているか確認
2. 初回実行時にブラウザで認証を完了する
3. 複数のチャンネルがある場合は、正しいチャンネルを選択する
4. 認証エラーが続く場合は、`token.pickle`を削除して再認証する

## ライセンス

MIT License
