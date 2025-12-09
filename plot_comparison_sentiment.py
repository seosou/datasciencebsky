import json
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

TRUMP_INPUT_FILE = "final_trump_daily_sentiment.json"
HARRIS_INPUT_FILE = "final_harris_daily_sentiment.json"

with open(TRUMP_INPUT_FILE, "r", encoding="utf-8") as f:
    trump_data = json.load(f)


with open(HARRIS_INPUT_FILE, "r", encoding="utf-8") as f:
    harris_data = json.load(f)


trump_dates = sorted(trump_data.keys(), key=lambda d: datetime.strptime(d, "%Y-%m-%d"))
harris_dates = sorted(harris_data.keys(), key=lambda d: datetime.strptime(d, "%Y-%m-%d"))

trump_pos_pct, trump_neu_pct, trump_neg_pct = [], [], []
harris_pos_pct, harris_neu_pct, harris_neg_pct = [], [], []

for date in trump_dates:
    positive = trump_data[date].get("positive", 0)
    neutral = trump_data[date].get("neutral", 0)
    negative = trump_data[date].get("negative", 0)
    total = trump_data[date].get("total", 0)

    if total > 0:
        trump_pos_pct.append((positive / total) * 100)
        trump_neu_pct.append((neutral / total) * 100)
        trump_neg_pct.append((negative / total) * 100)
    else:
        trump_pos_pct.append(0)
        trump_neu_pct.append(0)
        trump_neg_pct.append(0)


for date in harris_dates:
    positive = harris_data[date].get("positive", 0)
    neutral = harris_data[date].get("neutral", 0)
    negative = harris_data[date].get("negative", 0)
    total = harris_data[date].get("total", 0)

    if total > 0:
        harris_pos_pct.append((positive / total) * 100)
        harris_neu_pct.append((neutral / total) * 100)
        harris_neg_pct.append((negative / total) * 100)
    else:
        harris_pos_pct.append(0)
        harris_neu_pct.append(0)
        harris_neg_pct.append(0)

trump_dates_dt = [datetime.strptime(d, "%Y-%m-%d") for d in trump_dates]
harris_dates_dt = [datetime.strptime(d, "%Y-%m-%d") for d in harris_dates]


plt.figure(figsize=(14, 7))


plt.plot(trump_dates_dt, trump_pos_pct, label="Trump Positive (%)", color="green", linewidth=2)
plt.plot(trump_dates_dt, trump_neu_pct, label="Trump Neutral (%)", color="blue", linewidth=2)
plt.plot(trump_dates_dt, trump_neg_pct, label="Trump Negative (%)", color="red", linewidth=2)


plt.plot(harris_dates_dt, harris_pos_pct, label="Harris Positive (%)", color="darkgreen", linestyle="--", linewidth=2)
plt.plot(harris_dates_dt, harris_neu_pct, label="Harris Neutral (%)", color="deepskyblue", linestyle="--", linewidth=2)
plt.plot(harris_dates_dt, harris_neg_pct, label="Harris Negative (%)", color="darkred", linestyle="--", linewidth=2)


plt.xticks(trump_dates_dt, rotation=45, ha='right') 
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))


# plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=5)) 

plt.title("Sentiment Trend Comparison: Trump vs. Harris (Normalized to Percentages)")
plt.xlabel("Date")
plt.ylabel("Percentage of Posts (%)") 
plt.grid(True, linestyle="--", alpha=0.5)

plt.ylim(0, 100)

plt.legend()

plt.tight_layout()

plt.show()
