"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 3.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
from celery.schedules import crontab

BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '=oees2o6!f&a33bk0#l2dk!eyo4+c4^hx%)ej#bt()vr1sg9(g'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['covid-app-dev.prv.put.poznan.pl', 'localhost']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dal',
    'dal_select2',
    'bootstrap_modal_forms',
    'bootstrap_pagination',
    'apps.office',
    'apps.covid',
    'apps.mailing',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'covid_office',
        'USER': 'covid_office',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "unix:/var/sockets/redis.sock",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        },
        "KEY_PREFIX": "covidcache"
    }
}

CELERY_BROKER_URL = 'redis+socket:///var/sockets/redis.sock'
CELERY_TIMEZONE = "Europe/Warsaw"
CELERY_BEAT_SCHEDULE = {
    'daily_report': {
        'task': 'mailing.daily_report',
        'schedule': crontab(minute=0, hour=7),
    },
    'isolations_over': {
        'task': 'covid.isolations_over',
        'schedule': crontab(minute=0, hour=6),
    },
    'weekly_report': {
        'task': 'mailing.weekly_report',
        'schedule': crontab(minute=0, hour=0, day_of_week='monday'),
    },
    'monthly_report': {
        'task': 'mailing.monthly_report',
        'schedule': crontab(minute=0, hour=0, day_of_month='1')
    },
    'shifts_takeovers': {
        'task': 'office.shift_takeover',
        'schedule': crontab(minute=40, hour='6,14,22')
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = "office.worker"

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'pl-pl'
LANGUAGES = (  # supported languages
    ('en', 'English'),
    ('pl', 'Polish'),
)

LOCALE_PATHS = [
    BASE_DIR / "apps/covid/locale",
    BASE_DIR / "apps/office/locale",
    BASE_DIR / "locale",
]

FORMAT_MODULE_PATH = [
    'backend.formats',
]

TIME_ZONE = 'Europe/Warsaw'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

STATIC_ROOT = 'static_root'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
MEDIA_ROOT = 'media'
MEDIA_URL = '/media/'

X_FRAME_OPTIONS = 'SAMEORIGIN'

EMAIL_USE_TLS = True
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = "Biuro Covid <biurocovid@put.poznan.pl>"

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

with open(BASE_DIR / "backend/secrets.py") as F:
    exec(compile(F.read(), filename="secrets.py", mode="exec"))
