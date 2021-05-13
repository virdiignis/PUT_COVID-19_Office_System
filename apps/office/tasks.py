from celery import shared_task
from django.utils import timezone
from django.utils.timezone import localtime

from apps.office.models import Reminder, Worker
from django.utils.translation import gettext_lazy as _


@shared_task(name="office.shift_takeover")
def shift_takeover():
    now = localtime()
    takeover_deadline = now.replace(hour=now.hour + 1, minute=10, second=0)
    Reminder.objects.create(
        datetime=takeover_deadline,
        set_by=Worker.objects.get(id=1),
        title=_("Shift takeover"),
        notes=_(
            '''This is automatic reminder.
Accept it to indicate shift takeover.
There is one of us for each of you, to record who was on the shift when.'''
        )
    )
