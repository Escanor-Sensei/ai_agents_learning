"""
test_api.py — Quick API health & generate endpoint test.

Usage:
    1. Start the server:  python api.py
    2. Run this script:   python test_api.py
"""

import requests

BASE = "http://localhost:8000"

# 1. Health check
print("[1] GET /health")
r = requests.get(f"{BASE}/health")
print(f"    Status: {r.status_code} | Body: {r.json()}\n")

# 2. Generate blog
print("[2] POST /generate")
r = requests.post(f"{BASE}/generate", json={"topic": "When to Use an AI-Agent"})
print(f"    Status: {r.status_code}")
if r.ok:
    data = r.json()
    print(f"    Topic: {data['topic']}")
    print(f"    Retries: {data['retry_count']}")
    print(f"    Blog (first 300 chars): {data['blog_post'][:300]}...")
else:
    print(f"    Error: {r.text}")
