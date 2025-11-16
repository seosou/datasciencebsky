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

def get_trump_posts_election_day(limit=100, pages=5):

    #get posts about Trump on election day, and classify by sentiment
 
    keyword = "Trump since:2024-11-05 until:2024-11-06" # can change day and we might have to set up timezone
    #exclude_terms = ["Ivanka", "Melania", "Barron", "Donald Trump Jr."] might have to clean up after because this might take out trump too
    cursor = None

    sentiment_data = {
        "positive": [],
        "neutral": [],
        "negative": []
    }

    for _ in range(pages):
        response = client.app.bsky.feed.search_posts(
            params={"q": keyword, "sort": "latest", "cursor": cursor}
        )

        if not response.posts:
            break

        for post in response.posts:
            text = getattr(post.record, "text", "")
            if not text:
                continue

            # if any(term.lower() in text.lower() for term in exclude_terms):
            #     continue

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

        cursor = getattr(response, "cursor", None)
        if not cursor:
            break

        time.sleep(1)  # avoid rate limits

    # Trim to limit per sentiment
    for key in sentiment_data:
        sentiment_data[key] = sentiment_data[key][:limit]

    return sentiment_data


def save_to_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


print("Searching posts about Trump on 2024 election day...")

sentiment_results = get_trump_posts_election_day(limit=100, pages=5)

output_file = "trump_posts_2024_election_day.json"
save_to_json(sentiment_results, output_file)

pos = len(sentiment_results["positive"])
neg = len(sentiment_results["negative"])
neu = len(sentiment_results["neutral"])

print(f"✅ Saved results to {output_file}")
print(f"📊 Positive: {pos}, Neutral: {neu}, Negative: {neg}")
