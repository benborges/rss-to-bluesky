# rss-to-bluesky
a script to fetch new posts items from an rss feed every 15 minutes and post the new items to bluesky


## How-to

cp .env-example .env

prepare the .env file with your 
- hosts, username 
- app password
- RSS feed

pip install -r requirements.txt


## Run
python3 rss-to-bluesky.py


## known bugs

- {'error': 'InvalidRequest', 'message': 'Invalid app.bsky.feed.post record: Record/text must not be longer than 300 graphemes'}

- Error fetching the website (when embed is enabled)
{'error': 'InvalidRequest', 'message': 'Invalid app.bsky.feed.post record: Record/embed/external must be an object'}
