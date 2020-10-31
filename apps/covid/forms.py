from dal import autocomplete
from django.forms import inlineformset_factory, ModelForm, DateTimeInput
from apps.covid.models import Case, Action, Person
from bootstrap_modal_forms.forms import BSModalModelForm

ActionFormset = inlineformset_factory(Case,
                                      Action,
                                      fields=(
                                          "made_by", "datetime", "based_on", "contact_content", "action_description",
                                          "notes"),
                                      extra=1,
                                      widgets={
                                          "datetime": DateTimeInput(format='%Y-%m-%d %H:%M:%S',
                                                                    attrs={'class': 'form-control datetimefield'}),
                                          "made_by": autocomplete.ModelSelect2(url='worker-autocomplete',
                                                                               attrs={"style": "width:95%"})
                                      })


class CaseCreateModalForm(BSModalModelForm):
    class Meta:
        model = Case
        fields = ("title",)


class PersonCreateModalForm(BSModalModelForm):
    class Meta:
        model = Person
        fields = "__all__"


class CaseUpdateForm(ModelForm):
    class Meta:
        model = Case
        fields = "__all__"
        widgets = {
            "people": autocomplete.ModelSelect2Multiple(url='person-autocomplete', attrs={"style": "width:95%"})
        }
