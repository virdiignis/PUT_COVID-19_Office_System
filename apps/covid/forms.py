from dal import autocomplete
from django.forms import inlineformset_factory, ModelForm, DateTimeInput, DateInput
from apps.covid.models import Case, Action, Person, Isolation
from bootstrap_modal_forms.forms import BSModalModelForm


class ActionFormSet(inlineformset_factory(Case,
                                          Action,
                                          fields=(
                                                  "datetime", "made_by", "based_on", "contact_content",
                                                  "action_description",
                                                  "notes"),
                                          extra=0,
                                          widgets={
                                              "datetime": DateTimeInput(format='%Y-%m-%d %H:%M:%S',
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
                                             "start_date": DateInput(format='%Y-%m-%d',
                                                                     attrs={'class': 'form-control datefield'}),
                                             "end_date": DateInput(format='%Y-%m-%d',
                                                                   attrs={'class': 'form-control datefield'}),
                                             "ordered_on": DateInput(format='%Y-%m-%d',
                                                                     attrs={'class': 'form-control datefield'}),
                                             "person": autocomplete.ModelSelect2(url='person-autocomplete')
                                         })


class CaseCreateModalForm(BSModalModelForm):
    class Meta:
        model = Case
        fields = ("title",)


class PersonCreateModalForm(BSModalModelForm):
    class Meta:
        model = Person
        fields = "__all__"
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
