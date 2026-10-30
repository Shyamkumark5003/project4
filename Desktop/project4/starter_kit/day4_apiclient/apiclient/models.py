from datetime import date

from pydantic import BaseModel


class Book(BaseModel):
    id: int
    name: str
    status: str
    category: str
    created: date
