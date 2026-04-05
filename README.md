# Zorvyn Finance — Backend Assessment

A finance dashboard backend built with Django, DRF, and PostgreSQL.
It includes role-based access control, financial record workflows,
analytics endpoints, JWT auth, OpenAPI docs, and scoped rate limiting.

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Environment Configuration](#environment-configuration)
- [Getting Started](#getting-started)
- [API Docs (Swagger/Redoc)](#api-docs-swaggerredoc)
- [Rate Limiting](#rate-limiting)
- [Testing](#testing)
- [API Reference](#api-reference)

---

## Tech Stack

| Layer | Choice | Reason |
|---|---|---|
| Framework | Django + DRF | Mature and reliable API framework |
| Database | PostgreSQL | Strong aggregation/query support |
| Auth | SimpleJWT | Stateless token auth for APIs |
| Filtering | django-filter | Declarative filtering for records |
| API Docs | drf-spectacular | OpenAPI schema + Swagger/Redoc |
| Testing | pytest-django + factory-boy | Fast, modular, realistic test setup |

---

## Architecture

```text
zorvyn_finance/
├── config/
│   ├── settings.py                # Env-driven settings (APP_ENV aware)
│   └── urls.py                    # API routers + schema/docs routes
├── apps/
│   ├── core/
│   │   ├── apps.py                # App startup hooks (schema extension import)
│   │   ├── schema.py              # drf-spectacular auth extension
│   │   ├── throttling.py          # Shared throttle base class
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── base.py            # BaseModel + ActiveManager
│   │   └── utils/
│   │       ├── api_response.py
│   │       ├── exception_handler.py
│   │       ├── exceptions.py
│   │       ├── pagination.py
│   │       └── swagger_helpers.py
│   ├── accounts/
│   │   ├── models/
│   │   ├── serializers/
│   │   ├── services/
│   │   ├── views/
│   │   ├── throttling.py          # Accounts scopes (auth/users/me)
│   │   ├── urls.py
│   │   └── migrations/
│   │       └── 0002_seed_roles.py # Roles seeded via migration
│   └── records/
│       ├── models/
│       ├── serializers/
│       ├── services/
│       ├── views/
│       ├── throttling.py          # Records + dashboard scopes
│       ├── urls.py
│       └── management/commands/
│           └── seed_data.py       # Demo users + realistic records
└── tests/
    ├── conftest.py
    ├── factories.py
    ├── test_accounts.py
    └── test_records.py
```

### Core App Corrections

- `BaseModel` lives in `apps/core/models/base.py`.
- `apps/core/models.py` has been removed to avoid duplicate model definitions.
- Role seed data is not a management command anymore; it is migration-based.

---

## Environment Configuration

Settings are environment-driven using `python-decouple`.

- `APP_ENV=local` loads `.env`
- `APP_ENV=dev` loads `.env.dev`
- `APP_ENV=prod` loads `.env.prod`

### Relevant env-configured settings

- Django core: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `LANGUAGE_CODE`, `TIME_ZONE`, `USE_I18N`, `USE_TZ`, `STATIC_URL`
- Database: `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- API docs: `API_TITLE`, `API_DESCRIPTION`, `API_VERSION`, `SPECTACULAR_SERVE_INCLUDE_SCHEMA`, `SPECTACULAR_COMPONENT_SPLIT_REQUEST`, `SWAGGER_*`
- Throttling: `THROTTLE_*` scoped rates

Use your target env file values instead of editing code.

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

# Create and activate virtual environment
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Choose environment profile (optional)
# PowerShell examples:
# $env:APP_ENV="local"
# $env:APP_ENV="dev"
# $env:APP_ENV="prod"

# Run migrations (includes role seed migration)
python manage.py migrate

# Seed realistic users and records for manual testing
python manage.py seed_data

# Start server
python manage.py runserver
```

---

## API Docs (Swagger/Redoc)

- OpenAPI schema: `/api/schema/`
- Swagger UI: `/api/docs/`
- Redoc: `/api/redoc/`

JWT auth is integrated with a single `BearerAuth` scheme.
In Swagger Authorize, paste the access token value.

---

## Rate Limiting

Rate limiting uses DRF scoped throttling with modular throttle classes.

Configured scopes:

- `auth_register`
- `auth_login`
- `me_read`
- `users_read`
- `users_write`
- `records_read`
- `records_write`
- `dashboard_read`

Default rates are set in `config/settings.py` and can be overridden via env variables (`THROTTLE_*`).

---

## Testing

- Framework: `pytest-django`
- Factories: `factory-boy`
- Config: `pytest.ini`
- Test data fixtures: `tests/conftest.py`

Run tests:

```bash
python -m pytest
```

Run targeted suites:

```bash
python -m pytest tests/test_accounts.py tests/test_records.py
```

---

## API Reference

Base prefix: `/api`

### Accounts

| Method | Endpoint | Auth | Role | Description |
|---|---|---|---|---|
| POST | `/api/accounts/register/` | None | Public | Register user |
| POST | `/api/accounts/login/` | None | Public | Login and get JWT |
| GET | `/api/accounts/users/` | JWT | Admin | List users |
| GET | `/api/accounts/users/<uuid>/` | JWT | Admin | Get user detail |
| PATCH | `/api/accounts/users/<uuid>/` | JWT | Admin | Update role/status |
| GET | `/api/accounts/roles/` | JWT | Admin | List roles |

### Records

| Method | Endpoint | Auth | Role | Description |
|---|---|---|---|---|
| GET | `/api/records/v1/transaction/create` | JWT | Viewer+ | List records |
| POST | `/api/records/v1/transaction/create` | JWT | Admin | Create record |
| GET | `/api/records/v1/record/<uuid>/` | JWT | Viewer+ | Get record |
| PATCH | `/api/records/v1/record/<uuid>/` | JWT | Admin | Update record |
| DELETE | `/api/records/v1/record/<uuid>/` | JWT | Admin | Soft delete record |

### Dashboard

| Method | Endpoint | Auth | Role | Description |
|---|---|---|---|---|
| GET | `/api/records/v1/dashboard/summary/` | JWT | Analyst+ | Summary totals |
| GET | `/api/records/v1/dashboard/trends/` | JWT | Analyst+ | Trends |
| GET | `/api/records/v1/dashboard/categories/` | JWT | Analyst+ | Category breakdown |
| GET | `/api/records/v1/dashboard/activity/` | JWT | Analyst+ | Recent activity |

---

## Notes

- Roles are seeded by migration `apps/accounts/migrations/0002_seed_roles.py`.
- `seed_data` command expects those roles to exist and will warn if migrations were not applied.
- Endpoint schemas are explicitly decorated for APIView-based endpoints to provide request/response visibility in Swagger.
