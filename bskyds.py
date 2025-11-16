from atproto import Client
from dotenv import load_dotenv #pip install python-dotenv
from textblob import TextBlob #pip install and python -m textblob.download_corpora
import os
from datetime import datetime, timedelta, timezone
import json
import time

load_dotenv()
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

client = Client()
client.login(username, password)

def get_all_trump_posts_election_day():

    #get posts about Trump on election day, and classify by sentiment

    keyword = "Trump since:2024-11-05 until:2024-11-06"
    exclude_terms = ["Ivanka", "Melania", "Barron", "Donald Trump Jr."]
    cursor = None

    sentiment_data = {
        "positive": [],
        "neutral": [],
        "negative": []
    }

    total_fetched = 0

    while True:
        response = client.app.bsky.feed.search_posts(
            params={"q": keyword, "sort": "latest", "cursor": cursor}
        )

        if not response.posts:
            break

        for post in response.posts:
            text = getattr(post.record, "text", "")
            if not text:
                continue

            # exclude family 
            if any(term.lower() in text.lower() for term in exclude_terms):
                continue

            sentiment = TextBlob(text).sentiment.polarity

            post_info = {
                "author": post.author.handle,
                "text": text,
                "sentiment": sentiment,
                "likes": getattr(post, "like_count", 0),
                "reposts": getattr(post, "repost_count", 0),
                "replies": getattr(post, "reply_count", 0),
                "uri": post.uri,
                "timestamp": post.indexed_at,
            }

            # Classify by sentiment
            if sentiment > 0.2:
                sentiment_data["positive"].append(post_info)
            elif sentiment < -0.2:
                sentiment_data["negative"].append(post_info)
            else:
                sentiment_data["neutral"].append(post_info)

            total_fetched += 1

        cursor = getattr(response, "cursor", None)
        if not cursor:
            break

        print(f"Fetched {total_fetched} posts so far...")
        time.sleep(1)  # avoid rate limits

    print(f"Total posts fetched: {total_fetched}")
    return sentiment_data


def save_to_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# --- Run the script ---
print("Fetching all posts about Trump on 2024 election day...")
sentiment_results = get_all_trump_posts_election_day()

# Save results
output_file = "trump_posts_2024_election_day_all.json"
save_to_json(sentiment_results, output_file)

# Summary
pos = len(sentiment_results["positive"])
neg = len(sentiment_results["negative"])
neu = len(sentiment_results["neutral"])

print(f"📊 Positive: {pos}, Neutral: {neu}, Negative: {neg}")
