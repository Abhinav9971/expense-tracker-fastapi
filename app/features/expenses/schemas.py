from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


# ── Request schemas ──────────────────────────────────────────────────────────

class ExpenseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    amount: float = Field(..., gt=0)
    category: str = Field(..., min_length=1, max_length=100)
    date: date
    description: Optional[str] = Field(default=None, max_length=500)


# ── Response schemas ─────────────────────────────────────────────────────────

class ExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    amount: float
    category: str
    date: date
    description: Optional[str] = None


class PaginatedExpenses(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[ExpenseResponse]


class CategoryBreakdown(BaseModel):
    category: str
    total: float
    count: int


class ExpenseSummary(BaseModel):
    month: int
    year: int
    total_spending: float
    breakdown: list[CategoryBreakdown]