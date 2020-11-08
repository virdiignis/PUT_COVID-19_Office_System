from django.core.mail import EmailMessage

from apps.mailing.report import Report


def send_report(subject: str, content: str, start_date, end_date):
    email = EmailMessage(
        subject,
        content,
        'Biuro Covid <biurocovid@put.poznan.pl>',
        ['covid.head@put.poznan.pl'],
        ['covid19.office@put.poznan.pl'],
        reply_to=['covid19.office@put.poznan.pl'],
    )
    report_path = Report(start_date, end_date).get_path()
    email.attach_file(report_path)
    return email.send()
