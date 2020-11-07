from datetime import timedelta
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Model, BooleanField
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class Worker(AbstractUser):
    phone_number = PhoneNumberField(null=True, blank=True, unique=True, verbose_name=_("phone number"))
    write_access = BooleanField(default=False, verbose_name=_("write access"))

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = _("office worker")
        verbose_name_plural = _("office workers")


class Reminder(Model):
    datetime = models.DateTimeField(verbose_name=_("datetime"))
    set_by = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True, blank=False, related_name='set_reminders',
                               verbose_name=_("set by"))
    title = models.TextField(verbose_name=_("title"))
    notes = models.TextField(null=True, blank=True, verbose_name=_("notes"))
    read_by = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True, blank=True, related_name='read_reminders',
                                verbose_name=_("read by"))
    read_on = models.DateTimeField(null=True, verbose_name=_("read on"))

    @property
    def urgency(self):
        if self.datetime - timezone.now() < timedelta(0):
            return 3
        elif self.datetime - timezone.now() < timedelta(minutes=10):
            return 2
        elif self.datetime - timezone.now() < timedelta(hours=1):
            return 1
        else:
            return 0

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("reminder")
        verbose_name_plural = _("reminders")
