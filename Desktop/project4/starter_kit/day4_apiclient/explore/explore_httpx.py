import httpx

BASE = "http://127.0.0.1:9000"

with httpx.Client(base_url=BASE, timeout=5.0) as client:
    # 1. meta (curl: /v1/meta | jq .)
    r = client.get("/v1/meta")
    print("meta:", r.status_code, r.json())

    # 2. one page (curl -i + jq)
    r = client.get("/v1/books", params={"page": 1, "page_size": 3})
    body = r.json()
    print("status:", r.status_code)
    print("content-type:", r.headers["content-type"])
    print("keys:", list(body.keys()))
    print("count:", len(body["items"]))
    print("first:", body["items"][0])
    print("has_more:", body["has_more"])

    # 3. filter (jq select)
    r = client.get("/v1/books", params={"page": 1, "page_size": 20})
    active = [x for x in r.json()["items"] if x["status"] == "active"]
    print("active in first 20:", len(active))

    # 4. find the 500 (reset, then 20 calls)
    client.post("/v1/_reset")
    for i in range(1, 21):
        r = client.get("/v1/books", params={"page": 1})
        if r.status_code != 200:
            print("call", i, "->", r.status_code, r.text)
