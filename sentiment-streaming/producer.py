import redis
import json
import time
import random

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

comments = [
    # POSITIF
    "The beach is absolutely beautiful, great waves!",
    "The service was very friendly, I loved it!",
    "Amazing sunset view, highly recommended!",
    "The food is delicious and affordable.",
    "I will definitely come back again.",
    "Public transport is easy and cheap.",
    "The hotel facilities are complete and clean.",
    # NETRAL
    "The weather today is just okay.",
    "The place is quite crowded but still fine.",
    "The ticket price is standard, not too expensive.",
    "The journey took 2 hours.",
    "There are many souvenir options.",
    # NEGATIF
    "The food was good but too expensive.",
    "Too many street vendors disturbing.",
    "Public transport is hard to find here.",
    "Did not meet expectations, disappointed.",
    "The accommodation was comfortable but AC not cold.",
    "Terrible traffic jam.",
    "Ticket price is too high for the facilities provided."
]

print("Producer started. Sending English comments every 2 seconds...")

while True:
    text = random.choice(comments)
    comment = {"text": text, "timestamp": time.time()}
    r.rpush("comments_queue", json.dumps(comment))
    print(f"Sent: {text[:50]}...")
    time.sleep(2)