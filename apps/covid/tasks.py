from datetime import timedelta

from celery import shared_task
from django.utils import timezone
from django.utils.timezone import localtime

from apps.covid.models import Isolation, Person
from apps.office.models import Reminder, Worker
from django.utils.translation import gettext_lazy as _


@shared_task(name='covid.isolations_over')
def isolations_over():
    yesterday = timezone.now().date() - timedelta(days=1)
    if Isolation.objects.filter(end_date=yesterday).exists():
        for isolation in Isolation.objects.filter(end_date=yesterday):
            datetime = localtime(timezone.now()).replace(hour=16, minute=0, second=0)
            notes = _("Make sure to update their health state")
            try:
                room = isolation.person.isolationroom
                place = _("in DS4 room {nr} ").format(nr=room.number)
                notes += _(" and isolation room info.")
            except Person.isolationroom.RelatedObjectDoesNotExist:
                place = ""
                notes += "."

            Reminder.objects.create(
                datetime=datetime,
                set_by=Worker.objects.get(id=1),
                title=_("{person} ends their isolation {place}today.").format(person=isolation.person, place=place),
                notes=notes
            )
