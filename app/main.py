#!/usr/bin/env python3
import argparse
from datetime import datetime, timedelta
import pytz
from upload_manager import UploadManager


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


def main():
    parser = argparse.ArgumentParser(
        description='Twitch配信アーカイブをYouTubeに自動アップロード'
    )
    parser.add_argument(
        '--range', nargs=2, metavar=('START_DATETIME', 'END_DATETIME'),
        help='指定した日時範囲の動画をアップロード（例: --range "2024/12/01 00:00:00" "2024/12/07 23:59:59"）'
    )

    args = parser.parse_args()

    # UploadManagerを初期化
    upload_manager = UploadManager()

    if args.range is not None:
        # 日時範囲指定
        start_datetime_str, end_datetime_str = args.range
        jst = pytz.timezone('Asia/Tokyo')
        
        # 日時文字列をdatetimeオブジェクトに変換
        start_datetime = parse_datetime_arg(start_datetime_str)
        end_datetime = parse_datetime_arg(end_datetime_str)
        
        # 日本時間に変換
        start_datetime_jst = jst.localize(start_datetime)
        end_datetime_jst = jst.localize(end_datetime)
        
        upload_manager.run_manual_upload(start_datetime_jst, end_datetime_jst)
    else:
        # デフォルト: 前日の動画をアップロード（日時範囲指定を使用）
        jst = pytz.timezone('Asia/Tokyo')
        now_jst = datetime.now(jst)
        yesterday_start = now_jst - timedelta(days=1)
        yesterday_start = yesterday_start.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_end = yesterday_start.replace(hour=23, minute=59, second=59, microsecond=999999)
        print(
            f"前日（{yesterday_start.strftime('%Y年%m月%d日')}）"
            "の配信アーカイブをアップロードします"
        )
        upload_manager.run_manual_upload(yesterday_start, yesterday_end)


if __name__ == "__main__":
    main()
