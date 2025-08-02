import os
from datetime import datetime
import yt_dlp
from config import Config


class VideoDownloader:
    def __init__(self):
        self.download_dir = Config.DOWNLOAD_DIR
        self.max_video_length = Config.MAX_VIDEO_LENGTH

        # ダウンロードディレクトリが存在しない場合のみ作成
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir, exist_ok=True)
            print(f"ダウンロードディレクトリを作成しました: {self.download_dir}")
        else:
            print(f"既存のダウンロードディレクトリを使用します: {self.download_dir}")

    def download_video(self, url, filename):
        """動画をダウンロード"""
        try:
            # yt-dlpを使用して動画をダウンロード
            output_path = os.path.join(self.download_dir, filename)

            # ファイルが既に存在する場合はスキップ
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                # ファイルサイズが1MB以上ある場合はスキップ（不完全なダウンロードを除外）
                if file_size > 1024 * 1024:
                    print(
                        f"ファイルが既に存在します。スキップします: {filename} "
                        f"({file_size / (1024*1024):.1f}MB)"
                    )
                    return output_path
                else:
                    print(f"不完全なファイルを削除します: {filename}")
                    os.remove(output_path)

            ydl_opts = {
                'outtmpl': output_path,
                'format': 'best',
                'noplaylist': True,
            }

            print(f"動画をダウンロード中: {filename}")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            # ファイルが実際にダウンロードされたかチェック
            if os.path.exists(output_path):
                print(f"ダウンロード完了: {output_path}")
                return output_path
            else:
                print("ダウンロードされたファイルが見つかりません")
                return None

        except Exception as e:
            print(f"ダウンロードエラー: {str(e)}")
            return None

    def get_video_duration(self, file_path):
        """動画の長さを取得（秒）"""
        try:
            # ファイルが存在するかチェック
            if not os.path.exists(file_path):
                print(f"ファイルが存在しません: {file_path}")
                return None

            # 方法1: ffprobeを使用
            try:
                import subprocess

                cmd = [
                    'ffprobe',
                    '-v', 'quiet',
                    '-show_entries', 'format=duration',
                    '-of', 'csv=p=0',
                    file_path
                ]

                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    duration = float(result.stdout.strip())
                    return duration
            except Exception as ffprobe_error:
                print(f"ffprobeエラー: {ffprobe_error}")

            # 方法2: yt-dlpを使用（file://プロトコル）
            try:
                import urllib.parse

                # ファイルパスをURLエンコード
                abs_path = os.path.abspath(file_path)
                encoded_path = urllib.parse.quote(abs_path)
                file_url = f"file://{encoded_path}"

                ydl_opts = {
                    'quiet': True,
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(file_url, download=False)
                    duration = info.get('duration')
                    if duration:
                        return float(duration)
            except Exception as ytdlp_error:
                print(f"yt-dlpエラー: {ytdlp_error}")

            # 方法3: yt-dlpコマンドラインを使用
            try:

                cmd = [
                    'yt-dlp',
                    '--print', 'duration',
                    '--no-playlist',
                    file_path
                ]

                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    duration_str = result.stdout.strip()
                    if duration_str and duration_str != 'NA':
                        return float(duration_str)
            except Exception as ytdlp_cmd_error:
                print(f"yt-dlpコマンドエラー: {ytdlp_cmd_error}")

            print("動画の長さ情報を取得できませんでした")
            return None

        except Exception as e:
            print(f"動画長の取得エラー: {str(e)}")
            return None

    def cleanup_old_files(self, max_age_days=7):
        """古いファイルを削除"""
        try:
            current_time = datetime.now()
            for filename in os.listdir(self.download_dir):
                file_path = os.path.join(self.download_dir, filename)
                if os.path.isfile(file_path):
                    file_age = current_time - datetime.fromtimestamp(
                        os.path.getctime(file_path)
                    )
                    if file_age.days > max_age_days:
                        os.remove(file_path)
                        print(f"古いファイルを削除: {filename}")

        except Exception as e:
            print(f"ファイルクリーンアップエラー: {str(e)}")

    def format_duration(self, seconds):
        """秒数を時:分:秒形式に変換"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
