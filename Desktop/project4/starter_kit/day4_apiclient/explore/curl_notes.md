# Day 4: curl and jq notes (variant 1, Library)

## API facts
- Entity: books -> /v1/books
- Pagination: page (?page=1&page_size=N)
- Total records: 237
- Response keys: items, page, page_size, total, has_more

## Quirk
- Every 20th call returns 500 {"error":"internal_error"}
- The next call (21st) works, so retry helps

## One record
{
  "id": 1,
  "name": "Birch 0001",
  "status": "active",
  "category": "charlie",
  "created": "2025-09-08"
}

## What this means for my client
- Retry on 500
- Keep reading pages until has_more is false
- Validate each record with Pydantic
