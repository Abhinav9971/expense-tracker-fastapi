"""Unit tests for the service layer using FakeExpenseRepository."""
import pytest
from datetime import date
from typing import Optional
from uuid import UUID, uuid4

from app.features.expenses.exceptions import ExpenseNotFoundError
from app.features.expenses.models import Expense
from app.features.expenses.repository import ExpenseRepository
from app.features.expenses.schemas import ExpenseCreate
from app.features.expenses.service import ExpenseService


# ── Fake repository (in-memory) ───────────────────────────────────────────────

class FakeExpenseRepository(ExpenseRepository):
    def __init__(self):
        self._store: dict[UUID, Expense] = {}

    def create(self, expense: Expense) -> Expense:
        self._store[expense.id] = expense
        return expense

    def get_by_id(self, expense_id: UUID) -> Optional[Expense]:
        return self._store.get(expense_id)

    def list(self, category, start_date, end_date, offset, limit):
        items = list(self._store.values())
        if category:
            items = [e for e in items if e.category == category]
        if start_date:
            items = [e for e in items if e.date >= start_date]
        if end_date:
            items = [e for e in items if e.date <= end_date]
        return items[offset: offset + limit], len(items)

    def delete(self, expense_id: UUID) -> bool:
        if expense_id in self._store:
            del self._store[expense_id]
            return True
        return False

    def list_by_month(self, month: int, year: int) -> list[Expense]:
        return [
            e for e in self._store.values()
            if e.date.month == month and e.date.year == year
        ]


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def service():
    return ExpenseService(FakeExpenseRepository())


def make_payload(**overrides) -> ExpenseCreate:
    defaults = dict(
        title="Lunch",
        amount=12.50,
        category="Food",
        date=date(2024, 3, 15),
        description=None,
    )
    return ExpenseCreate(**{**defaults, **overrides})


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_create_expense_returns_response(service):
    result = service.create_expense(make_payload())
    assert result.title == "Lunch"
    assert result.amount == 12.50
    assert result.id is not None


def test_get_expense_found(service):
    created = service.create_expense(make_payload())
    fetched = service.get_expense(created.id)
    assert fetched.id == created.id


def test_get_expense_not_found_raises(service):
    with pytest.raises(ExpenseNotFoundError):
        service.get_expense(uuid4())


def test_delete_expense(service):
    created = service.create_expense(make_payload())
    service.delete_expense(created.id)
    with pytest.raises(ExpenseNotFoundError):
        service.get_expense(created.id)


def test_delete_nonexistent_raises(service):
    with pytest.raises(ExpenseNotFoundError):
        service.delete_expense(uuid4())


def test_list_expenses_pagination(service):
    for i in range(5):
        service.create_expense(make_payload(title=f"Expense {i}"))
    result = service.list_expenses(None, None, None, page=1, page_size=3)
    assert len(result.items) == 3
    assert result.total == 5


def test_list_expenses_filter_by_category(service):
    service.create_expense(make_payload(category="Food"))
    service.create_expense(make_payload(category="Travel"))
    result = service.list_expenses("Food", None, None, page=1, page_size=10)
    assert all(e.category == "Food" for e in result.items)


def test_summary_totals_and_breakdown(service):
    service.create_expense(make_payload(amount=30.0, category="Food",   date=date(2024, 3, 1)))
    service.create_expense(make_payload(amount=20.0, category="Food",   date=date(2024, 3, 10)))
    service.create_expense(make_payload(amount=50.0, category="Travel", date=date(2024, 3, 5)))
    # Different month — should NOT be included
    service.create_expense(make_payload(amount=99.0, category="Food",   date=date(2024, 4, 1)))

    summary = service.get_summary(month=3, year=2024)

    assert summary.total_spending == 100.0
    assert len(summary.breakdown) == 2

    food = next(b for b in summary.breakdown if b.category == "Food")
    assert food.total == 50.0
    assert food.count == 2

    travel = next(b for b in summary.breakdown if b.category == "Travel")
    assert travel.total == 50.0
    assert travel.count == 1


def test_summary_empty_month(service):
    summary = service.get_summary(month=1, year=2020)
    assert summary.total_spending == 0.0
    assert summary.breakdown == []