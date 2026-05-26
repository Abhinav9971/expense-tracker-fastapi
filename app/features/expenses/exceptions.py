class ExpenseNotFoundError(Exception):
    """Raised when an expense with the given ID does not exist."""

    def __init__(self, expense_id: str):
        self.expense_id = expense_id
        super().__init__(f"Expense with id '{expense_id}' not found.")