import tweepy
import json
import requests
import os
from dotenv import load_dotenv

# 載入環境變量
load_dotenv()

# 讀取設定檔
with open('config.json', 'r') as f:
    config = json.load(f)

# Twitter API 認證
auth = tweepy.OAuthHandler(
    os.getenv('TWITTER_CONSUMER_KEY'),
    os.getenv('TWITTER_CONSUMER_SECRET')
)
auth.set_access_token(
    os.getenv('TWITTER_ACCESS_TOKEN'),
    os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
)
api = tweepy.API(auth)

# 創建一個串流監聽器
class MyStreamListener(tweepy.Stream):
    def on_status(self, status):
        if status.user.screen_name in config['tracked_accounts']:
            if config['notification_settings']['tweets'] and not status.retweeted:
                send_notification(f"新推文: {status.user.screen_name} 說: {status.text}")
            elif config['notification_settings']['retweets'] and hasattr(status, 'retweeted_status'):
                send_notification(f"轉推: {status.user.screen_name} 轉推了: {status.text}")
            elif config['notification_settings']['replies'] and status.in_reply_to_status_id is not None:
                send_notification(f"回覆: {status.user.screen_name} 回覆了: {status.text}")

def send_notification(message):
    # 使用環境變量中的webhook URL
    webhook_url = os.getenv('WEBHOOK_URL')
    requests.post(webhook_url, json={"content": message})

# 開始監聽
myStream = MyStreamListener(
    os.getenv('TWITTER_CONSUMER_KEY'),
    os.getenv('TWITTER_CONSUMER_SECRET'),
    os.getenv('TWITTER_ACCESS_TOKEN'),
    os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
)
myStream.filter(follow=[api.get_user(screen_name=screen_name).id_str for screen_name in config['tracked_accounts']])