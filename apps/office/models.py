from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Model
from phonenumber_field.modelfields import PhoneNumberField


class Worker(AbstractUser):

    phone_number = PhoneNumberField(null=True, blank=True, unique=True)


class Reminder(Model):
    date = models.DateTimeField()
    set_by = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True, blank=False)
    title = models.TextField()
    note = models.TextField(null=True, blank=True)
