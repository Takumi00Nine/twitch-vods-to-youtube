import os
from datetime import datetime
import pytz
from twitch_api import TwitchAPI
from youtube_api import YouTubeAPI
from video_downloader import VideoDownloader
from config import Config


class UploadManager:
    def __init__(self):
        self.twitch_api = TwitchAPI()
        self.youtube_api = YouTubeAPI()
        self.downloader = VideoDownloader()

    def process_single_video(self, video):
        """単一の動画を処理"""
        video_id = video['id']
        title = video['title']
        duration = self.twitch_api.parse_twitch_duration(video['duration'])

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

    def _get_videos_in_date_range(self, start_date, end_date):
        """指定した日時範囲の動画を取得"""
        jst = pytz.timezone('Asia/Tokyo')
        
        # すべての動画を取得してソート
        all_raw_videos = []
        for days_back in range(1, 31):  # 最大30日間
            videos = self.twitch_api.get_videos(days_back=days_back)
            if videos:
                for video in videos:
                    # 重複チェック
                    if not any(v['id'] == video['id'] for v in all_raw_videos):
                        all_raw_videos.append(video)
        
        # 作成日時でソート（新しい順）
        all_raw_videos.sort(key=lambda x: x['created_at'], reverse=True)
        
        # 指定された日付範囲内の動画のみを抽出
        all_videos = []
        for video in all_raw_videos:
            created_at_utc = datetime.fromisoformat(
                video['created_at'].replace('Z', '+00:00')
            )
            created_at_jst = created_at_utc.astimezone(jst)
            
            # 指定された日付範囲内の動画のみを追加
            if start_date <= created_at_jst <= end_date:
                all_videos.append(video)
            elif created_at_jst < start_date:
                # 開始日より古い動画に到達したら終了
                break
        
        return all_videos

    def run_manual_upload(self, start_datetime, end_datetime):
        """指定した日時範囲の動画をアップロード処理を実行"""
        print(
            f"手動アップロード処理を開始: "
            f"{start_datetime.strftime('%Y年%m月%d日 %H:%M:%S')} から "
            f"{end_datetime.strftime('%Y年%m月%d日 %H:%M:%S')} "
            "までの動画"
        )

        # 指定した日時範囲の動画を取得
        videos = self._get_videos_in_date_range(start_datetime, end_datetime)

        if not videos:
            print(
                f"指定した期間（{start_datetime.strftime('%Y年%m月%d日 %H:%M:%S')} から "
                f"{end_datetime.strftime('%Y年%m月%d日 %H:%M:%S')}）の配信アーカイブが"
                "見つかりませんでした。"
            )
            return

        print(
            f"指定した期間の配信アーカイブ {len(videos)} 件を発見"
        )
        print("処理対象の動画一覧:")
        for i, video in enumerate(videos, 1):
            created_at_utc = datetime.fromisoformat(
                video['created_at'].replace('Z', '+00:00')
            )
            created_at_jst = created_at_utc.astimezone(pytz.timezone('Asia/Tokyo'))
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
