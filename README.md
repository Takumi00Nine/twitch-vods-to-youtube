# Twitch配信アーカイブ YouTube自動アップロード

Twitch APIを使用して前日分の配信アーカイブを自動的にYouTubeにアップロードするPythonスクリプトです。

## 機能

- **自動配信アーカイブ取得**: Twitch APIを使用して前日の配信アーカイブを自動取得
- **日本時間対応**: 日本標準時（JST）に基づいて前日の動画を判定
- **動画長制限**: YouTubeの制限（12時間）を超える動画は自動スキップ
- **重複ダウンロード防止**: 既にダウンロード済みの動画は再ダウンロードしない
- **自動アップロード**: YouTube Data API v3を使用して自動アップロード
- **トークン自動更新**: YouTube APIのトークンは自動的に更新される
- **ログ出力**: 詳細な処理ログを出力
- **設定確認ツール**: `check_config.sh`でAPI設定を確認可能
- **作者名タグ**: 設定した作者名を動画タグに自動追加

## 必要な環境

- Python 3.7以上

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 仮想環境の作成（推奨）

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate     # Windows
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
5. **client_secret.json**をダウンロードして`config`フォルダに配置

### 4. .envファイルの設定

`env/.env.sample`を参考に`env/.env`ファイルを作成してください：

```bash
# テンプレートをコピー
cp env/.env.sample env/.env

# env/.envファイルを編集
nano env/.env
```

`env/.env`ファイルの内容例：

```env
# Twitch API設定
TWITCH_CLIENT_ID=your_twitch_client_id
TWITCH_CLIENT_SECRET=your_twitch_client_secret
TWITCH_CHANNEL_NAME=your_channel_name
TWITCH_CHANNEL_URL=https://www.twitch.tv/your_channel_name

# 作者設定
AUTHOR_NAME=your_author_name

# アップロード設定
DOWNLOAD_DIR=./downloads
MAX_VIDEO_LENGTH=43200  # 12時間（YouTubeの制限）
```

## 使用方法

### 設定確認
```bash
# 設定確認スクリプト
bash sh/check_config.sh
```

### 前日の動画をアップロード
```bash
# シェルスクリプト経由
bash sh/run_upload.sh
```

### 手動で指定した日数前の動画をアップロード
```bash
# シェルスクリプト経由で手動実行
bash sh/run_upload.sh --manual 2  # 2日前の動画
```

### スケジュール実行（cron使用）
```bash
# crontabを編集
crontab -e

# 毎日午前9時に実行する設定例
0 9 * * * /path/to/twitch-vods-to-youtube/sh/run_upload.sh
```

## ファイル構成

```
twitch-vods-to-youtube/
├── app/                 # Pythonアプリケーションディレクトリ
│   ├── main.py          # メインスクリプト
│   ├── config.py        # 設定管理
│   ├── twitch_api.py    # Twitch API処理
│   ├── youtube_api.py   # YouTube API処理
│   ├── video_downloader.py # 動画ダウンロード処理
│   ├── upload_manager.py # アップロード管理
│   └── check_config.py  # 設定確認ツール
├── sh/                  # シェルスクリプトディレクトリ
│   ├── run_upload.sh    # cron実行用シェルスクリプト
│   └── check_config.sh  # 設定確認用シェルスクリプト
├── env/                 # 環境設定ディレクトリ
│   ├── .env.sample     # .envファイルのテンプレート
│   └── .env            # API設定ファイル（要作成）
├── requirements.txt     # 依存関係
├── README.md           # このファイル

├── config/            # 設定ファイルディレクトリ
│   └── client_secret.json # YouTube API認証ファイル（要作成）
├── pickle/            # 認証トークンディレクトリ
│   └── token.pickle  # YouTube API認証トークン（自動作成）
├── downloads/          # ダウンロードディレクトリ
└── logs/               # 実行ログディレクトリ
```

## 設定項目

| 項目 | 説明 | デフォルト値 |
|------|------|-------------|
| `TWITCH_CLIENT_ID` | Twitch API Client ID | - |
| `TWITCH_CLIENT_SECRET` | Twitch API Client Secret | - |
| `TWITCH_CHANNEL_NAME` | 対象チャンネル名 | - |
| `TWITCH_CHANNEL_URL` | TwitchチャンネルURL（動画説明に含まれる） | `https://www.twitch.tv/{TWITCH_CHANNEL_NAME}` |
| `AUTHOR_NAME` | 作者名（動画タグに含まれる） | - |
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

## 注意事項

- 初回実行時にYouTube APIの認証が必要です
- 認証時に複数のチャンネルがある場合は、アップロード先のチャンネルを選択してください
- 動画の長さが`MAX_VIDEO_LENGTH`を超える場合はスキップされます
- アップロード成功後、ローカルファイルは自動的に削除されます
- 古いファイルは7日後に自動的に削除されます
- cronで実行する場合は、絶対パスを使用してください
- 実行ログは`logs/`ディレクトリに保存されます
- 同じファイル名の動画が既に存在する場合はダウンロードをスキップします
- 設定した作者名が動画タグに自動的に追加されます

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
3. 複数のチャンネルがある場合は、アップロード先のチャンネルを選択する
4. 認証エラーが続く場合は、`token.pickle`を削除して再認証する

## 免責事項

**重要**: このコードはAI生成で作成されています。何かしら問題が発生した場合でも、作者は責任を負いかねます。

- このソフトウェアは「現状のまま」提供され、明示的または暗黙的な保証は一切ありません
- 作者は、このソフトウェアの使用または使用不能によって生じるいかなる損害についても責任を負いません
- このソフトウェアを使用する前に、必ずバックアップを取得し、テスト環境で十分に検証してください
- 本ソフトウェアの使用は、ユーザーの自己責任で行ってください

## ライセンス

MIT License