from .settings_common import *

SITE_ID = 1
ROOT_URLCONF = 'backend.urls_office'
ALLOWED_HOSTS = ['covid-app-dev.prv.put.poznan.pl', 'localhost']
WSGI_APPLICATION = 'backend.wsgi:office'

# CELERY_BROKER_URL = 'redis+socket:///var/sockets/redis.sock'
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

X_FRAME_OPTIONS = 'SAMEORIGIN'
