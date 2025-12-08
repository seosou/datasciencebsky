import json
import os
from datetime import datetime

# Input files
FILES = [
    "trump_daily_sentiment_trends_matthew.json",
    "trump_daily_sentiment_trends.json",
    "trump_daily_sentiment_trends2.json",
]

OUTPUT_FILE = "trump_daily_sentiment_trends_combined.json"

combined = {}

def is_date(s: str):
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return True
    except:
        return False

print("\nCombining trend files...\n")

for file in FILES:
    if not os.path.exists(file):
        print(f"File not found, skipping: {file}")
        continue

    print(f"Reading: {file}")

    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

    for date_str, counts in data.items():
        if not is_date(date_str):
            print(f"Skipping invalid date key: {date_str}")
            continue

        # Overwrite logic → latest file wins
        combined[date_str] = counts

# Sort by date
combined_sorted = dict(sorted(
    combined.items(),
    key=lambda x: datetime.strptime(x[0], "%Y-%m-%d")
))

# Save
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(combined_sorted, f, ensure_ascii=False, indent=4)

print(f"\nCombined trend file saved to: {OUTPUT_FILE}")
print(f"Total days included: {len(combined_sorted)}")

print("\nSample output dates:")
for d in list(combined_sorted)[:10]:
    print(" ", d)
print("...")
