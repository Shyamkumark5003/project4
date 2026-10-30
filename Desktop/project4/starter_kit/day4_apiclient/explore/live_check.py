import httpx

from apiclient.client import ApiClient

BASE = "http://127.0.0.1:9000"

httpx.post(f"{BASE}/v1/_reset")  # counters back to zero

with ApiClient(BASE, sleep=lambda s: None) as api:
    books = list(api.iter_books(page_size=10))

print("records:", len(books))
print("unique ids:", len({b.id for b in books}))
print("first:", books[0])
print("last:", books[-1])
