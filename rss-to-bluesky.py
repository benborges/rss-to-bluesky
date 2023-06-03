from dotenv import load_dotenv
import requests
import datetime
import re
import feedparser
import os
import time
from uniseg.graphemecluster import grapheme_clusters

load_dotenv()

ATP_HOST = os.getenv('ATP_HOST')
ATP_USERNAME = os.getenv('ATP_USERNAME')
ATP_PASSWORD = os.getenv('ATP_PASSWORD')
RSS_FEED_URL = os.getenv('RSS_FEED_URL')

def fetch_latest_rss_entry(rss_url):
    feed = feedparser.parse(rss_url)
    latest_entry = feed.entries[0]
    return latest_entry

def fetch_external_embed(uri):
    try:
        response = requests.get(uri)
        if response.status_code == 200:
            html_content = response.text

            title_match = re.search(r'<title>(.+?)</title>', html_content, re.IGNORECASE | re.DOTALL)
            title = title_match.group(1) if title_match else ""

            description_match = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']', html_content, re.IGNORECASE)
            description = description_match.group(1) if description_match else ""

            return {
                "uri": uri,
                "title": title,
                "description": description
            }
        else:
            print("Error fetching the website")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def trim_text(text, max_length=250):
    clusters = list(grapheme_clusters(text))
    if len(clusters) <= max_length:
        return text
    else:
        return "".join(clusters[:max_length])

def find_uri_position(text):
    pattern = r'(https?://\S+)'
    match = re.search(pattern, text)

    if match:
        uri = match.group(0)
        start_position = len(text[:text.index(uri)].encode('utf-8'))
        end_position = start_position + len(uri.encode('utf-8')) - 1
        return (uri, start_position, end_position)
    else:
        return None

def login(username, password):
    data = {"identifier": username, "password": password}
    resp = requests.post(
        ATP_HOST + "/xrpc/com.atproto.server.createSession",
        json=data
    )

    atp_auth_token = resp.json().get('accessJwt')
    if atp_auth_token == None:
        raise ValueError("No access token, is your password wrong?")

    did = resp.json().get("did")

    return atp_auth_token, did

def post_text(text, atp_auth_token, did, timestamp=None):
    if not timestamp:
        timestamp = datetime.datetime.now(datetime.timezone.utc)
    timestamp = timestamp.isoformat().replace('+00:00', 'Z')

    headers = {"Authorization": "Bearer " + atp_auth_token}

    found_uri = find_uri_position(text)
    if found_uri:
        uri, start_position, end_position = found_uri
        facets = [
            {
                "index": {
                    "byteStart": start_position,
                    "byteEnd": end_position + 1
                },
                "features": [
                    {
                        "$type": "app.bsky.richtext.facet#link",
                        "uri": uri
                    }
                ]
            },
        ]

        embed = {
            "$type": "app.bsky.embed.external",
            "external": fetch_external_embed(uri)
         }

    data = {
        "collection": "app.bsky.feed.post",
        "$type": "app.bsky.feed.post",
        "repo": "{}".format(did),
        "record": {
            "$type": "app.bsky.feed.post",
            "createdAt": timestamp,
            "text": text,
            "facets": facets,
            "embed": embed
        }
    }

    resp = requests.post(
        ATP_HOST + "/xrpc/com.atproto.repo.createRecord",
        json=data,
        headers=headers
    )

    return resp

def main():
    while True:
        latest_entry = fetch_latest_rss_entry(RSS_FEED_URL)

        title = latest_entry.title
        link = latest_entry.link
        post_content = f"{title} {link} #Ukraine"

        atp_auth_token, did = login(ATP_USERNAME, ATP_PASSWORD)
        post_resp = post_text(post_content, atp_auth_token, did)
        print(post_resp.json())

        time.sleep(300)  # Sleep for 5 minutes (300 seconds)

def lambda_handler(event, context):
    main()
    return {
        "statusCode": 200,
        "body": "Success"
    }

if __name__ == "__main__":
    main()
