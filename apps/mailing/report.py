import os

from apps.covid.reports import prepare_report_context
import xlsxwriter

from django.utils.timezone import localtime
from django.utils.translation import gettext as _
from django.conf import settings


class Report:
    TEXT_COLUMNS_WIDTH = 50

    @staticmethod
    def _clear_newlines(text):
        return '\n'.join(map(str.rstrip, str(text or "").split("\n")))

    @classmethod
    def _lines_num(cls, text):
        text_lines = cls._clear_newlines(text).split("\n")
        return max(
            len(text_lines),
            sum(((len(line) / cls.TEXT_COLUMNS_WIDTH) for line in text_lines))
        )

    def __create_workbook_with_styles(self):
        self.__wb = xlsxwriter.Workbook(self.__path)
        self._styles["bold"] = self.__wb.add_format({'bold': True})
        self._styles["bold"].set_align('center')
        self._styles["bold"].set_align('vcenter')
        self._styles["bold"].set_border(1)
        self._styles["bold_date"] = self.__wb.add_format({'bold': True, 'num_format': 'd mmmm yyyy'})
        self._styles["bold_date"].set_align('center')
        self._styles["bold_date"].set_align('vcenter')
        self._styles["bold_date"].set_border(1)
        self._styles["center"] = self.__wb.add_format()
        self._styles["center"].set_align('center')
        self._styles["center"].set_align('vcenter')
        self._styles["center"].set_border(1)
        self._styles["center_date"] = self.__wb.add_format({'num_format': 'd mmmm yyyy'})
        self._styles["center_date"].set_align('center')
        self._styles["center_date"].set_align('vcenter')
        self._styles["center_date"].set_border(1)
        self._styles["center_datetime"] = self.__wb.add_format({'num_format': 'd mmmm yyyy hh:mm'})
        self._styles["center_datetime"].set_align('center')
        self._styles["center_datetime"].set_align('vcenter')
        self._styles["center_datetime"].set_border(1)
        self._styles["justify"] = self.__wb.add_format({"text_wrap": True})
        self._styles["justify"].set_align('justify')
        self._styles["justify"].set_align('vcenter')
        self._styles["justify"].set_border(1)
        self._styles["header"] = self.__wb.add_format({'bold': True, 'bg_color': "#B7E1CD"})
        self._styles["header"].set_align('center')
        self._styles["header"].set_align('vcenter')
        self._styles["header"].set_border(2)
        self._styles["header"].set_bottom(5)

    def __add_numerical_report(self):
        ws = self.__wb.add_worksheet(name=_("Report"))
        ws.set_default_row(20)
        headers = (
            _("New students' infections"),
            _("New students' quarantines"),
            _("New employees' infections"),
            _("New employees' quarantines"),
        )
        ws.set_column(0, 3, 40)
        ws.set_row(0, 40)
        ws.set_row(1, 40)
        ws.write_row(0, 0, headers, self._styles["header"])
        ws.write_row(1, 0, [
            self.__context["students_sick_new"],
            self.__context["students_quarantined_new"],
            self.__context["employees_sick_new"],
            self.__context["employees_quarantined_new"],
        ], self._styles["center"])

    def __add_isolations_ordered(self):
        ws = self.__wb.add_worksheet(name=_("Isolations ordered"))
        ws.set_default_row(20)
        headers = (
            _("Name"),
            _("Ordered by"),
            _("Order date"),
            _("Office informed"),
            _("Start date"),
            _("End date"),
            _("Whereabouts"),
            _("Cause"),
            _("Health state"),
        )
        ws.set_column(0, 0, 25)
        ws.set_column(1, 1, 18)
        ws.set_column(2, 6, 20)
        ws.set_column(7, 8, 32)
        ws.set_row(0, 40)
        ws.write_row(0, 0, headers, self._styles["header"])
        for row, isolation in enumerate(self.__context["isolations"], 1):
            ws.write(row, 0, str(isolation.person), self._styles["center"])
            ws.write(row, 1, str(isolation.ordered_by), self._styles["center"])
            ws.write(row, 2, isolation.ordered_on, self._styles["center_date"])
            ws.write(row, 3, isolation.added, self._styles["center_date"])
            ws.write(row, 4, isolation.start_date, self._styles["center_date"])
            ws.write(row, 5, isolation.end_date, self._styles["center_date"])
            ws.write(row, 6, isolation.get_whereabouts_display(), self._styles["center"])
            ws.write(row, 7, str(isolation.cause), self._styles["center"])
            ws.write(row, 8, str(isolation.person.health_state), self._styles["center"])

    def __add_new_cases_opened(self):
        ws = self.__wb.add_worksheet(name=_("New cases opened"))
        ws.set_default_row(20)
        headers = (
            _("Title"),
            _("People involved"),
            _("Date open"),
            _("Date closed"),
        )
        ws.set_column(0, 1, 40)
        ws.set_column(2, 3, 20)
        ws.set_row(0, 40)
        ws.write_row(0, 0, headers, self._styles["header"])
        for row, case in enumerate(self.__context["cases_opened"], 1):
            ws.write(row, 0, case.title, self._styles["center"])
            ws.write(row, 1, '\n'.join(map(str, case.people.all())), self._styles["center"])
            ws.write(row, 2, case.date_open, self._styles["bold_date"])
            ws.write(row, 3, case.date_closed, self._styles["center_date"])
            ws.set_row(row, 20 * case.people.count())

    def __add_cases_closed(self):
        ws = self.__wb.add_worksheet(name=_("Cases closed"))
        ws.set_default_row(20)
        headers = (
            _("Title"),
            _("People involved"),
            _("Date open"),
            _("Date closed"),
        )
        ws.set_column(0, 1, 40)
        ws.set_column(2, 3, 20)
        ws.set_row(0, 40)
        ws.write_row(0, 0, headers, self._styles["header"])
        for row, case in enumerate(self.__context["cases_closed"], 1):
            ws.write(row, 0, case.title, self._styles["center"])
            ws.write(row, 1, '\n'.join(map(str, case.people.all())), self._styles["center"])
            ws.write(row, 2, case.date_open, self._styles["center_date"])
            ws.write(row, 3, case.date_closed, self._styles["bold_date"])
            ws.set_row(row, 20 * case.people.count())

    def __add_office_actions(self):
        ws = self.__wb.add_worksheet(name=_("Office actions"))
        ws.set_default_row(20)
        headers = (
            _("Datetime"),
            _("Made by"),
            _("Based on"),
            _("Contact from"),
            _("Incoming contact content"),
            _("Description"),
            _("Notes"),
            _("Case"),
        )

        ws.set_column(0, 0, 21)
        ws.set_column(1, 2, 16)
        ws.set_column(3, 3, 30)
        ws.set_column(4, 6, self.TEXT_COLUMNS_WIDTH)
        ws.set_column(7, 7, 30)
        ws.set_row(0, 40)
        ws.write_row(0, 0, headers, self._styles["header"])

        for row, action in enumerate(self.__context["actions"], 1):
            ws.write_datetime(row, 0, localtime(action.datetime).replace(tzinfo=None), self._styles["center_datetime"])
            ws.write(row, 1, str(action.made_by), self._styles["center"])
            ws.write(row, 2, str(action.get_based_on_display()), self._styles["center"])
            ws.write(row, 3, str(action.contact_from or ""), self._styles["center"])
            ws.write(row, 4, self._clear_newlines(action.contact_content), self._styles["justify"])
            ws.write(row, 5, self._clear_newlines(action.action_description), self._styles["justify"])
            ws.write(row, 6, self._clear_newlines(action.notes or ""), self._styles["justify"])
            ws.write(row, 7, str(action.case or "—"), self._styles["center"])
            ws.set_row(row, 20 * max(
                self._lines_num(action.contact_content),
                self._lines_num(action.action_description),
                self._lines_num(action.notes),
            ) or 1)

    def __create_report(self):
        self.__create_workbook_with_styles()
        self.__add_numerical_report()
        self.__add_isolations_ordered()
        self.__add_new_cases_opened()
        self.__add_cases_closed()
        self.__add_office_actions()
        self.__wb.close()

    def __init__(self, start_date, end_date):
        self.__context = prepare_report_context(start_date, end_date)
        self.__path = os.path.join(settings.MEDIA_ROOT, f"reports/report_{start_date}_{end_date}.xlsx")
        self._styles = {}
        self.__create_report()

    def get_path(self):
        return self.__path
