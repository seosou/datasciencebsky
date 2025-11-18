from atproto import Client
from dotenv import load_dotenv #pip install python-dotenv
from textblob import TextBlob #pip install and python -m textblob.download_corpora
from datetime import datetime, timedelta, timezone
import json
import time

load_dotenv()
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

client = Client()
client.login(username, password)

KEYWORD = "Trump"
#EXCLUDE = ["Ivanka", "Melania", "Barron", "Eric", "Donald Trump Jr.", "Tiffany"]

OUTPUT_DIR = "trump_daily_data2"
MASTER_FILE = "trump_master_dataset2.json"
TREND_FILE = "trump_daily_sentiment_trends2.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 3 months before and after the 2024 election
START_DATE = datetime(2024, 11, 26, tzinfo=timezone.utc)
END_DATE   = datetime(2024, 12, 5, tzinfo=timezone.utc)

SLEEP = 1
LIMIT = 50 


def load_existing_day_data(date_str):
    """Load data if the day was already collected (resume automatically)."""
    path = f"{OUTPUT_DIR}/{date_str}.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"positive": [], "neutral": [], "negative": []}


def save_day_data(date_str, data):
    """Save daily data safely."""
    path = f"{OUTPUT_DIR}/{date_str}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def classify_sentiment(text):
    """Return sentiment label based on polarity."""
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.2:
        return "positive", polarity
    elif polarity < -0.2:
        return "negative", polarity
    else:
        return "neutral", polarity


def fetch_one_day(day):
    """Collect posts for a single day."""
    day_start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
    day_end   = day_start + timedelta(days=1)

    date_str = day_start.strftime("%Y-%m-%d")

    print(f"\nFetching posts for {date_str}...")

    # Load existing data if partially done
    sentiment_data = load_existing_day_data(date_str)

    cursor = None
    collected_so_far = sum(len(v) for v in sentiment_data.values())

    while True:
        query = f"{KEYWORD} since:{date_str} until:{day_end.strftime('%Y-%m-%d')}"

        response = client.app.bsky.feed.search_posts(
            params={"q": query, "sort": "latest", "cursor": cursor, "limit": LIMIT}
        )

        if not response.posts:
            print("  No more posts returned by API.")
            break

        for post in response.posts:
            text = getattr(post.record, "text", "")
            if not text:
                continue

            # Exclude family
            # if any(term.lower() in text.lower() for term in EXCLUDE):
            #     continue

            # Timestamp filtering
            ts = datetime.fromisoformat(post.indexed_at.replace("Z", "+00:00"))

            if not (day_start <= ts < day_end):
                continue  # enforce exact day boundaries

            sentiment_label, polarity = classify_sentiment(text)

            post_info = {
                "author": post.author.handle,
                "text": text,
                "sentiment": polarity,
                "label": sentiment_label,
                "likes": getattr(post, "like_count", 0),
                "reposts": getattr(post, "repost_count", 0),
                "replies": getattr(post, "reply_count", 0),
                "uri": post.uri,
                "timestamp": post.indexed_at,
            }

            sentiment_data[sentiment_label].append(post_info)
            collected_so_far += 1

            if collected_so_far % 10 == 0:
                save_day_data(date_str, sentiment_data)
                print(f"  Saved progress — {collected_so_far} posts...")

        cursor = getattr(response, "cursor", None)
        if not cursor:
            print("  Reached end of day results.")
            break

        time.sleep(SLEEP)

    save_day_data(date_str, sentiment_data)
    print(f"Finished {date_str}: {collected_so_far} posts total.")
    return sentiment_data

current = START_DATE

all_days_data = []
daily_trends = {}

print("\nBeginning full Trump sentiment collection...\n")

while current <= END_DATE:
    date_str = current.strftime("%Y-%m-%d")

    daily_data = fetch_one_day(current)

    total_pos = len(daily_data["positive"])
    total_neu = len(daily_data["neutral"])
    total_neg = len(daily_data["negative"])

    daily_trends[date_str] = {
        "positive": total_pos,
        "neutral": total_neu,
        "negative": total_neg,
        "total": total_pos + total_neu + total_neg
    }

    # Combine into master list
    for label in ["positive", "neutral", "negative"]:
        for post in daily_data[label]:
            all_days_data.append(post)

    # move to next day
    current += timedelta(days=1)

with open(MASTER_FILE, "w", encoding="utf-8") as f:
    json.dump(all_days_data, f, ensure_ascii=False, indent=4)

with open(TREND_FILE, "w", encoding="utf-8") as f:
    json.dump(daily_trends, f, ensure_ascii=False, indent=4)

print("\nCOMPLETED FULL COLLECTION")
print(f"Master dataset saved to: {MASTER_FILE}")
print(f"Daily sentiment trends saved to: {TREND_FILE}")
print("\nExample trend entries:")
for k, v in list(daily_trends.items())[:10]:
    print(k, v)
