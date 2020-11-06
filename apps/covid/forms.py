from dal import autocomplete
from django.forms import inlineformset_factory, ModelForm, DateTimeInput, DateInput, modelformset_factory, NumberInput, \
    HiddenInput
from rest_framework.fields import HiddenField

from apps.covid.models import Case, Action, Person, Isolation, IsolationRoom
from bootstrap_modal_forms.forms import BSModalModelForm


class ActionFormSet(inlineformset_factory(Case,
                                          Action,
                                          fields=(
                                                  "datetime", "made_by", "based_on", "contact_content",
                                                  "action_description",
                                                  "notes"),
                                          extra=0,
                                          widgets={
                                              "datetime": DateTimeInput(format='%d.%m.%Y %H:%M:%S',
                                                                        attrs={'class': 'form-control datetimefield'}),
                                              "made_by": autocomplete.ModelSelect2(url='worker-autocomplete')
                                          })):
    def get_queryset(self):
        return super(ActionFormSet, self).get_queryset().order_by("-datetime")


IsolationFormSet = inlineformset_factory(Case,
                                         Isolation,
                                         fields=(
                                             "person", "ordered_by", "ordered_on", "start_date", "end_date",
                                             "whereabouts", "cause"),
                                         extra=1,
                                         widgets={
                                             "start_date": DateInput(format='%d.%m.%Y',
                                                                     attrs={'class': 'form-control datefield'}),
                                             "end_date": DateInput(format='%d.%m.%Y',
                                                                   attrs={'class': 'form-control datefield'}),
                                             "ordered_on": DateInput(format='%d.%m.%Y',
                                                                     attrs={'class': 'form-control datefield'}),
                                             "person": autocomplete.ModelSelect2(url='person-autocomplete')
                                         })

IsolationRoomFormSet = modelformset_factory(IsolationRoom, fields="__all__", extra=0, can_delete=False,
                                            widgets={
                                                "resident": autocomplete.ModelSelect2(url='person-autocomplete'),
                                                "number": HiddenInput(
                                                    attrs={'class': 'disabled', 'readonly': 'readonly'})
                                            }
                                            )


class CaseCreateModalForm(BSModalModelForm):
    class Meta:
        model = Case
        fields = ("title",)


class PersonCreateUpdateModalForm(BSModalModelForm):
    class Meta:
        model = Person
        fields = ("title", "first_name", "middle_name", "last_name", "role", "email",
                  "phone_number", "dorm", "unit", "health_state")
        widgets = {
            "unit": autocomplete.ModelSelect2(url='unit-autocomplete')
        }


class CaseUpdateForm(ModelForm):
    class Meta:
        model = Case
        fields = "__all__"
        widgets = {
            "people": autocomplete.ModelSelect2Multiple(url='person-autocomplete', attrs={"style": "width:95%"})
        }


class ActionCreateModalForm(BSModalModelForm):
    class Meta:
        model = Action
        exclude = ("case",)
        widgets = {
            "datetime": DateTimeInput(format='%d.%m.%Y %H:%M:%S',
                                      attrs={'class': 'form-control datetimefield'}),
            "made_by": autocomplete.ModelSelect2(url='worker-autocomplete')
        }
