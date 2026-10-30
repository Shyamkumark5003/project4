import random
import time

import httpx

RETRY_STATUS = {429, 500, 502, 503, 504}


def backoff_delay(attempt, base=0.5, cap=30.0, rng=random.uniform):
    """Wait time before the next try: exponential growth, capped, with jitter."""
    ceiling = min(cap, base * (2**attempt))
    return rng(0, ceiling)


def parse_retry_after(value):
    """Retry-After header in seconds. Returns None if missing or not a number."""
    if value is None:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        return None


def send_with_retry(
    client, method, url, *, max_retries=4, sleep=time.sleep, rng=random.uniform, **kwargs
):
    """Send one request. Retry on 5xx, 429 and network errors. Raise when out of tries."""
    for attempt in range(max_retries + 1):
        try:
            response = client.request(method, url, **kwargs)
        except httpx.TransportError:  # includes timeouts
            if attempt == max_retries:
                raise
            sleep(backoff_delay(attempt, rng=rng))
            continue

        if response.status_code not in RETRY_STATUS:
            return response  # success, or an error that retrying cannot fix

        if attempt == max_retries:
            response.raise_for_status()  # out of tries: raise HTTPStatusError

        wait = parse_retry_after(response.headers.get("Retry-After"))
        if wait is None:
            wait = backoff_delay(attempt, rng=rng)
        sleep(wait)
