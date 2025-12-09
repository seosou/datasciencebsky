import json
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

FILE = "final_harris_master_dataset.json"

with open(FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

timestamps = []
sentiments = []

for post in data:
    try:
        timestamps.append(datetime.fromisoformat(post["timestamp"].replace("Z", "+00:00")))
        sentiments.append(post["sentiment"])
    except KeyError:
        continue

sentiments = np.array(sentiments)
dates = np.array([ts.date() for ts in timestamps])


election_day = datetime(2024, 11, 5).date()

pre_mask = dates < election_day
post_mask = dates > election_day


def summarize_period(mask, label):
    period_pols = sentiments[mask]
    period_dates = dates[mask]
    total_posts = len(period_pols)
    unique_days = np.unique(period_dates)
    avg_posts_per_day = total_posts / len(unique_days) if len(unique_days) > 0 else 0

    print(f"\n===== {label} =====")
    print(f"Total posts: {total_posts}")
    print(f"Average posts per day: {avg_posts_per_day:.2f}")
    print("Mean sentiment:   ", np.mean(period_pols))
    print("Median sentiment: ", np.median(period_pols))
    print("Std deviation:   ", np.std(period_pols))
    print("Min sentiment:    ", np.min(period_pols))
    print("Max sentiment:    ", np.max(period_pols))

    return period_pols

pre_pols = summarize_period(pre_mask, "Pre-Election")
post_pols = summarize_period(post_mask, "Post-Election")


unique_dates, inverse_indices = np.unique(dates, return_inverse=True)
daily_mean = np.array([np.mean(sentiments[inverse_indices == i]) for i in range(len(unique_dates))])

plt.figure(figsize=(14, 6))
plt.plot(unique_dates, daily_mean, label="Daily Mean", linewidth=2)
plt.axvline(election_day, color='red', linestyle='--', label='Election Day')
plt.grid(True, linestyle="--", alpha=0.4)
plt.legend()
plt.title("Harris Sentiment Over Time")
plt.xlabel("Date")
plt.ylabel("Sentiment")
plt.tight_layout()
plt.show()
