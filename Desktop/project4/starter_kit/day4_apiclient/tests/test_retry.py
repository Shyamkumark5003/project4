import httpx
import pytest

from apiclient.retry import backoff_delay, send_with_retry


def make_client(handler):
    return httpx.Client(transport=httpx.MockTransport(handler), base_url="http://test")


def test_retries_500_then_succeeds():
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        if calls["n"] < 3:
            return httpx.Response(500)
        return httpx.Response(200, json={"ok": True})

    sleeps = []
    r = send_with_retry(make_client(handler), "GET", "/x", sleep=sleeps.append)
    assert r.status_code == 200
    assert calls["n"] == 3
    assert len(sleeps) == 2


def test_gives_up_after_max_retries():
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        return httpx.Response(503)

    with pytest.raises(httpx.HTTPStatusError):
        send_with_retry(make_client(handler), "GET", "/x", max_retries=2, sleep=lambda s: None)
    assert calls["n"] == 3  # 1 try + 2 retries


def test_no_retry_on_404():
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        return httpx.Response(404)

    r = send_with_retry(make_client(handler), "GET", "/x", sleep=lambda s: None)
    assert r.status_code == 404
    assert calls["n"] == 1


def test_retry_after_is_respected():
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(429, headers={"Retry-After": "2"})
        return httpx.Response(200)

    sleeps = []
    send_with_retry(make_client(handler), "GET", "/x", sleep=sleeps.append)
    assert sleeps == [2.0]


def test_timeout_is_retried():
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        if calls["n"] == 1:
            raise httpx.ReadTimeout("slow", request=request)
        return httpx.Response(200)

    sleeps = []
    r = send_with_retry(make_client(handler), "GET", "/x", sleep=sleeps.append)
    assert r.status_code == 200
    assert len(sleeps) == 1


def test_backoff_grows_and_is_capped():
    biggest = lambda low, high: high  # no randomness: always the maximum
    assert backoff_delay(0, rng=biggest) == 0.5
    assert backoff_delay(1, rng=biggest) == 1.0
    assert backoff_delay(2, rng=biggest) == 2.0
    assert backoff_delay(10, rng=biggest) == 30.0  # cap
