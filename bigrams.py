import json
import string
from collections import defaultdict
from datetime import datetime
import csv

harris_files = [
    "final_harris_master_dataset.json"
]
trump_files = [
    "final_trump_master_dataset.json"
]

election_day = datetime(2024, 11, 5).date()

stop_words = set([
    "i","me","my","myself","we","our","ours","ourselves","you","your","yours",
    "yourself","yourselves","he","him","his","himself","she","her","hers","herself",
    "it","its","itself","they","them","their","theirs","themselves","what","which",
    "who","whom","this","that","these","those","am","is","are","was","were","be",
    "been","being","have","has","had","having","do","does","did","doing","a","an",
    "the","and","but","if","or","because","as","until","while","of","at","by","for",
    "with","about","against","between","into","through","during","before","after",
    "above","below","to","from","up","down","in","out","on","off","over","under",
    "again","further","then","once","here","there","when","where","why","how","all",
    "any","both","each","few","more","most","other","some","such","no","nor","not",
    "only","own","same","so","than","too","very","s","t","can","will","just","don",
    "should","now"
])
punctuation = set(string.punctuation)

def generate_bigrams(tokens):
    return [tuple(tokens[i:i+2]) for i in range(len(tokens)-1)]

def clean_tokens(text):
    tokens = text.lower().split()
    return [t.strip(string.punctuation) for t in tokens 
            if t.strip(string.punctuation) not in stop_words and len(t.strip(string.punctuation)) > 2]

def process_files(files):
    bigram_counts = defaultdict(lambda: {"pre":0, "post":0})
    
    for filepath in files:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            
            posts = []
            if isinstance(data, dict):
                for label in ["positive", "neutral", "negative"]:
                    for post in data.get(label, []):
                        posts.append((post.get("text",""), post.get("timestamp","")))
            elif isinstance(data, list):
                for post in data:
                    posts.append((post.get("text",""), post.get("timestamp","")))
            
            for text, ts in posts:
                try:
                    post_date = datetime.fromisoformat(ts.replace("Z","+00:00")).date()
                except:
                    continue
                period = "pre" if post_date < election_day else "post"
                
                tokens = clean_tokens(text)
                for bigram in generate_bigrams(tokens):
                    bigram_counts[bigram][period] += 1
    return bigram_counts

results = {
    "harris": process_files(harris_files),
    "trump": process_files(trump_files)
}

all_bigrams = set(results["harris"].keys()).union(results["trump"].keys())
bigrams_table = []

for bigram in all_bigrams:
    entry = {"bigram": " ".join(bigram)}
    for candidate in ["harris","trump"]:
        counts = results[candidate].get(bigram, {"pre":0, "post":0})
        entry[f"{candidate}_pre"] = counts["pre"]
        entry[f"{candidate}_post"] = counts["post"]
    bigrams_table.append(entry)

bigrams_table = sorted(
    bigrams_table, 
    key=lambda x: x["harris_pre"] + x["harris_post"] + x["trump_pre"] + x["trump_post"], 
    reverse=True
)

top50_bigrams_table = bigrams_table[:50]

csv_file = "top50_bigrams_pre_post.csv"
with open(csv_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["bigram","harris_pre","harris_post","trump_pre","trump_post"])
    writer.writeheader()
    writer.writerows(top50_bigrams_table)

print(f"Top 50 bigrams pre/post election for both candidates saved to '{csv_file}'")
