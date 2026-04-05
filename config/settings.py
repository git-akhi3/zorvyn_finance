import os
from pathlib import Path
from decouple import AutoConfig, Config, Csv, RepositoryEnv

BASE_DIR = Path(__file__).resolve().parent.parent

APP_ENV = os.getenv("APP_ENV", "local").lower()
ENV_FILE_BY_ENV = {
    "local": ".env",
    "dev": ".env.dev",
    "prod": ".env.prod",
}
selected_env_file = ENV_FILE_BY_ENV.get(APP_ENV, ".env")
selected_env_path = BASE_DIR / selected_env_file

if selected_env_path.exists():
    config = Config(RepositoryEnv(str(selected_env_path)))
else:
    config = AutoConfig(search_path=BASE_DIR)

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="", cast=Csv())

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_filters",
    "drf_spectacular",
    "corsheaders",
    "apps.accounts",
    "apps.records",
    "apps.core",
]

REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "apps.core.utils.exception_handler.custom_exception_handler",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_RATES": {
        "auth_register": config("THROTTLE_AUTH_REGISTER", default="10/min"),
        "auth_login": config("THROTTLE_AUTH_LOGIN", default="20/min"),
        "users_read": config("THROTTLE_USERS_READ", default="120/min"),
        "users_write": config("THROTTLE_USERS_WRITE", default="60/min"),
        "records_read": config("THROTTLE_RECORDS_READ", default="240/min"),
        "records_write": config("THROTTLE_RECORDS_WRITE", default="120/min"),
        "dashboard_read": config("THROTTLE_DASHBOARD_READ", default="120/min"),
    },
}

SPECTACULAR_SETTINGS = {
    "TITLE": config("API_TITLE", default="Zorvyn Finance API"),
    "DESCRIPTION": config(
        "API_DESCRIPTION",
        default=(
            "Finance dashboard backend API. Authenticate via /api/accounts/login/ "
            "to get a JWT token, then click Authorize and paste the access token."
        ),
    ),
    "VERSION": config("API_VERSION", default="1.0.0"),
    "SERVE_INCLUDE_SCHEMA": config("SPECTACULAR_SERVE_INCLUDE_SCHEMA", default=False, cast=bool),
    "COMPONENT_SPLIT_REQUEST": config("SPECTACULAR_COMPONENT_SPLIT_REQUEST", default=True, cast=bool),
    "TAGS": [
        {"name": "auth", "description": "Registration and login"},
        {"name": "users", "description": "User management (admin only)"},
        {"name": "roles", "description": "Role listing (admin only)"},
        {"name": "records", "description": "Financial record management"},
        {"name": "dashboard", "description": "Aggregated dashboard data"},
    ],
    "SECURITY": [{"BearerAuth": []}],
    "SWAGGER_UI_SETTINGS": {
        "persistAuthorization": config("SWAGGER_PERSIST_AUTH", default=True, cast=bool),
        "displayRequestDuration": config("SWAGGER_DISPLAY_REQUEST_DURATION", default=True, cast=bool),
        "filter": config("SWAGGER_FILTER", default=True, cast=bool),
    },
}

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": config("DB_ENGINE", default="django.db.backends.postgresql"),
        "NAME": config("DB_NAME", default="assessment"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = config("LANGUAGE_CODE", default="en-us")
TIME_ZONE = config("TIME_ZONE", default="UTC")
USE_I18N = config("USE_I18N", default=True, cast=bool)
USE_TZ = config("USE_TZ", default=True, cast=bool)

STATIC_URL = config("STATIC_URL", default="static/")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.User"
