from django.db import models
from django.db.models import Model
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

from apps.office.models import Worker


class Unit(Model):
    name = models.CharField(max_length=255, primary_key=True)
    report_students_email = models.EmailField(null=True, blank=True)
    report_employees_email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return self.name


class HealthState(Model):
    name = models.CharField(max_length=16, primary_key=True)
    test = models.BooleanField(null=True, blank=True)
    considered_sick = models.BooleanField()
    considered_suspect = models.BooleanField()

    @property
    def severity(self):
        return 0 if self.considered_sick else 1 if self.considered_suspect else 2

    def __str__(self):
        if self.test is not None:
            if self.test:
                test = " with positive test result."
            else:
                test = " with negative test result."
        else:
            test = ""

        return f"{self.name}{test}"


class IsolationIssuer(Model):
    name = models.CharField(max_length=16, primary_key=True)

    def __str__(self):
        return self.name


class IsolationCause(Model):
    name = models.CharField(max_length=255, primary_key=True)

    def __str__(self):
        return self.name


class Person(Model):
    title = models.CharField(max_length=4, default="Mr", choices=(
        ("Mr", "Mr"),
        ("Ms", "Ms"),
        ("Mrs", "Mrs"),
        ("inz", "inż."),
        ("mgr", "mgr"),
        ("mgri", "mgr inż."),
        ("dr", "dr"),
        ("dri", "dr inż."),
        ("drh", "dr hab."),
        ("drhi", "dr hab. inż."),
        ("prh", "prof. dr hab."),
        ("prhi", "prof. dr hab. inż."),
        ("prp", "dr hab. prof. PP"),
        ("prip", "dr hab. inż. prof. PP"),
    ))
    first_name = models.CharField(max_length=32)
    middle_name = models.CharField(max_length=32, null=True, blank=True)
    last_name = models.CharField(max_length=32)
    email = models.EmailField(null=True, blank=True)
    phone_number = PhoneNumberField(null=True, blank=True, unique=True)
    role = models.CharField(max_length=1, default="N", choices=(("S", "Student"),
                                                                ("E", "Employee"),
                                                                ("N", "None")))
    health_state = models.ForeignKey(HealthState, on_delete=models.SET_NULL, null=True, blank=False)
    dorm = models.IntegerField(default=0, choices=(
        (0, "None"),
        (1, "DS1"),
        (2, "DS2"),
        (3, "DS3"),
        (4, "DS4"),
        (5, "DS5"),
        (6, "DS6"),
    ))
    unit = models.ForeignKey(Unit, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        title = f"{self.title} " if self.title is not None else ''
        middle = f" {self.middle_name} " if self.middle_name is not None else ' '
        return f"{title}{self.first_name}{middle}{self.last_name}"


class Case(Model):
    title = models.CharField(max_length=255)
    people = models.ManyToManyField(Person, related_name="cases")
    date_open = models.DateField(auto_now_add=True)
    date_close = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title


class Isolation(Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='isolations')
    ordered_by = models.ForeignKey(IsolationIssuer, on_delete=models.SET_NULL, null=True, blank=False)
    start_date = models.DateField()
    end_date = models.DateField()
    ordered_on = models.DateField()
    whereabouts = models.CharField(max_length=1, null=True, blank=False, default="H", choices=(("H", "Home"),
                                                                                               ("D", "DS4")))
    cause = models.ForeignKey(IsolationCause, on_delete=models.SET_NULL, null=True, blank=False)

    def active(self):
        return timezone.now().date() <= self.end_date

    def __str__(self):
        return f"{self.person}'s isolation in case {self.case}"


class Action(Model):
    datetime = models.DateTimeField(auto_now_add=True)
    made_by = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True, blank=False)
    based_on = models.CharField(max_length=1, default="O", choices=(("O", "Own action"),
                                                                    ("E", "Email"),
                                                                    ("P", "Phone call")))
    contact_content = models.TextField(null=True, blank=True)
    action_description = models.TextField()
    notes = models.TextField(null=True, blank=True)
    case = models.ForeignKey(Case, related_name="actions", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.made_by.get_short_name()} did {self.action_description} in case {self.case}"


class Document(Model):
    file = models.FileField(upload_to="docs")
    name = models.CharField(max_length=1024)
    upload_date = models.DateTimeField(auto_now_add=True)
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='documents')

    def __str__(self):
        return f"Document {self.name} in case {self.case}"


class IsolationRoom(Model):
    number = models.IntegerField()
    resident = models.OneToOneField(Person, null=True, blank=True, on_delete=models.SET_NULL)
    is_cleaned = models.BooleanField(default=True)

    def __str__(self):
        return f"Room {self.number}"
