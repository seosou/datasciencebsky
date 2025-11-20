from atproto import Client
from dotenv import load_dotenv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import os
from datetime import datetime, timezone
import json
import time

load_dotenv()
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

client = Client()
client.login(username, password)

# Parameters
KEYWORD = "Trump"
START_DATE = datetime(2024, 11, 4, tzinfo=timezone.utc)
END_DATE   = datetime(2024, 11, 5, tzinfo=timezone.utc)
OUTPUT_FILE = "trump_posts_incremental.json"
SLEEP_BETWEEN_REQUESTS = 1
BATCH_SIZE = 50

# Load previous file if exists
try:
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        sentiment_data = json.load(f)
except FileNotFoundError:
    sentiment_data = {"positive": [], "neutral": [], "negative": []}

def save_incremental():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(sentiment_data, f, ensure_ascii=False, indent=4)

# Initialize VADER
analyzer = SentimentIntensityAnalyzer()

def fetch_posts(keyword, start_date, end_date):
    cursor = None
    total_collected = sum(len(v) for v in sentiment_data.values())

    while True:
        # Query is kept the same as your template
        query = f"{keyword} since:{start_date.date()} until:{end_date.date()}"

        response = client.app.bsky.feed.search_posts(
            params={"q": query, "sort": "latest", "cursor": cursor, "limit": BATCH_SIZE}
        )

        if not response.posts:
            print("No more posts returned by API.")
            break

        for post in response.posts:
            text = getattr(post.record, "text", "")
            if not text:
                continue

            # Convert timestamp
            ts = datetime.fromisoformat(post.indexed_at.replace("Z", "+00:00"))
            if not (start_date <= ts <= end_date):
                continue

            # ---- VADER sentiment ----
            score = analyzer.polarity_scores(text)["compound"]

            post_info = {
                "author": post.author.handle,
                "text": text,
                "sentiment": score,
                "likes": getattr(post, "like_count", 0),
                "reposts": getattr(post, "repost_count", 0),
                "replies": getattr(post, "reply_count", 0),
                "uri": post.uri,
                "timestamp": post.indexed_at,
            }

            # Categorization (matching your original thresholds)
            if score > 0.2:
                sentiment_data["positive"].append(post_info)
            elif score < -0.2:
                sentiment_data["negative"].append(post_info)
            else:
                sentiment_data["neutral"].append(post_info)

            total_collected += 1

            # Progress print every 10 posts
            if total_collected % 10 == 0:
                print(f"Collected {total_collected} posts so far...")
                save_incremental()

        cursor = getattr(response, "cursor", None)
        if not cursor:
            print("Reached end of available posts.")
            break

        time.sleep(SLEEP_BETWEEN_REQUESTS)

    save_incremental()
    print(f"Finished collecting posts. Total: {total_collected}")

if __name__ == "__main__":
    print(f"Starting collection for keyword '{KEYWORD}' from {START_DATE.date()} to {END_DATE.date()}")
    fetch_posts(KEYWORD, START_DATE, END_DATE)
