from celery import shared_task
from django.utils import timezone
from django.utils.timezone import localtime

from apps.covid.models import Isolation
from apps.office.models import Reminder, Worker
from django.utils.translation import gettext_lazy as _


@shared_task(name='covid.isolations_over')
def isolations_over():
    if Isolation.objects.filter(end_date=timezone.now().date()).exists():
        for isolation in Isolation.objects.filter(end_date=timezone.now().date()):
            datetime = localtime(timezone.now()).replace(hour=16, minute=0, second=0)
            notes = _("Make sure to update their health state")
            if isolation.person.isolationroom is not None:
                place = _("in DS4 room {nr} ").format(nr=isolation.person.isolationroom.number)
                notes += _(" and isolation room info.")
            else:
                place = ""
                notes += "."

            Reminder.objects.create(
                datetime=datetime,
                set_by=Worker.objects.get(id=1),
                title=_("{person} ends their isolation {place}today.").format(person=isolation.person, place=place),
                notes=notes
            )