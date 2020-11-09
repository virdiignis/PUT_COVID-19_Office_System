from dal import autocomplete
from django.forms import inlineformset_factory, ModelForm, DateTimeInput, DateInput, modelformset_factory, HiddenInput
from django import forms
from django.utils.translation import gettext_lazy as _

from apps.covid.models import Case, Action, Person, Isolation, IsolationRoom, Document, Unit
from bootstrap_modal_forms.forms import BSModalModelForm

from backend import settings


class ActionFormSet(inlineformset_factory(Case,
                                          Action,
                                          fields=(
                                                  "datetime", "made_by", "based_on", "contact_from", "contact_content",
                                                  "action_description", "notes"),
                                          extra=0,
                                          widgets={
                                              "datetime": DateTimeInput(format='%d.%m.%Y %H:%M:%S',
                                                                        attrs={'class': 'form-control datetimefield'}),
                                              "made_by": autocomplete.ModelSelect2(url='worker-autocomplete'),
                                              "contact_from": autocomplete.ModelSelect2(url='person-autocomplete'),
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


class DocumentFormSet(inlineformset_factory(Case,
                                            Document,
                                            exclude=("uploaded_by",),
                                            extra=1,
                                            can_delete=False
                                            )):
    def get_queryset(self):
        return super(DocumentFormSet, self).get_queryset().order_by("-upload_date")


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
            "made_by": autocomplete.ModelSelect2(url='worker-autocomplete'),
            "contact_from": autocomplete.ModelSelect2(url='person-autocomplete'),
        }


class ReportForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(format='%d.%m.%Y', attrs={'class': 'form-control datefield'}),
                                 label=_("Start date"))
    end_date = forms.DateField(widget=forms.DateInput(format='%d.%m.%Y', attrs={'class': 'form-control datefield'}),
                               label=_("End date"))


class UnitCreateModalForm(BSModalModelForm):
    class Meta:
        model = Unit
        fields = ("name", "report_students_email", "report_employees_email")
