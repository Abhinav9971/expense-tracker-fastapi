from collections import defaultdict
from datetime import date
from typing import Optional
from uuid import UUID, uuid4

from app.features.expenses.exceptions import ExpenseNotFoundError
from app.features.expenses.models import Expense
from app.features.expenses.repository import ExpenseRepository
from app.features.expenses.schemas import (
    CategoryBreakdown,
    ExpenseCreate,
    ExpenseResponse,
    ExpenseSummary,
    PaginatedExpenses,
)


def _expense_to_response(expense: Expense) -> ExpenseResponse:
    return ExpenseResponse(
        id=expense.id,
        title=expense.title,
        amount=expense.amount,
        category=expense.category,
        date=expense.date,
        description=expense.description,
    )


class ExpenseService:
    def __init__(self, repository: ExpenseRepository):
        self._repo = repository

    # ── Create ────────────────────────────────────────────────────────────────

    def create_expense(self, data: ExpenseCreate) -> ExpenseResponse:
        expense = Expense(
            id=uuid4(),
            title=data.title,
            amount=data.amount,
            category=data.category,
            date=data.date,
            description=data.description,
        )
        saved = self._repo.create(expense)
        return _expense_to_response(saved)

    # ── Get by ID ─────────────────────────────────────────────────────────────

    def get_expense(self, expense_id: UUID) -> ExpenseResponse:
        expense = self._repo.get_by_id(expense_id)
        if expense is None:
            raise ExpenseNotFoundError(str(expense_id))
        return _expense_to_response(expense)

    # ── List (paginated + filtered) ───────────────────────────────────────────

    def list_expenses(
        self,
        category: Optional[str],
        start_date: Optional[date],
        end_date: Optional[date],
        page: int,
        page_size: int,
    ) -> PaginatedExpenses:
        offset = (page - 1) * page_size
        items, total = self._repo.list(
            category=category,
            start_date=start_date,
            end_date=end_date,
            offset=offset,
            limit=page_size,
        )
        return PaginatedExpenses(
            total=total,
            page=page,
            page_size=page_size,
            items=[_expense_to_response(e) for e in items],
        )

    # ── Delete ────────────────────────────────────────────────────────────────

    def delete_expense(self, expense_id: UUID) -> None:
        deleted = self._repo.delete(expense_id)
        if not deleted:
            raise ExpenseNotFoundError(str(expense_id))

    # ── Summary (core business logic) ─────────────────────────────────────────

    def get_summary(self, month: int, year: int) -> ExpenseSummary:
        expenses = self._repo.list_by_month(month=month, year=year)

        total_spending = sum(e.amount for e in expenses)

        # Aggregate per category
        category_totals: dict[str, float] = defaultdict(float)
        category_counts: dict[str, int] = defaultdict(int)

        for expense in expenses:
            category_totals[expense.category] += expense.amount
            category_counts[expense.category] += 1

        breakdown = [
            CategoryBreakdown(
                category=cat,
                total=round(category_totals[cat], 2),
                count=category_counts[cat],
            )
            for cat in sorted(category_totals)
        ]

        return ExpenseSummary(
            month=month,
            year=year,
            total_spending=round(total_spending, 2),
            breakdown=breakdown,
        )