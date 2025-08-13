import os
from dotenv import load_dotenv

# .envファイルを読み込み（envフォルダから）
env_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'env', '.env'
)
env_loaded = load_dotenv(env_path)


class Config:
    def __init__(self):
        if not env_loaded:
            print("警告: .envファイルが見つかりません。")
            print(".env.exampleを参考に.envファイルを作成してください。")

    # Twitch API設定
    TWITCH_CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
    TWITCH_CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET')
    TWITCH_CHANNEL_NAME = os.getenv('TWITCH_CHANNEL_NAME')
    TWITCH_CHANNEL_URL = os.getenv(
        'TWITCH_CHANNEL_URL',
        f'https://www.twitch.tv/{TWITCH_CHANNEL_NAME}'
    )

    # 作者設定
    AUTHOR_NAME = os.getenv('AUTHOR_NAME')

    # アップロード設定
    # プロジェクトルートのdownloadsフォルダを絶対パスで指定
    project_root = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
    DOWNLOAD_DIR = os.getenv(
        'DOWNLOAD_DIR', os.path.join(project_root, 'downloads')
    )
    MAX_VIDEO_LENGTH = int(os.getenv('MAX_VIDEO_LENGTH', 43200))

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
