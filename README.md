# Zorvyn Finance API

> **Finance dashboard backend built for production, submitted as an assessment.**
> Role-based access control, aggregated analytics, normalized role system, soft-delete audit trail — structured the way a real service is built, not the way tutorials teach.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.x-092E20?style=flat&logo=django&logoColor=white)](https://djangoproject.com)
[![DRF](https://img.shields.io/badge/DRF-3.x-A30000?style=flat)](https://www.django-rest-framework.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-4169E1?style=flat&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Deployed on Railway](https://img.shields.io/badge/Deployed-Railway-0B0D0E?style=flat&logo=railway&logoColor=white)](https://railway.app)
[![Tests](https://img.shields.io/badge/Tests-pytest-green?style=flat&logo=pytest&logoColor=white)](https://pytest.org)

**🔗 Live API:** `https://your-railway-url.railway.app/api/`  
**📖 Swagger Docs:** `https://your-railway-url.railway.app/api/docs/`

---

## Table of Contents

- [Why This Stands Out](#why-this-stands-out)
- [Live Demo](#live-demo)
- [Architecture](#architecture)
- [Features](#features)
- [Role Access Matrix](#role-access-matrix)
- [API Reference](#api-reference)
- [Rate Limiting](#rate-limiting)
- [Getting Started](#getting-started)
- [Running Tests](#running-tests)
- [Design Decisions](#design-decisions)
- [Assumptions](#assumptions)
- [What I Would Add With More Time](#what-i-would-add-with-more-time)
- [Tech Stack](#tech-stack)

---

## Why This Stands Out

Most assessment backends are CRUD wrappers with JWT bolted on.
This one is deliberately different in five ways:

**1. Three-layer architecture — enforced, not aspirational**  
Views own HTTP only. Services own all business logic. Serializers own validation and representation only. There is no business logic in a view, and no HTTP handling in a service. Every rule is independently testable without spinning up HTTP.

**2. Roles are a database concern, not a model field**  
A `role` CharField on `User` is the obvious choice — and the wrong one for a finance system. Roles live in a dedicated `roles` table, mapped via `user_roles`. This makes role assignment auditable, protects roles from accidental deletion via `on_delete=PROTECT`, and keeps the schema normalized.

**3. Financial-grade data handling throughout**  
`DecimalField` and Python's `Decimal` type everywhere — no floats. Auto-generated reference numbers (`TXN-20240401-X7K2`) with uniqueness checked against soft-deleted records. `on_delete=PROTECT` on `created_by` — financial audit trails are never silently destroyed.

**4. Soft delete is structural, not optional**  
Every model inherits from `BaseModel` which attaches `ActiveManager` as the default manager. Deleted records are invisible to every query by default — no filter needs to be remembered anywhere in the codebase. Hard delete is structurally impossible in normal application flow.

**5. Dashboard APIs designed for a real frontend**  
Four independent aggregation endpoints instead of one God endpoint. Each widget loads, fails, and can be cached independently. The alternative — one endpoint running six aggregations on every call — is a performance problem waiting to happen.

---

## Live Demo

| Role     | Email                  | Password      |
|----------|------------------------|---------------|
| Admin    | admin@zorvyn.com       | Admin@1234    |
| Analyst  | analyst@zorvyn.com     | Analyst@1234  |
| Viewer   | viewer@zorvyn.com      | Viewer@1234   |

**How to test via Swagger:**
1. Open `/api/docs/`
2. `POST /api/accounts/login/` with any credential above
3. Copy the `access` token from the response
4. Click **Authorize →** enter `Bearer <token>`
5. All protected endpoints are now unlocked — try them with different roles to see access control in action

---

## Architecture

### Project Structure

```
zorvyn_finance/
├── config/
│   └── settings/
│       ├── base.py             # Shared configuration
│       └── local.py            # Dev overrides
│
├── apps/
│   ├── core/                   # Shared infrastructure — no business logic
│   │   ├── models.py           # BaseModel: UUID pk, timestamps, soft delete
│   │   ├── exceptions.py       # Typed DRF exception classes (12 types)
│   │   ├── response.py         # APIResponse: enforces uniform response shape
│   │   └── pagination.py       # Shared pagination utility
│   │
│   ├── accounts/               # Identity, authentication, access control
│   │   ├── models/
│   │   │   ├── user.py         # Custom User — email auth, no username
│   │   │   ├── role.py         # Role definitions (viewer/analyst/admin)
│   │   │   └── user_role.py    # UserRole mapping — OneToOne enforces single role
│   │   ├── services/
│   │   │   ├── auth_service.py # Register, login, token generation
│   │   │   └── user_service.py # User listing, filtering, role updates
│   │   ├── serializers/        # auth · user · role (separate files)
│   │   ├── views/              # auth_views · user_views · role_views
│   │   └── permissions.py      # IsAdmin · IsAnalystOrAbove · IsViewerOrAbove
│   │
│   └── records/                # Financial data and dashboard analytics
│       ├── models/
│       │   └── record.py       # FinancialRecord with 6 DB indexes
│       ├── services/
│       │   ├── record_service.py    # CRUD + ref number generation
│       │   └── dashboard_service.py # 4 aggregation methods, pure ORM
│       ├── serializers/        # record · dashboard (separate files)
│       ├── views/              # record_views · dashboard_views
│       └── filters.py          # django-filter declarative filter layer
│
└── tests/
    ├── conftest.py             # Fixtures, factories, seeded roles
    ├── test_accounts.py        # Auth + role access boundary tests
    └── test_records.py         # CRUD + guards + soft delete tests
```

### Request Flow

```
Request
  │
  ├─▶ Permission Class     (role check — fail fast before any logic runs)
  │
  ├─▶ View                 (HTTP in/out only — extract data, return response)
  │
  ├─▶ Serializer           (validate input — raise typed exception on failure)
  │
  ├─▶ Service              (business logic — the only place rules live)
  │
  └─▶ Model / ORM          (data layer — BaseModel handles soft delete transparently)
```

### Response Contract

Every endpoint in the system — success or error — returns the same shape. No exceptions.

```json
{
  "status": "success | error",
  "message": "Human readable string",
  "data": {}
}
```

Errors add a `details` field with structured validation feedback when applicable. This is enforced by `APIResponse` in `core/` — raw `Response()` is never used directly in any view.

---

## Features

### 🔐 Authentication and Identity

- JWT authentication via SimpleJWT — access token (short-lived) + refresh token
- Email-based login — no username field
- Registration auto-assigns viewer role via `UserRole` mapping
- Inactive user login blocked at `403` — distinct from invalid credentials (`401`)
- `MeView` for any authenticated user to fetch their own profile

### 👥 User and Role Management

- Three roles: **Viewer**, **Analyst**, **Admin**
- Roles seeded via management command — `python manage.py seed_roles`
- Admin can update any user's role or active status via `PATCH /api/accounts/users/<id>/`
- Admin cannot deactivate themselves — enforced in `UserService`, not the view
- User list supports filtering by `role` and `is_active` query params
- Paginated user listing

### 📊 Financial Records

- Full CRUD with **soft delete** — no record is ever hard deleted
- Auto-generated reference numbers: `TXN-{YYYYMMDD}-{4-char suffix}`
  — uniqueness checked against all records including soft-deleted
- **Immutable closed records** — completed or cancelled records
  raise a typed exception on any update attempt
- `created_by` tracked on every record — protected from cascade deletion
- DB indexes on `date`, `type`, `category`, `status`, `reference_number`
  — query performance is a design concern, not an afterthought

### 🔍 Filtering, Search and Ordering

```
?type=income                        exact type filter
?category=salaries                  case-insensitive contains
?status=pending                     exact status filter
?date_from=2024-01-01               date range start
?date_to=2024-03-31                 date range end
?search=TXN-20240401                searches category, notes, reference_number
?ordering=-amount                   sort by any field, prefix - for descending
?page=2                             paginated results
```

### 📈 Dashboard Analytics

| Endpoint                            | Returns                                         |
|-------------------------------------|-------------------------------------------------|
| `GET /dashboard/summary/`           | Total income/expense, net balance, MoM % change |
| `GET /dashboard/trends/`            | Monthly trends (12 months) + daily (this month) |
| `GET /dashboard/categories/`        | Ranked categories with % share, split by type   |
| `GET /dashboard/activity/`          | Last 10 records for activity feed               |

All aggregations use pure Django ORM — `TruncMonth`, `TruncDay`,
conditional `Sum` with `Q` objects, `Decimal` arithmetic throughout.
No raw SQL anywhere.

Month-over-month comparison example:

```json
"period_comparison": {
  "current_month": { "income": "155000.00", "expense": "87200.00" },
  "last_month":    { "income": "132000.00", "expense": "91500.00" },
  "income_change":  "+17.4%",
  "expense_change": "-4.7%"
}
```

---

## Role Access Matrix

| Action                        | Viewer | Analyst | Admin |
|-------------------------------|:------:|:-------:|:-----:|
| Register / Login              | ✓      | ✓       | ✓     |
| View own profile              | ✓      | ✓       | ✓     |
| List and filter records       | ✓      | ✓       | ✓     |
| View single record            | ✓      | ✓       | ✓     |
| Create records                | ✗      | ✗       | ✓     |
| Update records                | ✗      | ✗       | ✓     |
| Soft delete records           | ✗      | ✗       | ✓     |
| View dashboard summary        | ✗      | ✓       | ✓     |
| View dashboard trends         | ✗      | ✓       | ✓     |
| View category breakdown       | ✗      | ✓       | ✓     |
| View recent activity          | ✗      | ✓       | ✓     |
| List and filter users         | ✗      | ✗       | ✓     |
| Update user role / status     | ✗      | ✗       | ✓     |
| View available roles          | ✗      | ✗       | ✓     |

---

## API Reference

### Register

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
    "user": { "id": "uuid", "email": "user@example.com", "role": "viewer" },
    "tokens": { "access": "eyJ...", "refresh": "eyJ..." }
  }
}
```

### Create Record (Admin only)

```http
POST /api/records/
Authorization: Bearer <admin_token>
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
    "created_by": { "id": "uuid", "email": "admin@zorvyn.com" },
    "created_at": "2024-04-01T10:30:00Z",
    "updated_at": "2024-04-01T10:30:00Z"
  }
}
```

### Error Response (consistent across all endpoints)

```json
{
  "status": "error",
  "message": "Completed or cancelled records cannot be modified.",
  "details": {}
}
```

Attempting to update a completed record returns `400`.  
Attempting the same action as a viewer returns `403`.  
Wrong credentials return `401`. Inactive user returns `403`.  
Every status code is intentional — not defaulted.

---

## Rate Limiting

All limits are environment-configurable — no code change required to tune for production traffic.

| Scope                | Limit      | Env Variable                  |
|----------------------|------------|-------------------------------|
| Auth — Register      | 5 / min    | `THROTTLE_AUTH_REGISTER`      |
| Auth — Login         | 10 / min   | `THROTTLE_AUTH_LOGIN`         |
| Users — Read         | 60 / min   | `THROTTLE_USERS_READ`         |
| Users — Write        | 30 / min   | `THROTTLE_USERS_WRITE`        |
| Records — Read       | 120 / min  | `THROTTLE_RECORDS_READ`       |
| Records — Write      | 60 / min   | `THROTTLE_RECORDS_WRITE`      |
| Dashboard — Read     | 60 / min   | `THROTTLE_DASHBOARD_READ`     |

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
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env — fill in SECRET_KEY, DB_USER, DB_PASSWORD

# 5. Run migrations
python manage.py migrate

# 6. Seed roles (required before any user can register)
python manage.py seed_roles

# 7. Seed test data — 3 users, 30 realistic financial records
python manage.py seed_data

# 8. Start server
python manage.py runserver
```

**Swagger UI →** http://127.0.0.1:8000/api/docs/  
**ReDoc →** http://127.0.0.1:8000/api/redoc/

### Environment Variables

```env
SECRET_KEY=your-secret-key
DEBUG=True

DB_NAME=assessment
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432

THROTTLE_AUTH_REGISTER=5/min
THROTTLE_AUTH_LOGIN=10/min
THROTTLE_USERS_READ=60/min
THROTTLE_USERS_WRITE=30/min
THROTTLE_RECORDS_READ=120/min
THROTTLE_RECORDS_WRITE=60/min
THROTTLE_DASHBOARD_READ=60/min
```

---

## Running Tests

```bash
pytest
```

Tests use `pytest-django` and `factory-boy`. No fixtures require
manual setup — `conftest.py` seeds roles automatically via
an `autouse` fixture before every test.

### Test Coverage

| Area                               | What's tested                                              |
|------------------------------------|------------------------------------------------------------|
| Registration                       | Success, duplicate email, short password, missing fields   |
| Login                              | Valid credentials, wrong password, inactive user           |
| User management                    | Admin access, viewer/analyst blocked, self-deactivation guard |
| Record creation                    | Success, zero/negative amount, missing fields, role guards |
| Record listing                     | Soft delete exclusion, type filter, unauthenticated block  |
| Record update                      | Pending editable, completed/cancelled immutable, role guards |
| Soft delete                        | Record marked deleted, excluded from list, 404 on re-fetch |

---

## Design Decisions

**UUIDs over sequential integer PKs**  
Sequential IDs expose record counts to API consumers.
For a finance system, knowing there are 1,247 transactions
is a meaningful information leak. UUIDs are opaque and safe
to expose in URLs and responses.

**`Decimal` for all monetary values**  
IEEE 754 floating point cannot represent 0.1 exactly.
`0.1 + 0.2 != 0.3` in Python float arithmetic.
Every amount in this system uses `DecimalField` and
Python's `Decimal` type end-to-end. This is non-negotiable
for any financial application.

**`on_delete=PROTECT` on `created_by`**  
A record's creator is part of its audit trail.
Cascade deletion would silently destroy that trail.
`PROTECT` forces the correct decision — deactivate users,
never delete them. This is enforced at the database level,
not just the application level.

**Roles in a mapping table**  
A `role` CharField on `User` would have been 10 lines simpler.
It was the wrong choice because it makes role changes
unauditable, doesn't prevent role deletion, and can't
extend to multiple roles without a schema migration.
The `UserRole` table costs one join and buys all of this.

**Immutable completed/cancelled records**  
Financial records should be append-only once finalised.
Allowing edits to completed records creates reconciliation
problems — a record's state at the time of finalisation
should be its permanent state. This is enforced in
`RecordService.update_record`, not as a serializer quirk.

**Four dashboard endpoints over one**  
One endpoint running all aggregations simultaneously couples
frontend widget loading to the slowest query in the set.
Four endpoints let widgets load independently, fail gracefully
in isolation, and be cached at different TTLs in future
without any structural change.

---

## Assumptions

- **One role per user** — enforced via `OneToOneField` on `UserRole`.
  Multiple roles per user is a schema change by design, not accident.
- **Roles are fixed system constants** — seeded at deployment,
  not created at runtime. A new role implies new permission logic,
  which requires a code change.
- **Amounts are stored in stated currency** — no conversion is
  performed. This is a recording system, not a trading system.
- **Completed and cancelled records are immutable** — this is
  intentional behaviour, not a missing feature.
- **Record creation is an admin operation** — viewers and analysts
  are consumers of financial data, not producers of it.

---

## What I Would Add With More Time

**Audit log model**  
A dedicated `AuditLog` recording every state change — who,
what, when, previous value, new value. Non-negotiable for
production fintech. The `BaseModel` pattern makes this
straightforward to add as a signal on `post_save`.

**Idempotency keys on record creation**  
Financial record creation should accept an `Idempotency-Key`
header so network retries don't create duplicate records.
Previously implemented this using a request hash with a
short-TTL cache key.

**Dashboard caching**  
60-second cache on the four dashboard endpoints via
`django-cache`. Would cut DB load significantly with no
meaningful impact on data freshness for a dashboard context.

**Server-side refresh token blacklisting**  
Logout is currently client-side. Server-side blacklisting
closes the window between intentional logout and token expiry.

**Role-tiered rate limiting**  
Current throttling is endpoint-scoped. A viewer making
heavy read requests should be throttled differently than
an admin performing writes. Achievable with a custom
`get_cache_key` on DRF's throttle classes.

---

## Tech Stack

| Layer              | Choice               | Reason                                                   |
|--------------------|----------------------|----------------------------------------------------------|
| Framework          | Django + DRF         | Mature ORM, built-in permission layer, serializer system |
| Database           | PostgreSQL           | Aggregation functions, query planner, `TruncMonth` support |
| Auth               | SimpleJWT            | Stateless, standard, refresh token support               |
| Filtering          | django-filter        | Declarative, composable, zero boilerplate                |
| API Docs           | drf-spectacular      | Auto-generated OpenAPI from existing code                |
| Deployment         | Railway              | Zero-config PostgreSQL + Django hosting                  |
| Testing            | pytest-django        | Clean fixtures, no unittest boilerplate                  |
| Test Factories     | factory-boy          | Realistic model instances without manual setup           |
