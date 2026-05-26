from dataclasses import dataclass
from datetime import date
from typing import Optional
from uuid import UUID


@dataclass
class Expense:
    """Internal domain model — never exposed directly in API responses."""
    id: UUID
    title: str
    amount: float
    category: str
    date: date
    description: Optional[str] = None