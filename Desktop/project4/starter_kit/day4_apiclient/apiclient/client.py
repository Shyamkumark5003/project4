import time

import httpx

from apiclient.models import Book
from apiclient.retry import send_with_retry


class ApiClient:
    def __init__(
        self,
        base_url,
        *,
        timeout=5.0,
        max_retries=4,
        sleep=time.sleep,
        transport=None,
    ):
        # The timeout set here applies to every call made with this client.
        self._client = httpx.Client(base_url=base_url, timeout=timeout, transport=transport)
        self._max_retries = max_retries
        self._sleep = sleep

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def _get(self, path, **params):
        response = send_with_retry(
            self._client,
            "GET",
            path,
            max_retries=self._max_retries,
            sleep=self._sleep,
            params=params,
        )
        response.raise_for_status()  # 404 etc. stop here with a clear error
        return response.json()

    def iter_books(self, page_size=50, entity="books"):
        """Yield every record, one at a time, as a validated Book."""
        page = 1
        while True:
            body = self._get(f"/v1/{entity}", page=page, page_size=page_size)
            for record in body["items"]:
                yield Book.model_validate(record)  # bad record -> ValidationError
            if not body["has_more"]:
                return
            page += 1
