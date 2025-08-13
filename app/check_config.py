#!/usr/bin/env python3
"""
Twitch設定とYouTube設定を確認するツール
"""

import os
import sys
import argparse
from datetime import datetime
import pytz

from config import Config
from twitch_api import TwitchAPI
from youtube_api import YouTubeAPI


def parse_datetime_arg(datetime_str):
    """日時文字列をdatetimeオブジェクトに変換"""
    try:
        # YYYY/MM/DD HH:MM:SS 形式
        if '/' in datetime_str and ':' in datetime_str:
            return datetime.strptime(datetime_str, '%Y/%m/%d %H:%M:%S')
        # YYYY/MM/DD 形式
        elif '/' in datetime_str and ':' not in datetime_str:
            return datetime.strptime(datetime_str, '%Y/%m/%d')
        else:
            raise ValueError(f"無効な日時形式: {datetime_str}")
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"日時形式エラー: {e}")


def check_twitch_config(start_datetime=None, end_datetime=None):
    """Twitch設定を確認"""

    print("=== Twitch設定確認 ===")

    # 基本設定の確認
    print(
        f"Client ID: "
        f"{'✅ 設定済み' if Config.TWITCH_CLIENT_ID else '❌ 未設定'}"
    )
    print(
        f"Client Secret: "
        f"{'✅ 設定済み' if Config.TWITCH_CLIENT_SECRET else '❌ 未設定'}"
    )
    print(
        f"Channel Name: {'✅ 設定済み' if Config.TWITCH_CHANNEL_NAME else '❌ 未設定'}"
    )

    if not all([
        Config.TWITCH_CLIENT_ID,
        Config.TWITCH_CLIENT_SECRET,
        Config.TWITCH_CHANNEL_NAME
    ]):
        print("\n❌ Twitch設定が不完全です")
        return False

    # API接続テスト
    print("\n--- API接続テスト ---")
    try:
        twitch_api = TwitchAPI()

        # アクセストークン取得テスト
        print("アクセストークン取得中...")
        if twitch_api.get_access_token():
            print("✅ アクセストークン取得成功")
        else:
            print("❌ アクセストークン取得失敗")
            return False

        # チャンネルID取得テスト
        print("チャンネルID取得中...")
        channel_id = twitch_api.get_channel_id()
        if channel_id:
            print(f"✅ チャンネルID取得成功: {channel_id}")
        else:
            print("❌ チャンネルID取得失敗")
            print("考えられる原因:")
            print("- チャンネル名が間違っている")
            print("- チャンネルが存在しない")
            print("- API権限が不足している")
            return False

        # 動画取得テスト（過去7日間の範囲で）
        print("動画取得テスト中...")
        videos = twitch_api.get_videos(days_back=3)  # 前日分をテスト
        if videos is not None:
            print(f"✅ 動画取得成功: {len(videos)}件の動画を発見")

            # 指定された日付範囲またはデフォルトで動画を取得
            all_videos = []
            if start_datetime and end_datetime:
                # 指定された日付範囲で動画を取得
                jst = pytz.timezone('Asia/Tokyo')
                start_jst = jst.localize(start_datetime)
                end_jst = jst.localize(end_datetime)

                print(f"検索期間: {start_jst.strftime('%Y年%m月%d日 %H:%M:%S')} から {end_jst.strftime('%Y年%m月%d日 %H:%M:%S')}")

                # すべての動画を取得してソート
                all_raw_videos = []
                for days_back in range(1, 31):  # 最大30日間
                    videos = twitch_api.get_videos(days_back=days_back)
                    if videos:
                        for video in videos:
                            # 重複チェック
                            if not any(v['id'] == video['id'] for v in all_raw_videos):
                                all_raw_videos.append(video)

                # 作成日時でソート（新しい順）
                all_raw_videos.sort(key=lambda x: x['created_at'], reverse=True)

                # 指定された日付範囲内の動画のみを抽出
                for video in all_raw_videos:
                    created_at_utc = datetime.fromisoformat(
                        video['created_at'].replace('Z', '+00:00')
                    )
                    created_at_jst = created_at_utc.astimezone(jst)

                    # 指定された日付範囲内の動画のみを追加
                    if start_jst <= created_at_jst <= end_jst:
                        all_videos.append(video)
                        print(f"期間内の動画を発見: {video['title']} - {created_at_jst.strftime('%Y年%m月%d日 %H:%M:%S')}")
                    elif created_at_jst < start_jst:
                        # 開始日より古い動画に到達したら終了
                        break
                
                print(f"指定期間で {len(all_videos)}件の動画を発見")
            else:
                # デフォルト: 昨日分の動画を取得
                videos = twitch_api.get_videos(days_back=1)
                if videos:
                    for video in videos:
                        all_videos.append(video)
                
                print(f"昨日分で {len(all_videos)}件の動画を発見")
            
            if all_videos:
                print("\n=== 動画一覧（最新10件） ===")
                for i, video in enumerate(all_videos[:10]):  # 最新10件を表示
                    jst = pytz.timezone('Asia/Tokyo')
                    created_at_utc = datetime.fromisoformat(
                        video['created_at'].replace('Z', '+00:00')
                    )
                    created_at_jst = created_at_utc.astimezone(jst)
                    
                    # 動画長を時間:分:秒形式に変換
                    duration_seconds = twitch_api.parse_twitch_duration(video['duration'])
                    hours = duration_seconds // 3600
                    minutes = (duration_seconds % 3600) // 60
                    seconds = duration_seconds % 60
                    duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                    
                    print(f"\n【動画 {i+1}】")
                    print(f"タイトル: {video['title']}")
                    print(f"動画ID: {video['id']}")
                    print(
                        f"作成日時: "
                        f"{created_at_jst.strftime('%Y年%m月%d日 %H:%M:%S')} (JST)"
                    )
                    print(f"動画長: {duration_str} ({duration_seconds}秒)")
                    print(f"URL: https://www.twitch.tv/videos/{video['id']}")
                    print(f"視聴回数: {video.get('view_count', 'N/A')}")
                    print(f"言語: {video.get('language', 'N/A')}")
            else:
                print("昨日分でも動画が見つかりません")
                print("考えられる原因:")
                print("- チャンネル名が間違っている")
                print("- 配信アーカイブが保存されていない")
                print("- API権限が不足している")


        else:
            print("❌ 動画取得失敗")
            return False

        print("\n✅ Twitch設定は正常です")
        return True

    except Exception as e:
        print(f"❌ Twitch API接続エラー: {str(e)}")
        return False


