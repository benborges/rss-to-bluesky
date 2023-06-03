import requests
import datetime
import re
import feedparser
import os
import time
import threading
from dotenv import load_dotenv

load_dotenv()

ATP_HOST = os.getenv('ATP_HOST')
ATP_USERNAME = os.getenv('ATP_USERNAME')
ATP_PASSWORD = os.getenv('ATP_PASSWORD')
RSS_FEED_URLS = os.getenv('RSS_FEED_URLS').split(';')  # split the URLs by semicolon

latest_posts = [None for _ in range(len(RSS_FEED_URLS))]  # initialize with None for each RSS feed

def fetch_latest_rss_entry(rss_urls):
    latest_entries = []
    for url in rss_urls:
        feed = feedparser.parse(url)
        latest_entry = feed.entries[0]
        latest_entries.append(latest_entry)
    return latest_entries

# ... keep the rest of the functions as they are ...

def check_rss_feed():
    global latest_posts
    while True:
        latest_entries = fetch_latest_rss_entry(RSS_FEED_URLS)
        for i, latest_entry in enumerate(latest_entries):
            if latest_entry != latest_posts[i]:
                latest_posts[i] = latest_entry
                title = latest_entry.title
                link = latest_entry.link
                post_content = f"New Update:\n{title} {link}"
                atp_auth_token, did = login(ATP_USERNAME,  ATP_PASSWORD)
                post_resp = post_text(post_content, atp_auth_token, did)
                print(f"Posted: {post_resp.json()}")
        time.sleep(5 * 60)  # wait for 5 minutes

def main():
    t = threading.Thread(target=check_rss_feed)
    t.start()

if __name__ == "__main__":
    main()
