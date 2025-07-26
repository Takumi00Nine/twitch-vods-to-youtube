#!/usr/bin/env python3
import argparse
import sys
from datetime import datetime, timedelta
import pytz
from upload_manager import UploadManager
from config import Config

def main():
    parser = argparse.ArgumentParser(description='Twitch配信アーカイブをYouTubeに自動アップロード')
    parser.add_argument('--manual', type=int, metavar='DAYS', 
                       help='手動で指定した日数前の動画をアップロード')

    
    args = parser.parse_args()
    

    
    # UploadManagerを初期化
    upload_manager = UploadManager()
    
    if args.manual is not None:
        # 手動実行
        jst = pytz.timezone('Asia/Tokyo')
        now_jst = datetime.now(jst)
        target_date = now_jst - timedelta(days=args.manual)
        print(f"手動アップロードを開始: {args.manual}日前（{target_date.strftime('%Y年%m月%d日')}）の動画")
        upload_manager.run_manual_upload(args.manual)
        
    else:
        # デフォルト: 前日の動画をアップロード
        jst = pytz.timezone('Asia/Tokyo')
        now_jst = datetime.now(jst)
        yesterday_jst = now_jst - timedelta(days=1)
        print(f"前日（{yesterday_jst.strftime('%Y年%m月%d日')}）の配信アーカイブをアップロードします")
        upload_manager.process_yesterday_videos()

if __name__ == "__main__":
    main() 