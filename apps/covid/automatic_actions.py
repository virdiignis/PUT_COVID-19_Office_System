from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.covid.models import Case, Action, Person
from apps.office.models import Worker, Reminder


class AutomaticLogActions:
    def __init__(self, case: Case = None, user: Worker = None):
        self.case = case
        self.user = user

    def __create_action(self, desc):
        Action.objects.create(
            datetime=timezone.now(),
            made_by=self.user,
            case=self.case,
            action_description=desc
        )

    def create_case(self):
        self.__create_action(_("Opened the {title} case.").format(title=self.case.title))

    def reopen_case(self):
        self.__create_action(_("Reopened the {title} case.").format(title=self.case.title))

    def close_case(self):
        self.__create_action(_("Closed the {title} case.").format(title=self.case.title))

    def add_new_person(self, person: Person):
        self.__create_action(_("Added new person: {person}.").format(person=person))

    def set_reminder(self, reminder: Reminder):
        self.__create_action(_('Set new reminder. "{reminder}"').format(reminder=reminder))

    def mark_reminder_done(self, reminder: Reminder):
        self.__create_action(_('Marked "{reminder}" done.').format(reminder=reminder))

    def delete_reminder(self, reminder: Reminder):
        self.__create_action(_('Deleted "{reminder}".').format(reminder=reminder))

    def change_person(self, person_new, changed_data):
        self.__create_action(_("Changed the following information: {data} of {person}.").format(
            data=', '.join(changed_data), person=person_new))
