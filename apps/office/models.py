from datetime import timedelta

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Model, BooleanField
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class Worker(AbstractUser):
    phone_number = PhoneNumberField(null=True, blank=True, unique=True)
    write_access = BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Reminder(Model):
    datetime = models.DateTimeField()
    set_by = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True, blank=False, related_name='set_reminders')
    title = models.TextField()
    notes = models.TextField(null=True, blank=True)
    read_by = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True, blank=True, related_name='read_reminders')

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