def check_youtube_config():
    """YouTube設定を確認"""
    print("\n=== YouTube設定確認 ===")

    # ファイルの存在確認
    print("\n--- ファイル確認 ---")
    client_secret_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 'config', 'client_secret.json'
    )
    if os.path.exists(client_secret_path):
        print("✅ config/client_secret.json ファイル存在")
    else:
        print("❌ config/client_secret.json ファイルが見つかりません")
        print("Google Cloud Consoleからダウンロードしてconfig/フォルダに配置してください")
        return False

    # API認証テスト
    print("\n--- API認証テスト ---")
    try:
        youtube_api = YouTubeAPI()

        # 認証テスト
        print("YouTube API認証中...")
        if youtube_api.authenticate():
            print("✅ YouTube API認証成功")
        else:
            print("❌ YouTube API認証失敗")
            return False

        # チャンネル情報取得テスト
        print("チャンネル情報取得中...")
        try:
            # 認証されたアカウントのチャンネル情報を取得
            channels_response = youtube_api.youtube.channels().list(
                part='snippet',
                mine=True
            ).execute()

            if channels_response['items']:
                channel = channels_response['items'][0]
                print(
                    f"✅ チャンネル情報取得成功: "
                    f"{channel['snippet']['title']}"
                )
                print(f"チャンネルID: {channel['id']}")
            else:
                print("❌ チャンネル情報取得失敗")
                return False

        except Exception as e:
            print(f"❌ チャンネル情報取得エラー: {str(e)}")
            return False

        print("\n✅ YouTube設定は正常です")
        return True

    except Exception as e:
        print(f"❌ YouTube API接続エラー: {str(e)}")
        return False


def check_environment():
    """環境設定を確認"""
    print("\n=== 環境設定確認 ===")

    # Python環境
    print(f"Python バージョン: {sys.version}")

    # プロジェクトルートディレクトリに移動
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)

    # 必要なファイルの存在確認
    print("\n--- ファイル確認 ---")
    files_to_check = [
        ('app/main.py', 'メインスクリプト'),
        ('app/config.py', '設定ファイル'),
        ('app/twitch_api.py', 'Twitch API'),
        ('app/youtube_api.py', 'YouTube API'),
        ('app/video_downloader.py', '動画ダウンローダー'),
        ('app/upload_manager.py', 'アップロードマネージャー'),
    ]

    for filepath, description in files_to_check:
        if os.path.exists(filepath):
            print(f"✅ {description}: {filepath}")
        else:
            print(f"❌ {description}: {filepath} が見つかりません")

    # シェルスクリプトの確認
    script_files = [
        ('sh/run_upload.sh', '実行スクリプト'),
        ('sh/check_config.sh', '設定確認スクリプト'),
    ]

    for script_path, description in script_files:
        if os.path.exists(script_path):
            print(f"✅ {description}: {script_path}")
        else:
            print(f"❌ {description}: {script_path} が見つかりません")




def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='Twitch/YouTube設定確認ツール'
    )
    parser.add_argument(
        '--range', nargs=2, metavar=('START_DATETIME', 'END_DATETIME'),
        help='指定した日時範囲の動画を確認（例: --range "2024/12/01 00:00:00" "2024/12/07 23:59:59"）'
    )

    args = parser.parse_args()

    print("Twitch/YouTube設定確認ツール")
    print("=" * 50)

    # 日付範囲を解析
    start_datetime = None
    end_datetime = None
    if args.range:
        start_datetime = parse_datetime_arg(args.range[0])
        end_datetime = parse_datetime_arg(args.range[1])

    # 環境設定確認
    check_environment()

    # Twitch設定確認
    twitch_ok = check_twitch_config(start_datetime, end_datetime)

    # YouTube設定確認
    youtube_ok = check_youtube_config()

    # 総合結果
    print("\n" + "=" * 50)
    print("=== 総合結果 ===")

    if twitch_ok and youtube_ok:
        print("✅ すべての設定が正常です！")
        print("システムは使用可能です。")
        return 0
    else:
        print("❌ 一部の設定に問題があります")
        if not twitch_ok:
            print("- Twitch設定を確認してください")
        if not youtube_ok:
            print("- YouTube設定を確認してください")
        return 1


if __name__ == "__main__":
    sys.exit(main())
