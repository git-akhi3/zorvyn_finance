# Zorvyn Finance API

> A production-structured finance dashboard backend — built with Django, DRF, and PostgreSQL.
> Role-based access control, aggregated analytics, soft-delete audit trail, and JWT auth.


[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.x-092E20?style=flat&logo=django&logoColor=white)](https://djangoproject.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-4169E1?style=flat&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Railway](https://img.shields.io/badge/Deployed-Railway-0B0D0E?style=flat&logo=railway&logoColor=white)](https://railway.app)

**Live API:** `https://your-railway-url.railway.app/api/`
**Swagger Docs:** `https://your-railway-url.railway.app/api/docs/`

> Login with the test credentials below and hit Authorize in Swagger to explore all endpoints interactively.

---

## What Makes This Different

Most assessment backends are CRUD wrappers with JWT bolted on.
This one is built the way a real backend engineer would structure a
service that needs to scale.

- **Three-layer architecture** — views own HTTP only, services own
  business logic, serializers own validation. Every layer is
  independently testable.
- **Normalized role system** — roles live in a dedicated table with
  a UserRole mapping, not a field on the user model. Auditable,
  extensible, and protected from accidental deletion via
  `on_delete=PROTECT`.
- **Financial-grade data handling** — `DecimalField` everywhere,
  no floats. Auto-generated reference numbers (`TXN-{date}-{suffix}`)
  with uniqueness guaranteed across soft-deleted records.
- **Soft delete by default** — no record is ever hard deleted.
  `ActiveManager` filters deleted records transparently so no
  query in the codebase ever accidentally surfaces them.
- **Dashboard APIs built for a real frontend** — four independent
  aggregation endpoints so widgets load and fail independently,
  not one God endpoint that runs six queries on every call.

---

## Live Test Credentials

| Role     | Email                   | Password      |
|----------|-------------------------|---------------|
| Admin    | admin@zorvyn.com        | Admin@1234    |
| Analyst  | analyst@zorvyn.com      | Analyst@1234  |
| Viewer   | viewer@zorvyn.com       | Viewer@1234   |

**How to use Swagger:**
1. Open `/api/docs/`
2. `POST /api/accounts/login/` with any credential above
3. Copy the `access` token from the response
4. Click **Authorize** → enter `Bearer <token>`
5. All protected endpoints are now unlocked

---

## Architecture
zorvyn_finance/
├── config/                     # Settings, URLs, WSGI
│   └── settings/
│       ├── base.py             # Shared config
│       └── local.py            # Dev overrides
├── apps/
│   ├── core/                   # Shared infrastructure
│   │   ├── models.py           # BaseModel: UUID pk, timestamps, soft delete
│   │   ├── exceptions.py       # Typed DRF exception classes
│   │   ├── response.py         # APIResponse: uniform response shape
│   │   └── pagination.py       # Shared pagination utility
│   ├── accounts/               # Identity and access
│   │   ├── models/             # User · Role · UserRole
│   │   ├── services/           # AuthService · UserService
│   │   ├── serializers/        # Per-concern serializers
│   │   ├── views/              # Auth · Users · Roles
│   │   └── permissions.py      # IsAdmin · IsAnalystOrAbove · IsViewerOrAbove
│   └── records/                # Financial data and analytics
│       ├── models/             # FinancialRecord
│       ├── services/           # RecordService · DashboardService
│       ├── serializers/        # Record · Dashboard
│       ├── views/              # CRUD · Dashboard
│       └── filters.py          # django-filter declarative layer
└── tests/
├── conftest.py             # Fixtures and factories
├── test_accounts.py        # Auth + role access tests
└── test_records.py         # CRUD + guard + soft delete tests

### Request Flow
HTTP Request
│
▼
View (HTTP in/out only)
│
├── Serializer (validate input)
│
▼
Service (business logic)
│
▼
Model / ORM
│
▼
APIResponse (uniform shape)
│
▼
HTTP Response

---

## Features

### Identity and Access Control

- JWT authentication via SimpleJWT (access + refresh tokens)
- Three roles: **Viewer**, **Analyst**, **Admin** — stored in a
  normalized `roles` table, mapped via `user_roles`
- Method-level permission enforcement — same endpoint,
  different permissions per HTTP verb
- Admin cannot deactivate their own account — enforced in the
  service layer, not the view

### Financial Records

- Full CRUD with soft delete — deleted records are never lost
- Auto-generated reference numbers: `TXN-20240401-X7K2`
- Immutable completed/cancelled records — business rule enforced
  at the service layer, returns a typed exception
- `created_by` tracked on every record with `on_delete=PROTECT`
- DB indexes on `date`, `type`, `category`, `status`,
  `reference_number` for query performance

### Filtering and Search
GET /api/records/?type=income&category=salaries
GET /api/records/?date_from=2024-01-01&date_to=2024-03-31
GET /api/records/?status=pending&ordering=-amount
GET /api/records/?search=TXN-20240401
GET /api/records/?page=2

### Dashboard Analytics

Four independent aggregation endpoints — each maps to a
frontend widget:

| Endpoint                          | Role Required     | Returns                                    |
|-----------------------------------|-------------------|--------------------------------------------|
| `/dashboard/summary/`             | Analyst, Admin    | Totals, net balance, month-over-month %    |
| `/dashboard/trends/`              | Analyst, Admin    | Monthly (12 months) + daily (this month)   |
| `/dashboard/categories/`          | Analyst, Admin    | Ranked categories with % share             |
| `/dashboard/activity/`            | Analyst, Admin    | Last 10 records                            |

### Rate Limiting (per endpoint group)

| Scope             | Read      | Write     |
|-------------------|-----------|-----------|
| Auth (register)   | —         | 5/min     |
| Auth (login)      | —         | 10/min    |
| Users             | 60/min    | 30/min    |
| Records           | 120/min   | 60/min    |
| Dashboard         | 60/min    | —         |

All rate limits are configurable via environment variables.
No code change needed to tune for production traffic.

---

## Role Access Matrix

| Action                     | Viewer | Analyst | Admin |
|----------------------------|--------|---------|-------|
| View own profile           | ✓      | ✓       | ✓     |
| View records               | ✓      | ✓       | ✓     |
| Filter and search records  | ✓      | ✓       | ✓     |
| Create records             | ✗      | ✗       | ✓     |
| Update records             | ✗      | ✗       | ✓     |
| Delete records             | ✗      | ✗       | ✓     |
| View dashboard             | ✗      | ✓       | ✓     |
| Manage users               | ✗      | ✗       | ✓     |
| View available roles       | ✗      | ✗       | ✓     |

---

## API Reference

### Auth
```http
POST /api/accounts/register/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepass123",
  "first_name": "Arjun",
  "last_name": "Mehta"
}
```
```json
{
  "status": "success",
  "message": "Account created successfully.",
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "role": "viewer"
    },
    "tokens": {
      "access": "eyJ...",
      "refresh": "eyJ..."
    }
  }
}
```

---
```http
POST /api/accounts/login/
Content-Type: application/json

{
  "email": "admin@zorvyn.com",
  "password": "Admin@1234"
}
```

### Records
```http
POST /api/records/
Authorization: Bearer <token>
Content-Type: application/json

{
  "amount": "75000.00",
  "type": "income",
  "category": "Client Payment",
  "date": "2024-04-01",
  "currency": "INR",
  "status": "completed",
  "notes": "Q1 retainer from Infosys"
}
```
```json
{
  "status": "success",
  "message": "Financial record created successfully.",
  "data": {
    "id": "uuid",
    "reference_number": "TXN-20240401-X7K2",
    "amount": "75000.00",
    "type": "income",
    "category": "Client Payment",
    "date": "2024-04-01",
    "currency": "INR",
    "status": "completed",
    "created_by": {
      "id": "uuid",
      "email": "admin@zorvyn.com"
    },
    "created_at": "2024-04-01T10:30:00Z"
  }
}
```

### Dashboard Summary
```http
GET /api/records/dashboard/summary/
Authorization: Bearer <analyst_or_admin_token>
```
```json
{
  "status": "success",
  "message": "Dashboard summary retrieved successfully.",
  "data": {
    "total_income": "824500.00",
    "total_expense": "391800.00",
    "net_balance": "432700.00",
    "period_comparison": {
      "current_month": {
        "income": "155000.00",
        "expense": "87200.00"
      },
      "last_month": {
        "income": "132000.00",
        "expense": "91500.00"
      },
      "income_change": "+17.4%",
      "expense_change": "-4.7%"
    }
  }
}
```

### Error Response Shape

Every error in the system — validation, auth, not found,
server error — returns the same shape:
```json
{
  "status": "error",
  "message": "Completed or cancelled records cannot be modified.",
  "details": {}
}
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 14+

### Local Setup
```bash
# 1. Clone
git clone https://github.com/your-username/zorvyn-finance.git
cd zorvyn-finance

# 2. Virtual environment
python -m venv venv
source venv/bin/activate        

# 3. Dependencies
pip install -r requirements.txt

# 4. Environment
cp .env.example .env
# Open .env and fill in DB_USER, DB_PASSWORD, SECRET_KEY

# 5. Database
python manage.py migrate

# 6. Seed roles (required before any user can register)
python manage.py seed_roles

# 7. Seed realistic test data (30 records, 3 users)
python manage.py seed_data

# 8. Run
python manage.py runserver
```

**Swagger UI:** http://127.0.0.1:8000/api/docs/

### Environment Variables
```env
SECRET_KEY=your-secret-key
DEBUG=True

DB_NAME=assessment
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432

# Rate limits (all configurable, no code change needed)
THROTTLE_AUTH_REGISTER=5/min
THROTTLE_AUTH_LOGIN=10/min
THROTTLE_USERS_READ=60/min
THROTTLE_USERS_WRITE=30/min
THROTTLE_RECORDS_READ=120/min
THROTTLE_RECORDS_WRITE=60/min
THROTTLE_DASHBOARD_READ=60/min
```

### Run Tests
```bash
pytest
```

---

## Design Decisions

**UUID primary keys over sequential integers**
Sequential IDs expose record counts to API consumers — a
basic information leak. For a finance system, knowing there
are 1,247 transactions is sensitive. UUIDs are opaque, safe
to expose in URLs, and consistent across environments.

**Soft delete via `ActiveManager`**
Financial records should never be permanently destroyed.
`ActiveManager` excludes deleted records from every default
query transparently — no filter needs to be remembered
at the call site. Hard delete is structurally impossible
in normal application flow.

**`Decimal` everywhere for monetary values**
IEEE 754 floating point is unsuitable for financial arithmetic.
`0.1 + 0.2 != 0.3`. Every monetary value in this system uses
`DecimalField` with explicit precision and Python's `Decimal`
type throughout the service layer.

**`on_delete=PROTECT` on financial records**
A record's creator is part of its audit trail. Cascade
deletion would silently destroy that trail. `PROTECT` forces
an explicit decision: deactivate users, never delete them.

**Roles in a mapping table, not a field**
A `role` CharField on User is simpler but not normalized.
A `UserRole` mapping table keeps assignment auditable, allows
future extension to multiple roles, and prevents role deletion
while users hold it via `on_delete=PROTECT`.

**Four dashboard endpoints over one**
A single endpoint running all aggregations on every call is a
performance problem at scale. Four endpoints let each frontend
widget load independently, fail independently, and be cached
independently in future without any structural change.

---

## Assumptions

- One active role per user enforced via `OneToOneField`
  on `UserRole`. Multiple roles per user would require
  a schema change by design, not accident.
- Roles are fixed system constants seeded at deployment.
  Runtime role creation is not supported — new roles
  imply new permission logic which requires a code change.
- All amounts stored in the record's stated currency.
  No conversion is performed — this is a recording system,
  not a trading system.
- Completed and cancelled records are immutable by design.
  Financial records should be append-only once finalised.
- Viewers are read-only consumers. Record creation is an
  admin operation — not an end-user operation.

---

## What I Would Add With More Time

**Audit log**
A dedicated `AuditLog` model capturing every state change —
who changed what, from what value, at what time. Non-negotiable
for a production finance system and the natural next model
after `UserRole`.

**Idempotency keys on record creation**
Financial record creation should accept an `Idempotency-Key`
header so network retries don't create duplicate records.
Implemented this pattern in a previous project using a
request hash stored with a short TTL.

**Refresh token blacklisting**
Currently logout is client-side. Server-side blacklisting
of refresh tokens on logout would close the window between
token expiry and intentional logout.

**Dashboard caching**
Aggregation queries are expensive at scale. A 60-second
cache on the four dashboard endpoints via `django-cache`
would cut DB load significantly with no meaningful impact
on data freshness for a dashboard use case.

**Role-tiered rate limiting**
Current throttling is endpoint-scoped. A viewer hammering
read endpoints should be throttled differently than an admin
performing writes. DRF's throttle classes support this with
a custom `get_cache_key` implementation.

---

## Tech Stack

| Layer          | Choice                   | Reason                                               |
|----------------|--------------------------|------------------------------------------------------|
| Framework      | Django + DRF             | Mature ORM, built-in permission layer, serializers   |
| Database       | PostgreSQL               | Aggregation functions for dashboard, query planner   |
| Auth           | SimpleJWT                | Stateless, standard, refresh token support           |
| Filtering      | django-filter            | Declarative, composable, zero boilerplate            |
| API Docs       | drf-spectacular          | Auto-generated OpenAPI from existing code            |
| Deployment     | Railway                  | Zero-config PostgreSQL + Django hosting              |
| Testing        | pytest-django + factory-boy | Fixtures, factories, no boilerplate test setup    |