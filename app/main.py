from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.dependencies import get_expense_service
from app.features.expenses.exceptions import ExpenseNotFoundError
from app.features.expenses.router import get_service, router as expense_router

app = FastAPI(
    title="Expense Tracker API",
    description="Clean-architecture expense tracker built with FastAPI + Supabase.",
    version="1.0.0",
)

# Wire the real service implementation into the router
app.dependency_overrides[get_service] = get_expense_service

# Global exception handler — translates domain errors to HTTP responses
@app.exception_handler(ExpenseNotFoundError)
async def not_found_handler(request: Request, exc: ExpenseNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})

app.include_router(expense_router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}