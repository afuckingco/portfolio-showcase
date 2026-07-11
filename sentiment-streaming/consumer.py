import redis
import json
import time
from textblob import TextBlob
import pandas as pd
import os

# Koneksi Redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# File CSV untuk riwayat
csv_path = "data/sentiment_history.csv"
os.makedirs("data", exist_ok=True)

print("Consumer started. Waiting for comments...")

def get_sentiment(text):
    """Mengembalikan POSITIVE, NEUTRAL, NEGATIVE berdasarkan polaritas TextBlob."""
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.05:
        return "POSITIVE"
    elif polarity < -0.05:
        return "NEGATIVE"
    else:
        return "NEUTRAL"

while True:
    comment_data = r.blpop("comments_queue", timeout=1)
    if comment_data:
        _, value = comment_data
        comment = json.loads(value)
        text = comment["text"]
        
        sentiment = get_sentiment(text)
        confidence = abs(TextBlob(text).sentiment.polarity)  # kepercayaan sederhana
        
        timestamp = comment.get("timestamp", time.time())
        record = {
            "text": text,
            "sentiment": sentiment,
            "confidence": confidence,
            "timestamp": timestamp
        }
        r.hset("sentiment_results", str(timestamp), json.dumps(record))
        
        # Simpan ke CSV
        df = pd.DataFrame([record])
        if not os.path.exists(csv_path):
            df.to_csv(csv_path, index=False)
        else:
            df.to_csv(csv_path, mode='a', header=False, index=False)
        
        print(f"Processed: {text[:50]}... -> {sentiment} ({confidence:.2f})")
    else:
        time.sleep(0.1)