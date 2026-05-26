from functools import lru_cache

from fastapi import Depends
from supabase import Client

from app.database.supabase_client import create_supabase_client
from app.features.expenses.repository import SupabaseExpenseRepository
from app.features.expenses.service import ExpenseService


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    return create_supabase_client()


def get_expense_repository(
    client: Client = Depends(get_supabase_client),
) -> SupabaseExpenseRepository:
    return SupabaseExpenseRepository(client)


def get_expense_service(
    repo: SupabaseExpenseRepository = Depends(get_expense_repository),
) -> ExpenseService:
    return ExpenseService(repo)