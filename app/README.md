# Expense Tracker API

A production-grade REST API built with **FastAPI** + **Supabase**, following clean architecture principles.

## Setup

```bash
# 1. Clone and install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your Supabase URL and key

# 3. Create the expenses table in Supabase SQL editor:
```

```sql
CREATE TABLE expenses (
  id          UUID PRIMARY KEY,
  title       TEXT NOT NULL,
  amount      NUMERIC(10, 2) NOT NULL,
  category    TEXT NOT NULL,
  date        DATE NOT NULL,
  description TEXT
);
```

```bash
# 4. Run the server
uvicorn app.main:app --reload
```

## Running Tests

```bash
pytest tests/ -v
```

## Architecture Decisions

| Decision                             | Rationale                                                          |
| ------------------------------------ | ------------------------------------------------------------------ |
| Abstract `ExpenseRepository`         | Decouples service from Supabase; enables FakeRepository in tests   |
| Domain `Expense` model               | Separates internal representation from API-facing Pydantic schemas |
| Service raises domain exceptions     | Keeps HTTP concerns out of business logic                          |
| `/summary` registered before `/{id}` | Prevents FastAPI from treating "summary" as a UUID path param      |
| `lru_cache` on Supabase client       | Creates a single client instance for the app lifetime              |

## API Endpoints

| Method   | Path                | Description                    |
| -------- | ------------------- | ------------------------------ |
| `POST`   | `/expenses`         | Create an expense              |
| `GET`    | `/expenses`         | List with filters & pagination |
| `GET`    | `/expenses/{id}`    | Get by ID                      |
| `DELETE` | `/expenses/{id}`    | Delete by ID                   |
| `GET`    | `/expenses/summary` | Monthly summary & breakdown    |
