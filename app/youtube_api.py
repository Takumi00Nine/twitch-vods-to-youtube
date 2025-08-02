import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


class YouTubeAPI:
    def __init__(self):
        self.credentials = None
        self.youtube = None

        # OAuth 2.0のスコープ（Brand Account対応のため追加）
        self.SCOPES = [
            'https://www.googleapis.com/auth/youtube.upload',
            'https://www.googleapis.com/auth/youtube.readonly',
            'https://www.googleapis.com/auth/youtube.force-ssl'
        ]

    def authenticate(self):
        """YouTube APIの認証を行う"""
        creds = None

        # トークンファイルが存在する場合は読み込み
        token_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 'pickle', 'token.pickle'
        )
        if os.path.exists(token_path):
            try:
                with open(token_path, 'rb') as token:
                    creds = pickle.load(token)
            except Exception as e:
                print(f"トークンファイルの読み込みエラー: {str(e)}")
                # 破損したトークンファイルを削除
                os.remove(token_path)
                creds = None

        # 有効な認証情報がない場合、または期限切れの場合
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    print("YouTube APIトークンを更新中...")
                    creds.refresh(Request())
                    print("YouTube APIトークンを更新しました")
                except Exception as e:
                    print(f"YouTube APIトークン更新エラー: {str(e)}")
                    creds = None
            else:
                # client_secret.jsonファイルが必要
                client_secret_path = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)), 'config',
                    'client_secret.json'
                )
                if not os.path.exists(client_secret_path):
                    print("config/client_secret.jsonファイルが見つかりません。")
                    print(
                        "Google Cloud Consoleからダウンロードして"
                        "config/フォルダに配置してください。"
                    )
                    return False

                try:
                    print("YouTube API認証を開始します...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        client_secret_path, self.SCOPES
                    )

                    # チャネルIDが指定されている場合は、認証時に明示的に指定

                    creds = flow.run_local_server(port=8080)
                    print("YouTube API認証が完了しました")
                except Exception as e:
                    print(f"YouTube API認証エラー: {str(e)}")
                    return False

            # 認証情報を保存
            try:
                # pickleディレクトリが存在しない場合は作成
                pickle_dir = os.path.dirname(token_path)
                os.makedirs(pickle_dir, exist_ok=True)

                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
            except Exception as e:
                print(f"トークンファイル保存エラー: {str(e)}")

        self.credentials = creds
        self.youtube = build('youtube', 'v3', credentials=creds)

        return True

    def upload_video(self, file_path, title, description="", tags=None,
                     category_id="22"):
        """動画をYouTubeにアップロード"""
        if not self.youtube:
            if not self.authenticate():
                return None

        try:
            # 動画ファイルのアップロード
            media = MediaFileUpload(file_path, resumable=True)

            # 動画のメタデータ
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags or [],
                    'categoryId': category_id
                },
                'status': {
                    'privacyStatus': 'private',  # 最初は非公開でアップロード
                    'selfDeclaredMadeForKids': False
                }
            }

            # アップロード実行
            request = self.youtube.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=media
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"アップロード進捗: {int(status.progress() * 100)}%")

            video_id = response['id']
            print(f"アップロード完了: {video_id}")

            return video_id

        except Exception as e:
            error_msg = str(e)
            print(f"アップロードエラー: {error_msg}")

            # 認証エラーの場合は再認証を試行
            if ("unauthorized" in error_msg.lower() or
                    "invalid credentials" in error_msg.lower()):
                print("認証エラーが発生しました。再認証を試行します。")
                self.credentials = None
                self.youtube = None
                if self.authenticate():
                    return self.upload_video(
                        file_path, title, description, tags, category_id
                    )

            return None

    def update_video_privacy(self, video_id, privacy_status='public'):
        """動画のプライバシー設定を更新"""
        if not self.youtube:
            if not self.authenticate():
                return False

        try:
            self.youtube.videos().update(
                part='status',
                body={
                    'id': video_id,
                    'status': {
                        'privacyStatus': privacy_status
                    }
                }
            ).execute()

            print(f"プライバシー設定を更新: {video_id} -> {privacy_status}")
            return True

        except Exception as e:
            print(f"プライバシー設定更新エラー: {str(e)}")
            return False
