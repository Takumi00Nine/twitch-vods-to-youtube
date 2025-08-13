import requests
import re
from config import Config


class TwitchAPI:
    def __init__(self):
        self.client_id = Config.TWITCH_CLIENT_ID
        self.client_secret = Config.TWITCH_CLIENT_SECRET
        self.channel_name = Config.TWITCH_CHANNEL_NAME
        self.access_token = None
        self.base_url = "https://api.twitch.tv/helix"

    def get_access_token(self):
        """Twitch APIのアクセストークンを取得"""
        url = "https://id.twitch.tv/oauth2/token"
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }

        try:
            response = requests.post(url, data=data, timeout=30)
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                print("Twitch APIアクセストークンを取得しました")
                return True
            else:
                print(f"アクセストークンの取得に失敗: {response.status_code}")
                print(f"エラー詳細: {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Twitch API接続エラー: {str(e)}")
            return False

    def get_channel_id(self):
        """チャンネル名からチャンネルIDを取得"""
        if not self.access_token:
            if not self.get_access_token():
                return None

        headers = {
            'Client-ID': self.client_id,
            'Authorization': f'Bearer {self.access_token}'
        }

        url = f"{self.base_url}/users"
        params = {'login': self.channel_name}

        try:
            response = requests.get(
                url, headers=headers, params=params, timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                if data['data']:
                    return data['data'][0]['id']
                else:
                    print(f"チャンネル '{self.channel_name}' が見つかりません")
            elif response.status_code == 401:
                print(
                    "Twitch API認証エラー: トークンが無効です。再取得を試行します。"
                )
                self.access_token = None
                if self.get_access_token():
                    return self.get_channel_id()  # 再帰的に再試行
            else:
                print(f"チャンネルID取得エラー: {response.status_code}")
                print(f"エラー詳細: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Twitch API接続エラー: {str(e)}")

        return None

    def get_videos(self, days_back=1):
        """指定した日数前の配信アーカイブを取得"""
        if not self.access_token:
            if not self.get_access_token():
                return []

        channel_id = self.get_channel_id()
        if not channel_id:
            print(f"チャンネル '{self.channel_name}' が見つかりません")
            return []

        headers = {
            'Client-ID': self.client_id,
            'Authorization': f'Bearer {self.access_token}'
        }

        url = f"{self.base_url}/videos"
        params = {
            'user_id': channel_id,
            'type': 'archive',
            'first': 100  # Twitch APIの最大値
        }

        try:
            response = requests.get(
                url, headers=headers, params=params, timeout=30
            )
            if response.status_code == 200:
                videos = response.json()['data']
                return videos
            elif response.status_code == 401:
                print(
                    "Twitch API認証エラー: トークンが無効です。再取得を試行します。"
                )
                self.access_token = None
                if self.get_access_token():
                    return self.get_videos(days_back)  # 再帰的に再試行
            else:
                print(f"動画の取得に失敗: {response.status_code}")
                print(f"エラー詳細: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Twitch API接続エラー: {str(e)}")

        return []

    def parse_twitch_duration(self, duration_str):
        """Twitchのduration文字列（例: '2h21m23s'）を秒に変換"""
        pattern = r'((?P<hours>\d+)h)?((?P<minutes>\d+)m)?((?P<seconds>\d+)s)?'
        match = re.match(pattern, duration_str)
        if not match:
            return 0
        hours = int(match.group('hours') or 0)
        minutes = int(match.group('minutes') or 0)
        seconds = int(match.group('seconds') or 0)
        return hours * 3600 + minutes * 60 + seconds

    def get_video_url(self, video_id):
        """動画のダウンロードURLを取得"""
        if not self.access_token:
            if not self.get_access_token():
                return None

        headers = {
            'Client-ID': self.client_id,
            'Authorization': f'Bearer {self.access_token}'
        }

        url = f"{self.base_url}/videos"
        params = {'id': video_id}

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if data['data']:
                return data['data'][0]['url']

        return None
