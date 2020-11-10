"""
Django settings for AlertMap project.

Generated by 'django-admin startproject' using Django 3.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv(dotenv_path=".env.local", verbose=True)
except:
    pass

# DEBUG is false by default. Change .env.local file to change this
DEBUG = os.environ.get("STOCKSPEC_DEBUG", "0") == "1"

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["STOCKSPEC_SECRET_KEY"]

CSRF_COOKIE_NAME = "sspec_csrf"
LANGUAGE_COOKIE_NAME = "sspec_lang"
SESSION_COOKIE_NAME = "sspec_session"
ALLOWED_HOSTS = [
    # implement in prod
]

# Env variables
ALPHAVANTAGE_KEY = os.environ["AV_KEY"]


# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # non django
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    "social_django",
    # alertmap
    "stockspec.users",
    "stockspec.portfolio",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
    ),
    "EXCEPTION_HANDLER": "stockspec.exceptions.api_exception_handler",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}

if not DEBUG:
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
        "rest_framework.renderers.JSONRenderer",
    ]

ROOT_URLCONF = "stockspec.urls"

# CORS
CORS_ALLOW_CREDENTIALS = True

# frontend app
CORS_DEBUG_WHITELIST = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ORIGIN_WHITELIST = [
    # implement in prod
]

if DEBUG:
    CORS_ORIGIN_WHITELIST += CORS_DEBUG_WHITELIST

CORS_ORIGIN_REGEX_WHITELIST = [
    # implement in prod
]

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

WSGI_APPLICATION = "stockspec.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "users.User"

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "/static/"

LOGGING = {
    "disable_existing_loggers": False,
    "version": 1,
    "handlers": {
        "console": {
            # logging handler that outputs log messages to terminal
            "class": "logging.StreamHandler",
            "level": "INFO",  # message level to be written to console
        },
    },
    "loggers": {
        "": {
            # this sets root level logger to log debug and higher level
            # logs to console. All other loggers inherit settings from
            # root level logger.
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,  # this tells logger to send logging message
            # to its parent (will send if set to True)
        },
        "django.db": {
            "level": "INFO"
            # django also has database level logging
        },
    },
}

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
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ],
        },
    },
]