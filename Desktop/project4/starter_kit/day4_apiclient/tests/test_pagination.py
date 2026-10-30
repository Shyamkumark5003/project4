import httpx
import pytest
from pydantic import ValidationError

from apiclient.client import ApiClient

RECORDS = [
    {
        "id": i,
        "name": f"Book {i}",
        "status": "active",
        "category": "alpha",
        "created": "2025-01-01",
    }
    for i in range(1, 6)
]


def pages_handler(request):
    page = int(request.url.params["page"])
    size = int(request.url.params["page_size"])
    start = (page - 1) * size
    return httpx.Response(
        200,
        json={
            "items": RECORDS[start : start + size],
            "page": page,
            "page_size": size,
            "total": len(RECORDS),
            "has_more": start + size < len(RECORDS),
        },
    )


def make_api(handler):
    return ApiClient(
        "http://test",
        transport=httpx.MockTransport(handler),
        sleep=lambda s: None,  # no real waiting in tests
    )


def test_yields_all_records_in_order():
    api = make_api(pages_handler)
    ids = [book.id for book in api.iter_books(page_size=2)]
    assert ids == [1, 2, 3, 4, 5]


def test_one_call_per_page_then_stops():
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        return pages_handler(request)

    api = make_api(handler)
    list(api.iter_books(page_size=2))
    assert calls["n"] == 3  # 2 + 2 + 1 records


def test_empty_result():
    def handler(request):
        return httpx.Response(200, json={"items": [], "has_more": False})

    assert list(make_api(handler).iter_books()) == []


def test_bad_record_raises_validation_error():
    def handler(request):
        bad = {"id": "abc", "name": "x"}
        return httpx.Response(200, json={"items": [bad], "has_more": False})

    with pytest.raises(ValidationError):
        list(make_api(handler).iter_books())


def test_retry_works_in_the_middle_of_pagination():
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        if calls["n"] == 2:  # the second call (page 2) fails once
            return httpx.Response(500)
        return pages_handler(request)

    api = make_api(handler)
    ids = [book.id for book in api.iter_books(page_size=2)]
    assert ids == [1, 2, 3, 4, 5]  # nothing lost
    assert calls["n"] == 4  # 3 pages + 1 retry


def test_timeout_is_set_on_the_client():
    api = make_api(pages_handler)
    assert api._client.timeout == httpx.Timeout(5.0)
