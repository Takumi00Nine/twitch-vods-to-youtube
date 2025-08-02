import os
from datetime import datetime, timedelta
import pytz
from twitch_api import TwitchAPI
from youtube_api import YouTubeAPI
from video_downloader import VideoDownloader
from config import Config
import re


def parse_twitch_duration(duration_str):
    """Twitchのduration文字列（例: '2h21m23s'）を秒に変換"""
    pattern = r'((?P<hours>\d+)h)?((?P<minutes>\d+)m)?((?P<seconds>\d+)s)?'
    match = re.match(pattern, duration_str)
    if not match:
        return 0
    hours = int(match.group('hours') or 0)
    minutes = int(match.group('minutes') or 0)
    seconds = int(match.group('seconds') or 0)
    return hours * 3600 + minutes * 60 + seconds


class UploadManager:
    def __init__(self):
        self.twitch_api = TwitchAPI()
        self.youtube_api = YouTubeAPI()
        self.downloader = VideoDownloader()

    def process_yesterday_videos(self):
        """前日の配信アーカイブを処理"""
        jst = pytz.timezone('Asia/Tokyo')
        now_jst = datetime.now(jst)
        yesterday_jst = now_jst - timedelta(days=1)
        print(
            f"前日（{yesterday_jst.strftime('%Y年%m月%d日')}）"
            "の配信アーカイブを取得中..."
        )

        # 前日の動画を取得
        videos = self.twitch_api.get_videos(days_back=4)

        if not videos:
            print(
                f"前日（{yesterday_jst.strftime('%Y年%m月%d日')}）"
                "の配信アーカイブが見つかりませんでした。"
            )
            return

        print(
            f"前日（{yesterday_jst.strftime('%Y年%m月%d日')}）"
            f"の配信アーカイブ {len(videos)} 件を発見"
        )

        for video in videos:
            try:
                self.process_single_video(video)
            except Exception as e:
                print(f"動画処理エラー: {str(e)}")
                continue

    def process_single_video(self, video):
        """単一の動画を処理"""
        video_id = video['id']
        title = video['title']
        duration = parse_twitch_duration(video['duration'])

        # Twitch APIから返される時間はUTCなので、日本時間に変換
        jst = pytz.timezone('Asia/Tokyo')
        created_at_utc = datetime.fromisoformat(
            video['created_at'].replace('Z', '+00:00')
        )
        created_at_jst = created_at_utc.astimezone(jst)

        print(f"\n動画を処理中: {title}")
        print(f"動画ID: {video_id}")
        print(f"長さ: {self.downloader.format_duration(duration)}")
        print(f"作成日時（JST）: {created_at_jst}")

        # 動画が長すぎる場合の処理
        if duration > self.downloader.max_video_length:
            print(
                f"動画が長すぎます（{self.downloader.format_duration(duration)}）。"
                "スキップします。"
            )
            return

        # 動画URLを取得
        video_url = self.twitch_api.get_video_url(video_id)
        if not video_url:
            print("動画URLの取得に失敗しました。")
            return

        # ファイル名を生成（日本時間の日付を使用）
        date_str = created_at_jst.strftime("%Y%m%d")
        safe_title = "".join(
            c for c in title if c.isalnum() or c in (' ', '-', '_')
        ).rstrip()
        filename = f"{date_str}_{safe_title[:50]}.mp4"

        # 動画をダウンロード
        file_path = self.downloader.download_video(video_url, filename)
        if not file_path:
            print("動画のダウンロードに失敗しました。")
            return

        # 動画の長さを確認
        actual_duration = self.downloader.get_video_duration(file_path)
        if actual_duration and actual_duration > self.downloader.max_video_length:
            print(
                f"ダウンロードした動画が長すぎます"
                f"（{self.downloader.format_duration(actual_duration)}）。"
                "削除します。"
            )
            os.remove(file_path)
            return

        # YouTubeにアップロード
        self._upload_single_video(file_path, title, date_str, created_at_jst)

    def _upload_single_video(self, file_path, title, date_str, created_at_jst):
        """単一の動画をYouTubeにアップロード"""
        # TwitchチャンネルURLを含む説明文を作成
        twitch_url = Config.TWITCH_CHANNEL_URL
        author_name = Config.AUTHOR_NAME
        date_str = created_at_jst.strftime('%Y年%m月%d日')
        description = (
            f"Twitch配信アーカイブ\n\n配信日（JST）: {date_str}\n\n"
            f"Twitchチャンネル: {twitch_url}\n\n#Twitch #配信アーカイブ"
        )

        # タグに作者名を追加
        tags = ['Twitch', '配信アーカイブ', 'ライブ配信']
        if author_name:
            tags.append(author_name)

        video_id = self.youtube_api.upload_video(
            file_path=file_path,
            title=title,
            description=description,
            tags=tags
        )

        if video_id:
            print(f"YouTubeアップロード成功: {video_id}")

            # アップロード成功後、ローカルファイルを削除
            os.remove(file_path)
            print(f"ローカルファイルを削除: {file_path}")
        else:
            print("YouTubeアップロードに失敗しました。")

    def run_manual_upload(self, days_back=1):
        """手動でアップロード処理を実行"""
        jst = pytz.timezone('Asia/Tokyo')
        now_jst = datetime.now(jst)
        target_date = now_jst - timedelta(days=days_back)
        print(
            f"手動アップロード処理を開始: {days_back}日前"
            f"（{target_date.strftime('%Y年%m月%d日')}）の動画"
        )

        # 指定した日数前の動画を取得
        videos = self.twitch_api.get_videos(days_back=days_back)

        if not videos:
            print(f"{days_back}日前の配信アーカイブが見つかりませんでした。")
            return

        print(f"{days_back}日前の配信アーカイブ {len(videos)} 件を発見")
        print("処理対象の動画一覧:")
        for i, video in enumerate(videos, 1):
            created_at_utc = datetime.fromisoformat(
                video['created_at'].replace('Z', '+00:00')
            )
            created_at_jst = created_at_utc.astimezone(jst)
            print(
                f"  {i}. {video['title']} - "
                f"{created_at_jst.strftime('%Y年%m月%d日 %H:%M:%S')}"
            )

        for i, video in enumerate(videos, 1):
            print(f"\n=== {i}件目の動画を処理中 ===")
            try:
                self.process_single_video(video)
            except Exception as e:
                print(f"動画処理エラー: {str(e)}")
                continue
