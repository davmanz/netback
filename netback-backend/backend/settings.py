from datetime import timedelta
from pathlib import Path
from decouple import config

# small helper to parse comma separated env vars into lists (removes empty/whitespace)
def _parse_list(value):
    """Parse comma-separated env values into a list.

    Accepts non-string inputs (casts to str) and returns an empty list
    for None/empty values.
    """
    if value is None:
        return []
    s = str(value)
    if not s:
        return []
    return [v.strip() for v in s.split(",") if v.strip()]

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY")
ZABBIX_URL = config("ZABBIX_URL", default="")
ZABBIX_TOKEN = config("ZABBIX_TOKEN", default="")
ENCRYPTION_KEY_VAULT = config("ENCRYPTION_KEY_VAULT", default="")

# SECURITY WARNING: don't run with debug turned on in production!
# Make DEBUG configurable via environment (default False)
DEBUG = config("DEBUG", default=False, cast=bool)

# Hosts and CORS: parse and strip whitespace, ignore empty entries
ALLOWED_HOSTS = _parse_list(config("ALLOWED_HOSTS", default="localhost,127.0.0.1"))

CORS_ALLOWED_ORIGINS = _parse_list(
    config(
        "CORS_ALLOWED_ORIGINS",
        default="http://localhost:3000,http://localhost,http://127.0.0.1",
    )
)
CORS_URLS_REGEX = r"^/api/.*$"

# CSRF trusted origins (useful when serving behind https and proxies)
CSRF_TRUSTED_ORIGINS = _parse_list(config("CSRF_TRUSTED_ORIGINS", default=""))

# Application definition

INSTALLED_APPS = [
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_celery_results",
    "django_celery_beat",
    "corsheaders",
    "core",
]

MIDDLEWARE = [
    # Security middleware should be at the top
    "django.middleware.security.SecurityMiddleware",
    # corsheaders recommends being placed as high as possible (before CommonMiddleware)
    "corsheaders.middleware.CorsMiddleware",
    # Sessions must come before CsrfViewMiddleware and AuthenticationMiddleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    # Nuestro middleware de doble-submit CSRF (valida X-CSRF-Token vs cookie XSRF-TOKEN)
    "core.middleware.csrf_double_submit.CSRFDobleSubmitMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # Clickjacking protection last
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "backend.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB", default="netback"),
        "USER": config("POSTGRES_USER", default="postgres"),
        "PASSWORD": config("POSTGRES_PASSWORD", default=""),
        "HOST": config("POSTGRES_HOST", default="localhost"),
        # cast port to int and provide a sensible default
        "PORT": config("POSTGRES_PORT", default=5432, cast=int),
    }
}


# Password validation
AUTH_USER_MODEL = "core.UserSystem"
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = config(
    "TIME_ZONE", 
    default="America/Santiago",)

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"
# Serve static files in production: set STATIC_ROOT and optionally MEDIA
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Rest Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PAGINATION_CLASS": None,
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ),
    # Agregar URLs exentas de autenticación
    "UNAUTHENTICATED_USER": None,
    "UNAUTHENTICATED_TOKEN": None,
    "DEFAULT_AUTHENTICATION_EXEMPT_URLS": [
        "/api/health/",
    ],
}
# Authentification
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    # allow overriding the JWT signing key (good practice to separate from SECRET_KEY)
    "SIGNING_KEY": config("JWT_SIGNING_KEY", default=SECRET_KEY),
    "VERIFYING_KEY": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# Configuracion de Celery
CELERY_BROKER_URL = config("CELERY_BROKER_URL")
CELERY_BROKER_CONNECTION_RETRY = True
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_BACKEND = "django-db"
CELERY_CACHE_BACKEND = "django-cache"
# Optional: allow disabling eager mode for tests by env var
CELERY_TASK_ALWAYS_EAGER = config("CELERY_TASK_ALWAYS_EAGER", default=False, cast=bool)

# Security-related defaults (enable these in production via env vars)
SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", default=not DEBUG, cast=bool)
CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", default=not DEBUG, cast=bool)
# Nombre de la cookie expuesta a JS para double-submit
CSRF_COOKIE_NAME = config("CSRF_COOKIE_NAME", default="XSRF-TOKEN")
CSRF_COOKIE_SAMESITE = config("CSRF_COOKIE_SAMESITE", default="Lax")

#SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=not DEBUG, cast=bool)
SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=0, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config("SECURE_HSTS_INCLUDE_SUBDOMAINS", default=False, cast=bool)
SECURE_HSTS_PRELOAD = config("SECURE_HSTS_PRELOAD", default=False, cast=bool)

# If you're behind a proxy/load balancer that sets X-Forwarded-Proto
if config("USE_X_FORWARDED_PROTO", default=False, cast=bool):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Basic logging to capture errors — extend as needed
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
