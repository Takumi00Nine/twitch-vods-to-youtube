import requests
import json
from datetime import datetime, timedelta
import pytz
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
            response = requests.get(url, headers=headers, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data['data']:
                    return data['data'][0]['id']
                else:
                    print(f"チャンネル '{self.channel_name}' が見つかりません")
            elif response.status_code == 401:
                print("Twitch API認証エラー: トークンが無効です。再取得を試行します。")
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
        
        # 日本時間の前日の日付を計算
        jst = pytz.timezone('Asia/Tokyo')
        now_jst = datetime.now(jst)
        yesterday_jst = now_jst - timedelta(days=days_back)
        start_date = yesterday_jst.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = yesterday_jst.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        url = f"{self.base_url}/videos"
        params = {
            'user_id': channel_id,
            'type': 'archive',
            'first': 100
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            if response.status_code == 200:
                videos = response.json()['data']
                
                # 前日の動画のみをフィルタリング（日本時間で比較）
                filtered_videos = []
                for video in videos:
                    # Twitch APIから返される時間はUTCなので、日本時間に変換
                    created_at_utc = datetime.fromisoformat(video['created_at'].replace('Z', '+00:00'))
                    created_at_jst = created_at_utc.astimezone(jst)
                    if start_date <= created_at_jst <= end_date:
                        filtered_videos.append(video)
                return filtered_videos
            elif response.status_code == 401:
                print("Twitch API認証エラー: トークンが無効です。再取得を試行します。")
                self.access_token = None
                if self.get_access_token():
                    return self.get_videos(days_back)  # 再帰的に再試行
            else:
                print(f"動画の取得に失敗: {response.status_code}")
                print(f"エラー詳細: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Twitch API接続エラー: {str(e)}")
        
        return []
    
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