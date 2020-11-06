from django.utils import timezone

from apps.covid.models import Case, Action, Person
from apps.office.models import Worker


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
        self.__create_action(f"{str(self.user)} opened the {self.case.title} case.")

    def reopen_case(self):
        self.__create_action(f"{str(self.user)} reopened the {self.case.title} case.")

    def close_case(self):
        self.__create_action(f"{str(self.user)} closed the {self.case.title} case.")

    def add_new_person(self, person: Person):
        self.__create_action(f"{str(self.user)} added new person — {str(person)} — to database.")

    def set_reminder(self):
        self.__create_action(f"{str(self.user)} set new reminder.")
