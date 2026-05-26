from abc import ABC, abstractmethod
from calendar import monthrange
from datetime import date
from typing import Optional, List, Tuple
from uuid import UUID

from supabase import Client

from app.features.expenses.models import Expense


class ExpenseRepository(ABC):

    @abstractmethod
    def create(self, expense: Expense) -> Expense:
        ...

    @abstractmethod
    def get_by_id(self, expense_id: UUID) -> Optional[Expense]:
        ...

    @abstractmethod
    def list(
        self,
        category: Optional[str],
        start_date: Optional[date],
        end_date: Optional[date],
        offset: int,
        limit: int,
    ) -> Tuple[List[Expense], int]:
        ...

    @abstractmethod
    def delete(self, expense_id: UUID) -> bool:
        ...

    @abstractmethod
    def list_by_month(self, month: int, year: int) -> List[Expense]:
        ...


def _row_to_expense(row: dict) -> Expense:
    return Expense(
        id=UUID(row["id"]),
        title=row["title"],
        amount=float(row["amount"]),
        category=row["category"],
        date=date.fromisoformat(row["date"]),
        description=row.get("description"),
    )


class SupabaseExpenseRepository(ExpenseRepository):
    TABLE = "expenses"

    def __init__(self, client: Client):
        self._client = client

    def create(self, expense: Expense) -> Expense:
        payload = {
            "id": str(expense.id),
            "title": expense.title,
            "amount": expense.amount,
            "category": expense.category,
            "date": expense.date.isoformat(),
            "description": expense.description,
        }
        result = self._client.table(self.TABLE).insert(payload).execute()
        return _row_to_expense(result.data[0])

    def get_by_id(self, expense_id: UUID) -> Optional[Expense]:
        result = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("id", str(expense_id))
            .execute()
        )
        if not result.data:
            return None
        return _row_to_expense(result.data[0])

    def list(
        self,
        category: Optional[str],
        start_date: Optional[date],
        end_date: Optional[date],
        offset: int,
        limit: int,
    ) -> Tuple[List[Expense], int]:
        query = self._client.table(self.TABLE).select("*", count="exact")

        if category:
            query = query.eq("category", category)
        if start_date:
            query = query.gte("date", start_date.isoformat())
        if end_date:
            query = query.lte("date", end_date.isoformat())

        result = query.range(offset, offset + limit - 1).execute()
        items = [_row_to_expense(row) for row in result.data]
        total = result.count or 0
        return items, total

    def delete(self, expense_id: UUID) -> bool:
        result = (
            self._client.table(self.TABLE)
            .delete()
            .eq("id", str(expense_id))
            .execute()
        )
        return len(result.data) > 0

    def list_by_month(self, month: int, year: int) -> List[Expense]:
        first_day = date(year, month, 1)
        last_day = date(year, month, monthrange(year, month)[1])

        result = (
            self._client.table(self.TABLE)
            .select("*")
            .gte("date", first_day.isoformat())
            .lte("date", last_day.isoformat())
            .execute()
        )
        return [_row_to_expense(row) for row in result.data]