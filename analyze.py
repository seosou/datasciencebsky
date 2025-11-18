import json
import sys
from collections import Counter
from datetime import datetime


def load_data(file_path):
    """Load the JSON file that contains the sentiment data."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: Invalid JSON format.")
        sys.exit(1)


def basic_counts(data):
    pos = len(data["positive"])
    neu = len(data["neutral"])
    neg = len(data["negative"])
    total = pos + neu + neg
    return {
        "positive": pos,
        "neutral": neu,
        "negative": neg,
        "total_posts": total,
    }


def average_sentiment(data):
    all_posts = data["positive"] + data["neutral"] + data["negative"]
    if not all_posts:
        return 0
    return sum(p["sentiment"] for p in all_posts) / len(all_posts)


def top_authors(data, top_n=10):
    all_posts = data["positive"] + data["neutral"] + data["negative"]
    authors = [p["author"] for p in all_posts]
    return Counter(authors).most_common(top_n)


def most_liked_posts(data, top_n=5):
    all_posts = data["positive"] + data["neutral"] + data["negative"]
    return sorted(all_posts, key=lambda x: x["likes"], reverse=True)[:top_n]


def date_distribution(data):
    all_posts = data["positive"] + data["neutral"] + data["negative"]
    dates = [
        datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00")).date()
        for p in all_posts
    ]
    return Counter(dates).most_common()


def keyword_frequency(data, keyword="trump"):
    all_posts = data["positive"] + data["neutral"] + data["negative"]
    return sum(keyword.lower() in p["text"].lower() for p in all_posts)


def sentiment_interaction_stats(data):
    results = {}

    for sentiment_type in ["positive", "neutral", "negative"]:
        posts = data[sentiment_type]

        if len(posts) == 0:
            results[sentiment_type] = {
                "avg_likes": 0,
                "avg_replies": 0,
                "avg_reposts": 0,
                "avg_total_interactions": 0,
            }
            continue

        avg_likes = sum(p["likes"] for p in posts) / len(posts)
        avg_replies = sum(p["replies"] for p in posts) / len(posts)
        avg_reposts = sum(p["reposts"] for p in posts) / len(posts)

        results[sentiment_type] = {
            "avg_likes": round(avg_likes, 3),
            "avg_replies": round(avg_replies, 3),
            "avg_reposts": round(avg_reposts, 3),
            "avg_total_interactions": round(
                avg_likes + avg_replies + avg_reposts, 3
            ),
        }

    return results


def print_report(data, filename):
    print("\n===== JSON ANALYSIS REPORT =====\n")
    print(f"Analyzing file: {filename}\n")

    counts = basic_counts(data)
    print("Total Posts:", counts["total_posts"])
    print("Positive:", counts["positive"])
    print("Neutral:", counts["neutral"])
    print("Negative:", counts["negative"])

    print("\nAverage Sentiment:", round(average_sentiment(data), 3))

    print("\nTop Authors:")
    for author, c in top_authors(data):
        print(f"  {author}: {c} posts")

    print("\nMost Liked Posts:")
    for p in most_liked_posts(data):
        print(f"{p['likes']} | {p['author']}: {p['text'][:60]}...")

    print("\nPosts Per Day:")
    for d, c in date_distribution(data):
        print(f"  {d}: {c} posts")

    print("\nKeyword Frequency:")
    print("  'Trump' appears in", keyword_frequency(data, "trump"), "posts")

    print("\nAverage Interactions Per Sentiment:")
    stats = sentiment_interaction_stats(data)
    for sentiment, values in stats.items():
        print(f"\n{sentiment.capitalize()}:")
        print(f"  Avg Likes: {values['avg_likes']}")
        print(f"  Avg Replies: {values['avg_replies']}")
        print(f"  Avg Reposts: {values['avg_reposts']}")
        print(f"  Avg Total Interactions: {values['avg_total_interactions']}")

    print("\n================================\n")


if __name__ == "__main__":

    #example "python analyze.py trump_posts_incremental.json"

    if len(sys.argv) != 2:
        print("Usage: python analyze_json.py <json_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    data = load_data(input_file)
    print_report(data, input_file)
