from bootstrap_modal_forms.forms import BSModalModelForm
from django.forms import DateTimeInput

from apps.office.models import Reminder


class ReminderCreateModalForm(BSModalModelForm):
    class Meta:
        model = Reminder
        fields = ("datetime", "title", "notes")
        widgets = {
            "datetime": DateTimeInput(format='%d.%m.%Y %H:%M:%S',
                                      attrs={'class': 'form-control datetimefield'}),
        }
