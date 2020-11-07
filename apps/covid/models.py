from django.db import models
from django.db.models import Model
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _

from apps.office.models import Worker


class Unit(Model):
    name = models.CharField(max_length=255, primary_key=True, verbose_name=_("name"))
    report_students_email = models.EmailField(null=True, blank=True, verbose_name=_("report students email"))
    report_employees_email = models.EmailField(null=True, blank=True, verbose_name=_("report employees email"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("unit")
        verbose_name_plural = _("units")


class HealthState(Model):
    name = models.CharField(max_length=16, primary_key=True, verbose_name=_("name"))
    test = models.BooleanField(null=True, blank=True, verbose_name=_("test result"))
    considered_sick = models.BooleanField(verbose_name=_("considered sick"))
    considered_suspect = models.BooleanField(verbose_name=_("considered suspect"))

    @property
    def severity(self):
        return 0 if self.considered_sick else 1 if self.considered_suspect else 2

    def __str__(self):
        if self.test is not None:
            if self.test:
                test = _(" (positive test result)")
            else:
                test = _(" (negative test result)")
        else:
            test = ""

        return f"{self.name}{test}"

    class Meta:
        verbose_name = _("health state")
        verbose_name_plural = _("health states")


class IsolationIssuer(Model):
    name = models.CharField(max_length=16, primary_key=True, verbose_name=_("name"))
    official = models.BooleanField(default=False, verbose_name=_("official"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("isolation issuer")
        verbose_name_plural = _("isolation issuers")


class IsolationCause(Model):
    name = models.CharField(max_length=255, primary_key=True, verbose_name=_("name"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("isolation cause")
        verbose_name_plural = _("isolation causes")


class Person(Model):
    title = models.CharField(max_length=4, default="Mr", choices=(
        ("Mr", _("Mr")),
        ("Ms", _("Ms")),
        ("Mrs", _("Mrs")),
        ("inz", _("eng.")),
        ("mgr", _("msc")),
        ("mgri", _("msc eng.")),
        ("dr", _("dr")),
        ("dri", _("dr eng.")),
        ("drh", _("dr habil.")),
        ("drhi", _("dr habil. eng.")),
        ("prh", _("prof. dr habil.")),
        ("prhi", _("prof. dr habil. eng.")),
        ("prp", _("dr habil. prof. PUT")),
        ("prip", _("dr habil. eng. prof. PUT")),
    ), verbose_name=_("title"))
    first_name = models.CharField(max_length=32, verbose_name=_("first name"))
    middle_name = models.CharField(max_length=32, null=True, blank=True, verbose_name=_("middle name"))
    last_name = models.CharField(max_length=32, verbose_name=_("last name"))
    email = models.EmailField(null=True, blank=True, unique=True)
    phone_number = PhoneNumberField(null=True, blank=True, unique=True, verbose_name=_("phone number"))
    role = models.CharField(max_length=1, default="N", choices=(("S", _("Student")),
                                                                ("E", _("Employee")),
                                                                ("N", _("None"))))
    health_state = models.ForeignKey(HealthState, on_delete=models.SET_NULL, null=True, blank=False,
                                     verbose_name=_("health state"))
    dorm = models.IntegerField(default=0, choices=(
        (0, _("None")),
        (1, "DS1"),
        (2, "DS2"),
        (3, "DS3"),
        (4, "DS4"),
        (5, "DS5"),
        (6, "DS6"),
    ), verbose_name=_("dorm"))
    unit = models.ForeignKey(Unit, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_("unit"))

    def __str__(self):
        title = f"{self.get_title_display()} " if self.title is not None else ''
        middle = f" {self.middle_name} " if self.middle_name is not None else ' '
        return f"{title}{self.first_name}{middle}{self.last_name}"

    class Meta:
        verbose_name = _("person")
        verbose_name_plural = _("people")


class HealthStateChange(Model):
    datetime = models.DateField(auto_now_add=True, verbose_name=_("datetime"))
    person = models.ForeignKey(Person, on_delete=models.CASCADE, verbose_name=_("person"))
    change_from = models.ForeignKey(HealthState, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='healthchanges_from', verbose_name=_("change from"))
    change_to = models.ForeignKey(HealthState, on_delete=models.SET_NULL, null=True, blank=False,
                                  related_name='healthchanges_to', verbose_name=_("change to"))
    changed_by = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name=_("changed by"))

    class Meta:
        verbose_name = _("health state change")
        verbose_name_plural = _("health states changes")


class Case(Model):
    title = models.CharField(max_length=255, unique=True, verbose_name=_("title"))
    people = models.ManyToManyField(Person, related_name="cases", blank=True, verbose_name=_("people"))
    date_open = models.DateField(auto_now_add=True, verbose_name=_("date open"))
    date_closed = models.DateField(null=True, blank=True, verbose_name=_("date closed"))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("case")
        verbose_name_plural = _("cases")


class Isolation(Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, verbose_name=_("person"))
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='isolations', verbose_name=_("case"))
    ordered_by = models.ForeignKey(IsolationIssuer, on_delete=models.SET_NULL, null=True, blank=False,
                                   verbose_name=_("ordered by"))
    ordered_on = models.DateField(verbose_name=_("ordered on"))
    start_date = models.DateField(verbose_name=_("start date"))
    end_date = models.DateField(verbose_name=_("end date"))
    whereabouts = models.CharField(max_length=1, null=True, blank=False, default="H", choices=(("H", _("Home")),
                                                                                               ("D", "DS4")),
                                   verbose_name=_("whereabouts"))
    cause = models.ForeignKey(IsolationCause, on_delete=models.SET_NULL, null=True, blank=False,
                              verbose_name=_("cause"))

    def active(self):
        return timezone.now().date() <= self.end_date

    def __str__(self):
        return _(f"{self.person}'s isolation in case {self.case}")

    class Meta:
        verbose_name = _("isolation")
        verbose_name_plural = _("isolations")


class Action(Model):
    datetime = models.DateTimeField(verbose_name=_("datetime"))
    made_by = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True, blank=False, verbose_name=_("made by"))
    based_on = models.CharField(max_length=1, default="O", choices=(("O", _("Own action")),
                                                                    ("E", _("Email")),
                                                                    ("P", _("Phone call"))),
                                verbose_name=_("based on"))

    contact_from = models.ForeignKey(Person, null=True, blank=True, on_delete=models.SET_NULL,
                                     verbose_name=_("contact from"))
    contact_content = models.TextField(null=True, blank=True, verbose_name=_("incoming contact content"))
    action_description = models.TextField(verbose_name=_("action description"))
    notes = models.TextField(null=True, blank=True, verbose_name=_("notes"))
    case = models.ForeignKey(Case, related_name="actions", on_delete=models.CASCADE, null=True, blank=True,
                             verbose_name=_("case"))

    def __str__(self):
        return f"{self.made_by.get_short_name() or self.made_by.username} did {self.action_description} in case {self.case}"

    class Meta:
        verbose_name = _("action")
        verbose_name_plural = _("actions")


class Document(Model):
    file = models.FileField(upload_to="docs", verbose_name=_("file"))
    name = models.CharField(max_length=1024, verbose_name=_("name"))
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name=_("upload date"))
    uploaded_by = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True, blank=False,
                                    verbose_name=_("uploaded by"))
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='documents', verbose_name=_("case"))

    def __str__(self):
        return _(f"Document {self.name} in case {self.case}")

    class Meta:
        verbose_name = _("document")
        verbose_name_plural = _("documents")


class IsolationRoom(Model):
    number = models.PositiveSmallIntegerField(verbose_name=_("number"), primary_key=True)
    resident = models.OneToOneField(Person, null=True, blank=True, on_delete=models.SET_NULL,
                                    verbose_name=_("resident"))
    is_cleaned = models.BooleanField(default=True, verbose_name=_("is cleaned"))

    def __str__(self):
        return _(f"Room {self.number}")

    class Meta:
        verbose_name = _("isolation room")
        verbose_name_plural = _("isolation rooms")
