#!/usr/bin/env python3
"""
Twitch設定とYouTube設定を確認するツール
"""

import os
import sys
import requests
from datetime import datetime
import pytz
from config import Config
from twitch_api import TwitchAPI
from youtube_api import YouTubeAPI

def check_twitch_config():
    """Twitch設定を確認"""
    
    print("=== Twitch設定確認 ===")
    
    # 基本設定の確認
    print(f"Client ID: {'✅ 設定済み' if Config.TWITCH_CLIENT_ID else '❌ 未設定'}")
    print(f"Client Secret: {'✅ 設定済み' if Config.TWITCH_CLIENT_SECRET else '❌ 未設定'}")
    print(f"Channel Name: {'✅ 設定済み' if Config.TWITCH_CHANNEL_NAME else '❌ 未設定'}")
    
    if not all([Config.TWITCH_CLIENT_ID, Config.TWITCH_CLIENT_SECRET, Config.TWITCH_CHANNEL_NAME]):
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
            
            # デバッグ情報を追加
            if len(videos) == 0:
                print("\n--- デバッグ情報 ---")
                print(f"対象チャンネル: {Config.TWITCH_CHANNEL_NAME}")
                print(f"チャンネルID: {channel_id}")
                
                # より広い範囲で動画を取得してみる
                print("過去7日間の動画を確認中...")
                all_videos = twitch_api.get_videos(days_back=7)
                if all_videos:
                    print(f"過去7日間で {len(all_videos)}件の動画を発見")
                    for i, video in enumerate(all_videos[:5]):  # 最新5件を表示
                        jst = pytz.timezone('Asia/Tokyo')
                        created_at_utc = datetime.fromisoformat(video['created_at'].replace('Z', '+00:00'))
                        created_at_jst = created_at_utc.astimezone(jst)
                        print(f"  {i+1}. {video['title']} - {created_at_jst.strftime('%Y年%m月%d日 %H:%M:%S')} (JST)")
                else:
                    print("過去7日間でも動画が見つかりません")
                    print("考えられる原因:")
                    print("- チャンネル名が間違っている")
                    print("- 配信アーカイブが保存されていない")
                    print("- API権限が不足している")
            
            # 最新の動画情報を表示
            if videos:
                latest_video = videos[0]
                jst = pytz.timezone('Asia/Tokyo')
                created_at_utc = datetime.fromisoformat(latest_video['created_at'].replace('Z', '+00:00'))
                created_at_jst = created_at_utc.astimezone(jst)
                
                print(f"最新動画: {latest_video['title']}")
                print(f"作成日時: {created_at_jst.strftime('%Y年%m月%d日 %H:%M:%S')} (JST)")
                print(f"動画長: {latest_video['duration']}秒")
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
    if os.path.exists('client_secret.json'):
        print("✅ client_secret.json ファイル存在")
    else:
        print("❌ client_secret.json ファイルが見つかりません")
        print("Google Cloud Consoleからダウンロードしてください")
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
                print(f"✅ チャンネル情報取得成功: {channel['snippet']['title']}")
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
    
    # 必要なファイルの存在確認
    print("\n--- ファイル確認 ---")
    files_to_check = [
        ('main.py', 'メインスクリプト'),
        ('config.py', '設定ファイル'),
        ('twitch_api.py', 'Twitch API'),
        ('youtube_api.py', 'YouTube API'),
        ('video_downloader.py', '動画ダウンローダー'),
        ('upload_manager.py', 'アップロードマネージャー'),
        ('run_upload.sh', '実行スクリプト'),
    ]
    
    for filename, description in files_to_check:
        if os.path.exists(filename):
            print(f"✅ {description}: {filename}")
        else:
            print(f"❌ {description}: {filename} が見つかりません")
    
    # 外部ツールの確認
    print("\n--- 外部ツール確認 ---")
    
    # yt-dlpのPythonライブラリ確認
    try:
        import yt_dlp
        print(f"✅ 動画ダウンロード・情報取得: yt-dlp (Pythonライブラリ)")
    except ImportError:
        print(f"❌ 動画ダウンロード・情報取得: yt-dlp がインストールされていません")

def main():
    """メイン関数"""
    print("Twitch/YouTube設定確認ツール")
    print("=" * 50)
    
    # 環境設定確認
    check_environment()
    
    # Twitch設定確認
    twitch_ok = check_twitch_config()
    
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