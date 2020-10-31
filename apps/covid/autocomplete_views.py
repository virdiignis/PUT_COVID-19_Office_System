from dal import autocomplete
from django.db.models import Q

from apps.covid.models import Person


class PersonAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Person.objects.none()

        qs = Person.objects.all()

        if self.q:
            qs = qs.filter(
                Q(first_name__istartswith=self.q) |
                Q(last_name__istartswith=self.q) |
                Q(email__istartswith=self.q)
            )

        return qs
