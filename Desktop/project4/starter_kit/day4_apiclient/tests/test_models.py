import pytest
from pydantic import ValidationError

from apiclient.models import Book

GOOD = {
    "id": 1,
    "name": "Birch 0001",
    "status": "active",
    "category": "charlie",
    "created": "2025-09-08",
}


def test_valid_record():
    book = Book.model_validate(GOOD)
    assert book.id == 1
    assert book.created.year == 2025


def test_missing_field_raises():
    bad = {"id": 1, "name": "x"}
    with pytest.raises(ValidationError):
        Book.model_validate(bad)


def test_wrong_type_raises():
    bad = {**GOOD, "id": "abc"}
    with pytest.raises(ValidationError):
        Book.model_validate(bad)
