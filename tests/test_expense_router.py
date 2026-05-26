"""Integration tests for the router layer using TestClient + service mock."""
import pytest
from datetime import date
from unittest.mock import MagicMock
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.dependencies import get_expense_service
from app.features.expenses.exceptions import ExpenseNotFoundError
from app.features.expenses.schemas import (
    CategoryBreakdown,
    ExpenseResponse,
    ExpenseSummary,
    PaginatedExpenses,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_expense_response(**overrides) -> ExpenseResponse:
    defaults = dict(
        id=uuid4(),
        title="Coffee",
        amount=4.5,
        category="Food",
        date=date(2024, 3, 1),
        description=None,
    )
    return ExpenseResponse(**{**defaults, **overrides})


@pytest.fixture
def mock_service():
    return MagicMock()


@pytest.fixture
def client(mock_service):
    app.dependency_overrides[get_expense_service] = lambda: mock_service
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.pop(get_expense_service, None)


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_create_expense_201(client, mock_service):
    expense = make_expense_response()
    mock_service.create_expense.return_value = expense

    resp = client.post("/expenses", json={
        "title": "Coffee",
        "amount": 4.5,
        "category": "Food",
        "date": "2024-03-01",
    })
    assert resp.status_code == 201
    assert resp.json()["title"] == "Coffee"


def test_get_expense_200(client, mock_service):
    expense = make_expense_response()
    mock_service.get_expense.return_value = expense

    resp = client.get(f"/expenses/{expense.id}")
    assert resp.status_code == 200


def test_get_expense_404(client, mock_service):
    mock_service.get_expense.side_effect = ExpenseNotFoundError("abc")

    resp = client.get(f"/expenses/{uuid4()}")
    assert resp.status_code == 404


def test_delete_expense_204(client, mock_service):
    mock_service.delete_expense.return_value = None

    resp = client.delete(f"/expenses/{uuid4()}")
    assert resp.status_code == 204


def test_delete_expense_404(client, mock_service):
    mock_service.delete_expense.side_effect = ExpenseNotFoundError("xyz")

    resp = client.delete(f"/expenses/{uuid4()}")
    assert resp.status_code == 404


def test_list_expenses_200(client, mock_service):
    mock_service.list_expenses.return_value = PaginatedExpenses(
        total=1, page=1, page_size=20,
        items=[make_expense_response()]
    )
    resp = client.get("/expenses")
    assert resp.status_code == 200
    assert resp.json()["total"] == 1


def test_summary_200(client, mock_service):
    mock_service.get_summary.return_value = ExpenseSummary(
        month=3, year=2024, total_spending=100.0,
        breakdown=[CategoryBreakdown(category="Food", total=100.0, count=2)]
    )
    resp = client.get("/expenses/summary?month=3&year=2024")
    assert resp.status_code == 200
    assert resp.json()["total_spending"] == 100.0