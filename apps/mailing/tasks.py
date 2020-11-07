import random
from django.utils.translation import gettext as _

import xlsxwriter
from django.core.mail import EmailMessage

from apps.covid.reports import prepare_report_context


def send_report():
    email = EmailMessage(
        'Report 1',
        "eh",
        'Biuro Covid <biurocovid@put.poznan.pl>',
        ['covid.head@put.poznan.pl'],
        ['covid19.office@put.poznan.pl'],
        reply_to=['covid19@put.poznan.pl'],
    )
    # email.content_subtype = 'html'
    email.send()


def prepare_report_xlsx(start_date, end_date):
    context = prepare_report_context(start_date, end_date)
    wb = xlsxwriter.Workbook(f'/tmp/report.xlsx')
    bold = wb.add_format({'bold': True})
    bold.set_align('center')
    bold.set_align('vcenter')
    center = wb.add_format()
    center.set_align('center')
    center.set_align('vcenter')
    justify = wb.add_format()
    justify.set_align('justify')

    ws = wb.add_worksheet(name=_("Report"))
    headers = (
        _("New students' infections"),
        _("New students' quarantines"),
        _("New employees' infections"),
        _("New employees' quarantines"),
    )
    ws.set_column(0, 3, 40)
    ws.set_row(0, 40)
    ws.set_row(1, 40)
    ws.write_row(0, 0, headers, bold)
    ws.write_row(1, 0, [
        context["students_sick_new"],
        context["students_quarantined_new"],
        context["employees_sick_new"],
        context["employees_quarantined_new"],
    ], center)

    ws = wb.add_worksheet(name=_("Isolations ordered"))
    headers = (
        _("Ordered by"),
        _("Order date"),
        _("Start date"),
        _("End date"),
        _("Whereabouts"),
        _("Cause"),
        _("Health state"),
    )
    ws.set_column(0, 4, 20)
    ws.set_column(5, 6, 40)
    ws.set_row(0, 40)
    ws.write_row(0, 0, headers, bold)
    for row, case in enumerate(context["isolations"], 1):
        data = (
            str(case.ordered_by),
            case.ordered_on,
            case.start_date,
            case.end_date,
            case.get_whereabouts_display(),
            str(case.cause),
            str(case.person.health_state)
        )
        ws.write_row(row, 0, data, center)

    ws = wb.add_worksheet(name=_("New cases opened"))
    headers = (
        _("Title"),
        _("People involved"),
        _("Date open"),
        _("Date closed"),
    )
    ws.set_column(0, 1, 40)
    ws.set_column(2, 3, 20)
    ws.set_row(0, 40)
    ws.write_row(0, 0, headers, bold)
    for row, case in enumerate(context["cases_opened"], 1):
        ws.write(row, 0, case.title, center)
        ws.write(row, 1, '\n'.join(map(str, case.people.all())), center)
        ws.write(row, 2, case.date_open, bold)
        ws.write(row, 3, case.date_closed, center)
        ws.set_row(row, 20 * case.people.count())

    ws = wb.add_worksheet(name=_("Cases closed"))
    headers = (
        _("Title"),
        _("People involved"),
        _("Date open"),
        _("Date closed"),
    )
    ws.set_column(0, 1, 40)
    ws.set_column(2, 3, 20)
    ws.set_row(0, 40)
    ws.write_row(0, 0, headers, bold)
    for row, case in enumerate(context["cases_closed"], 1):
        ws.write(row, 0, case.title, center)
        ws.write(row, 1, '\n'.join(map(str, case.people.all())), center)
        ws.write(row, 2, case.date_open, bold)
        ws.write(row, 3, case.date_closed, center)
        ws.set_row(row, 20 * case.people.count())



    wb.close()
