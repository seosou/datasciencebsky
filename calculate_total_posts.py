import json
from datetime import datetime

with open("final_harris_daily_sentiment.json", "r", encoding="utf-8") as f:
    trends = json.load(f)

oct_6_to_nov_4_start = datetime(2024, 10, 6)
oct_6_to_nov_4_end = datetime(2024, 11, 4)
nov_5_start = datetime(2024, 11, 5)
nov_5_end = datetime(2024, 11, 5)
nov_6_to_dec_5_start = datetime(2024, 11, 6)
nov_6_to_dec_5_end = datetime(2024, 12, 5)

oct_6_to_nov_4_positive = 0
oct_6_to_nov_4_negative = 0
oct_6_to_nov_4_neutral = 0
oct_6_to_nov_4_total = 0

nov_5_positive = 0
nov_5_negative = 0
nov_5_neutral = 0
nov_5_total = 0

nov_6_to_dec_5_positive = 0
nov_6_to_dec_5_negative = 0
nov_6_to_dec_5_neutral = 0
nov_6_to_dec_5_total = 0

total_positive_posts = 0
total_negative_posts = 0
total_neutral_posts = 0
total_posts = 0


for date_str, counts in trends.items():
    current = datetime.strptime(date_str, "%Y-%m-%d")

    if oct_6_to_nov_4_start <= current <= oct_6_to_nov_4_end:
        oct_6_to_nov_4_positive += counts.get("positive", 0)
        oct_6_to_nov_4_negative += counts.get("negative", 0)
        oct_6_to_nov_4_neutral += counts.get("neutral", 0)
        oct_6_to_nov_4_total += counts.get("total", 0)


    if nov_5_start <= current <= nov_5_end:
        nov_5_positive += counts.get("positive", 0)
        nov_5_negative += counts.get("negative", 0)
        nov_5_neutral += counts.get("neutral", 0)
        nov_5_total += counts.get("total", 0)


    if nov_6_to_dec_5_start <= current <= nov_6_to_dec_5_end:
        nov_6_to_dec_5_positive += counts.get("positive", 0)
        nov_6_to_dec_5_negative += counts.get("negative", 0)
        nov_6_to_dec_5_neutral += counts.get("neutral", 0)
        nov_6_to_dec_5_total += counts.get("total", 0)


total_positive_posts = oct_6_to_nov_4_positive + nov_5_positive + nov_6_to_dec_5_positive
total_negative_posts = oct_6_to_nov_4_negative + nov_5_negative + nov_6_to_dec_5_negative
total_neutral_posts = oct_6_to_nov_4_neutral + nov_5_neutral + nov_6_to_dec_5_neutral
total_posts = oct_6_to_nov_4_total + nov_5_total + nov_6_to_dec_5_total

table = [
    ["Date Range", "Positive Posts", "Negative Posts", "Neutral Posts", "Total Posts"],
    ["10/6-11/4", oct_6_to_nov_4_positive, oct_6_to_nov_4_negative, oct_6_to_nov_4_neutral, oct_6_to_nov_4_total],
    ["11/5", nov_5_positive, nov_5_negative, nov_5_neutral, nov_5_total],
    ["11/6-12/5", nov_6_to_dec_5_positive, nov_6_to_dec_5_negative, nov_6_to_dec_5_neutral, nov_6_to_dec_5_total],
    ["Total", total_positive_posts, total_negative_posts, total_neutral_posts, total_posts]
]

print(f"{'Date Range':<25}{'Positive Posts':<15}{'Negative Posts':<15}{'Neutral Posts':<15}{'Total Posts':<15}")
for row in table[1:]:
    print(f"{row[0]:<25}{row[1]:<15}{row[2]:<15}{row[3]:<15}{row[4]:<15}")
