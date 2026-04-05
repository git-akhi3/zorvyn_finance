# Zorvyn Finance — Backend Assessment

A finance dashboard backend built with Django, Django REST Framework,
and PostgreSQL. Implements user role management, financial record
tracking, dashboard analytics, and role-based access control.

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [API Reference](#api-reference)
- [Role Access Matrix](#role-access-matrix)
- [Design Decisions](#design-decisions)
- [Assumptions](#assumptions)
- [What I Would Add With More Time](#what-i-would-add-with-more-time)

---

## Tech Stack

| Layer            | Choice                        | Reason                                              |
|------------------|-------------------------------|-----------------------------------------------------|
| Framework        | Django + DRF                  | Mature, battle-tested for data-heavy backends       |
| Database         | PostgreSQL                    | Window functions and aggregations for dashboard APIs|
| Auth             | SimpleJWT                     | Stateless, standard for API-first backends          |
| Filtering        | django-filter                 | Clean declarative filter layer                      |
| API Docs         | drf-spectacular               | Auto-generated OpenAPI from existing code           |

---

## Architecture
zorvyn_finance/
├── config/                  # Project settings, URLs, WSGI
├── apps/
│   ├── core/                # Shared base classes, exceptions, response wrapper
│   │   ├── models.py        # BaseModel — UUID pk, timestamps, soft delete
│   │   ├── exceptions.py    # Typed exception classes
│   │   ├── response.py      # APIResponse wrapper
│   │   └── pagination.py    # Shared pagination utility
│   ├── accounts/            # Users, roles, authentication
│   │   ├── models/          # User, Role, UserRole
│   │   ├── services/        # AuthService, UserService
│   │   ├── serializers/     # Auth, user, role serializers
│   │   ├── views/           # Auth views, user views, role views
│   │   └── permissions.py   # IsAdmin, IsAnalystOrAbove, IsViewerOrAbove
│   └── records/             # Financial records + dashboard
│       ├── models/          # FinancialRecord
│       ├── services/        # RecordService, DashboardService
│       ├── serializers/     # Record + dashboard serializers
│       ├── views/           # Record CRUD + dashboard views
│       └── filters.py       # FinancialRecordFilter
└── tests/
├── test_accounts.py
└── test_records.py

### Key Architectural Decisions

**Three-layer service architecture**
Views handle HTTP only. Services own all business logic.
Serializers handle validation and representation only.
This makes every business rule independently testable
without spinning up HTTP.

**Shared core app**
`apps/core/` owns base classes used across every app.
`BaseModel` gives every model UUID primary keys, timestamps,
and soft delete out of the box. No model in this project
inherits from `models.Model` directly.

**Per-app constants**
Message strings and choice constants live in each app's
`constants.py`. No cross-app imports for constants.
`core/` only holds truly generic exceptions and utilities.

**Role via mapping table**
User roles are stored in a dedicated `UserRole` table
mapping users to roles, rather than a field on the User model.
This keeps the schema normalized and makes role changes
auditable. `on_delete=PROTECT` on the role FK ensures
roles cannot be deleted while users hold them.

---

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 14+

### Setup
```bash
# Clone and enter project
git clone <repo-url>
cd zorvyn_finance

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Fill in DB_USER, DB_PASSWORD, SECRET_KEY in .env

# Run migrations
python manage.py migrate

# Seed roles (required before registering users)
python manage.py seed_roles

# Create superuser (admin role)
python manage.py createsuperuser

# Start server
python manage.py runserver
```

### Test Users (Quick Start)

After running `seed_roles`, register users via the API
or use the Django admin. Assign roles via `PATCH /api/accounts/users/<id>/`.

---

## API Reference

Full interactive docs available at `/api/docs/` after starting the server.

### Accounts

| Method | Endpoint                      | Auth     | Role       | Description              |
|--------|-------------------------------|----------|------------|--------------------------|
| POST   | /api/accounts/register/       | None     | Public     | Register new user        |
| POST   | /api/accounts/login/          | None     | Public     | Login, receive JWT       |
| GET    | /api/accounts/me/             | JWT      | Any        | Own profile              |
| GET    | /api/accounts/users/          | JWT      | Admin      | List all users           |
| PATCH  | /api/accounts/users/<id>/     | JWT      | Admin      | Update role or status    |
| GET    | /api/accounts/roles/          | JWT      | Admin      | List available roles     |

### Records

| Method | Endpoint                      | Auth     | Role       | Description              |
|--------|-------------------------------|----------|------------|--------------------------|
| GET    | /api/records/                 | JWT      | Any        | List records with filters|
| POST   | /api/records/                 | JWT      | Admin      | Create record            |
| GET    | /api/records/<id>/            | JWT      | Any        | Get single record        |
| PATCH  | /api/records/<id>/            | JWT      | Admin      | Update record            |
| DELETE | /api/records/<id>/            | JWT      | Admin      | Soft delete record       |

### Dashboard

| Method | Endpoint                          | Auth | Role              | Description              |
|--------|-----------------------------------|------|-------------------|--------------------------|
| GET    | /api/records/dashboard/summary/   | JWT  | Analyst, Admin    | Totals + period compare  |
| GET    | /api/records/dashboard/trends/    | JWT  | Analyst, Admin    | Monthly + daily trends   |
| GET    | /api/records/dashboard/categories/| JWT  | Analyst, Admin    | Category breakdown       |
| GET    | /api/records/dashboard/activity/  | JWT  | Analyst, Admin    | Recent 10 records        |

### Record Filters
GET /api/records/?type=income&category=salaries&status=completed
GET /api/records/?date_from=2024-01-01&date_to=2024-03-31
GET /api/records/?search=TXN-20240401
GET /api/records/?ordering=-amount
GET /api/records/?page=2

---

## Role Access Matrix

| Action                        | Viewer | Analyst | Admin |
|-------------------------------|--------|---------|-------|
| View own profile              | ✓      | ✓       | ✓     |
| View records list             | ✓      | ✓       | ✓     |
| View single record            | ✓      | ✓       | ✓     |
| Create records                | ✗      | ✗       | ✓     |
| Update records                | ✗      | ✗       | ✓     |
| Delete records                | ✗      | ✗       | ✓     |
| View dashboard summary        | ✗      | ✓       | ✓     |
| View dashboard trends         | ✗      | ✓       | ✓     |
| View category breakdown       | ✗      | ✓       | ✓     |
| View recent activity          | ✗      | ✓       | ✓     |
| List all users                | ✗      | ✗       | ✓     |
| Update user role/status       | ✗      | ✗       | ✓     |
| View available roles          | ✗      | ✗       | ✓     |

---

## Design Decisions

**Why PostgreSQL over SQLite**
The dashboard APIs use `TruncMonth`, `TruncDay`, and conditional
`Sum` aggregations. PostgreSQL handles these efficiently at scale.
SQLite supports basic aggregations but lacks the query planner
optimizations needed for financial reporting on large datasets.

**Why UUIDs as primary keys**
Sequential integer IDs leak record counts to API consumers.
For a finance system, exposing that you have 1,247 transactions
is an information leak. UUIDs are opaque and safe to expose
in URLs and API responses.

**Why soft delete over hard delete**
Financial records should never be permanently destroyed.
Regulatory requirements in most jurisdictions require
transaction history to be preserved. Soft delete via
`is_deleted` + `deleted_at` satisfies this while keeping
the default queryset clean via `ActiveManager`.

**Why `on_delete=PROTECT` on created_by**
A financial record's creator is part of its audit trail.
Cascading deletion would silently destroy that trail.
`PROTECT` forces an explicit decision — deactivate the user,
don't delete them — which is the correct behavior for a
finance system.

**Why roles in a separate table**
Storing role as a field on User is simpler but not normalized.
A `UserRole` mapping table keeps role assignment auditable,
allows future extension to multiple roles per user if needed,
and prevents role deletion while users hold that role
via `on_delete=PROTECT`.

**Why `Decimal` for all monetary values**
Floating point arithmetic is unsuitable for financial calculations.
`0.1 + 0.2 != 0.3` in IEEE 754. All amounts in this system
use `DecimalField` with explicit precision (`max_digits=12,
decimal_places=2`) and Python's `Decimal` type in service logic.

**Why separate dashboard endpoints over one combined endpoint**
A single `/dashboard/` endpoint that runs all aggregations
on every call is a performance problem waiting to happen.
Separate endpoints let each widget load independently,
fail independently, and be cached independently in future.

---

## Assumptions

- One role per user at all times. The `UserRole` table
  uses `OneToOneField` on user to enforce this.
- Roles are fixed at three (viewer, analyst, admin) and
  seeded at deployment. Runtime role creation is not supported.
- All monetary amounts are stored in the record's stated
  currency. No currency conversion is performed.
- Soft-deleted records are excluded from all dashboard
  aggregations. The `ActiveManager` handles this automatically.
- Completed and cancelled records are immutable. This is
  intentional — financial records should be append-only
  once finalised.
- The `created_by` field tracks which admin created a record.
  End users (viewers, analysts) do not create records.

---

## What I Would Add With More Time

**Audit log**
A dedicated `AuditLog` model recording every state change
on users and records — who changed what, when, and from
what previous value. Critical for a production finance system.

**Refresh token blacklisting**
Currently logout is client-side only. A token blacklist
would invalidate refresh tokens server-side on logout.

**Request-level idempotency**
Financial record creation should support an idempotency key
header so duplicate requests (network retries) don't create
duplicate records. Implemented this in a previous project
using a hash of the request body stored in Redis.

**Caching on dashboard endpoints**
Dashboard aggregations are expensive at scale.
`django-cache` on the four dashboard endpoints with a
short TTL (60 seconds) would significantly reduce DB load
with no impact on data freshness for a dashboard use case.

**Celery + async reporting**
Monthly trend generation across large datasets should
be precomputed asynchronously and served from cache
rather than computed on each request.

**Rate limiting per role**
Current rate limiting is uniform. Viewers making heavy
read requests should be throttled more aggressively
than admins performing writes.