from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.features.expenses.exceptions import ExpenseNotFoundError
from app.features.expenses.schemas import (
    ExpenseCreate,
    ExpenseResponse,
    ExpenseSummary,
    PaginatedExpenses,
)
from app.features.expenses.service import ExpenseService

router = APIRouter(prefix="/expenses", tags=["expenses"])


def get_service() -> ExpenseService:
    """Overridden in dependencies.py via app.dependency_overrides."""
    raise NotImplementedError


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    payload: ExpenseCreate,
    service: ExpenseService = Depends(get_service),
):
    return service.create_expense(payload)


@router.get("/summary", response_model=ExpenseSummary)
def get_summary(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2000),
    service: ExpenseService = Depends(get_service),
):
    # NOTE: /summary must be registered BEFORE /{id} to avoid route conflict
    return service.get_summary(month=month, year=year)


@router.get("", response_model=PaginatedExpenses)
def list_expenses(
    category: Optional[str] = Query(default=None),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service: ExpenseService = Depends(get_service),
):
    return service.list_expenses(
        category=category,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(
    expense_id: UUID,
    service: ExpenseService = Depends(get_service),
):
    try:
        return service.get_expense(expense_id)
    except ExpenseNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: UUID,
    service: ExpenseService = Depends(get_service),
):
    try:
        service.delete_expense(expense_id)
    except ExpenseNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))