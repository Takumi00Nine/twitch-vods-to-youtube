import os
from dotenv import load_dotenv

# .envファイルを読み込み
env_loaded = load_dotenv()

class Config:
    def __init__(self):
        if not env_loaded:
            print("警告: .envファイルが見つかりません。")
            print(".env.exampleを参考に.envファイルを作成してください。")
    
    # Twitch API設定
    TWITCH_CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
    TWITCH_CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET')
    TWITCH_CHANNEL_NAME = os.getenv('TWITCH_CHANNEL_NAME')
    TWITCH_CHANNEL_URL = os.getenv('TWITCH_CHANNEL_URL', f'https://www.twitch.tv/{os.getenv("TWITCH_CHANNEL_NAME", "")}')
    
    # 作者設定
    AUTHOR_NAME = os.getenv('AUTHOR_NAME')
    
    # アップロード設定
    DOWNLOAD_DIR = os.getenv('DOWNLOAD_DIR', './downloads')
    MAX_VIDEO_LENGTH = int(os.getenv('MAX_VIDEO_LENGTH', 43200))  # 最大動画長（秒）- 12時間
    
    @classmethod
    def validate_config(cls):
        """設定の妥当性をチェック"""
        missing_configs = []
        
        if not cls.TWITCH_CLIENT_ID:
            missing_configs.append('TWITCH_CLIENT_ID')
        if not cls.TWITCH_CLIENT_SECRET:
            missing_configs.append('TWITCH_CLIENT_SECRET')
        if not cls.TWITCH_CHANNEL_NAME:
            missing_configs.append('TWITCH_CHANNEL_NAME')

        
        return missing_configs 