from datetime import timedelta, date
from celery import shared_task
from django.core.mail import EmailMessage
from django.utils import timezone
from django.template.defaultfilters import date as date_filter

from apps.mailing.report import Report
from django.conf import settings


def send_report(subject: str, content: str, start_date, end_date):
    email = EmailMessage(
        subject,
        content,
        'Biuro Covid <biurocovid@put.poznan.pl>',
        settings.REPORT_TO,
        settings.DW,
        reply_to=['covid19.office@put.poznan.pl'],
    )
    report_path = Report(start_date, end_date).get_path()
    email.attach_file(report_path)
    return email.send()


@shared_task(name='mailing.daily_report')
def daily_report():
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    send_report(
        f"Dzienny raport Biura ds. Covid za {date_filter(yesterday, 'j E Y')}",
        '''
        Szanowna Pani Rektor,
        w załączeniu znajduje się automatycznie wygenerowany dzienny raport sprawozdawczy Biura ds. Covid.
        
        Pozdrawiamy
        Obsada Biura
        ''',
        yesterday,
        today
    )


@shared_task(name='mailing.weekly_report')
def weekly_report():
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    last_week = yesterday - timedelta(days=6)

    if date_filter(last_week, "m") == date_filter(yesterday, "m"):
        rng = f"{date_filter(last_week, 'j')}-{date_filter(yesterday, 'j')} {date_filter(yesterday, 'E Y')}"
    else:
        rng = f"{date_filter(last_week, 'j E Y')} — {date_filter(yesterday, 'j E Y')}"

    send_report(
        f"Tygodniowy raport Biura ds. Covid za {rng}",
        '''
        Szanowna Pani Rektor,
        w załączeniu znajduje się automatycznie wygenerowany tygodniowy raport sprawozdawczy Biura ds. Covid.

        Pozdrawiamy
        Obsada Biura
        ''',
        last_week,
        yesterday
    )


@shared_task(name='mailing.monthly_report')
def monthly_report():
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    last_month = date(year=yesterday.year, month=yesterday.month, day=1)

    send_report(
        f"Miesięczny raport Biura ds. Covid za {date_filter(last_month, 'F Y')}",
        '''
        Szanowna Pani Rektor,
        w załączeniu znajduje się automatycznie wygenerowany miesięczny raport sprawozdawczy Biura ds. Covid.

        Pozdrawiamy
        Obsada Biura
        ''',
        last_month,
        yesterday
    )
